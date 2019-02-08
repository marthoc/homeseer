"""
Component for interacting with a HomeSeer HomeTroller or HS3 software installation.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/homeseer/
"""
import asyncio
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_EVENT, CONF_HOST, CONF_ID, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import EventOrigin
from homeassistant.helpers import aiohttp_client, discovery

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['pyhs3==0.9']

DOMAIN = 'homeseer'

CONF_HTTP_PORT = 'http_port'
CONF_ASCII_PORT = 'ascii_port'
CONF_LOCATION_NAMES = 'location_names'

DEFAULT_HTTP_PORT = 80
DEFAULT_PASSWORD = 'default'
DEFAULT_USERNAME = 'default'
DEFAULT_ASCII_PORT = 11000
DEFAULT_LOCATION_NAMES = False

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PASSWORD, default=DEFAULT_PASSWORD): cv.string,
        vol.Optional(CONF_USERNAME, default=DEFAULT_USERNAME): cv.string,
        vol.Optional(CONF_HTTP_PORT, default=DEFAULT_HTTP_PORT): cv.port,
        vol.Optional(CONF_ASCII_PORT, default=DEFAULT_ASCII_PORT): cv.port,
        vol.Optional(CONF_LOCATION_NAMES, default=DEFAULT_LOCATION_NAMES): cv.boolean
    })
}, extra=vol.ALLOW_EXTRA)

HOMESEER_COMPONENTS = ['binary_sensor', 'cover', 'light', 'lock', 'scene', 'sensor', 'switch']


async def async_setup(hass, config):
    """Set up the HomeSeer component."""
    from pyhs3 import STATE_LISTENING

    config = config.get(DOMAIN)
    host = config[CONF_HOST]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    http_port = config[CONF_HTTP_PORT]
    ascii_port = config[CONF_ASCII_PORT]
    location_names = config[CONF_LOCATION_NAMES]

    homeseer = HSConnection(hass, host, username, password, http_port, ascii_port, location_names)

    await homeseer.api.initialize()
    if len(homeseer.devices) == 0 and len(homeseer.events) == 0:
        _LOGGER.error('No supported HomeSeer devices found, aborting component setup.')
        return False

    await homeseer.start()
    i = 0
    while homeseer.api.state != STATE_LISTENING:
        if i < 3:
            i += 1
            await asyncio.sleep(1)
        elif i == 3:
            _LOGGER.error('Failed to connect to HomeSeer ASCII server, aborting component setup.')
            await homeseer.stop()
            return False
    _LOGGER.info('Connected to HomeSeer ASCII server at {}:{}'.format(host, ascii_port))

    homeseer.add_remotes()

    for component in HOMESEER_COMPONENTS:
        hass.async_create_task(discovery.async_load_platform(
            hass, component, DOMAIN, {}, config))

    hass.data[DOMAIN] = homeseer

    hass.bus.async_listen_once('homeassistant_stop', homeseer.stop)

    return True


class HSConnection:
    """Manages a connection between HomeSeer and Home Assistant."""
    def __init__(self, hass, host, username, password, http_port, ascii_port, location_names):
        from pyhs3 import HomeTroller
        self._hass = hass
        self._session = aiohttp_client.async_get_clientsession(self._hass)
        self.api = HomeTroller(host, self._session, username=username, password=password,
                               http_port=http_port, ascii_port=ascii_port)
        self._location_names = location_names
        self.remotes = []

    @property
    def devices(self):
        return self.api.devices.values()

    @property
    def events(self):
        return self.api.events

    @property
    def location_names(self):
        return self._location_names

    async def start(self):
        await self.api.start_listener()

    async def stop(self, *args):
        await self.api.stop_listener()

    def add_remotes(self):
        from pyhs3 import HASS_EVENTS
        for device in self.devices:
            if device.device_type_string in HASS_EVENTS:
                self.remotes.append(HSRemote(self._hass, device))
                _LOGGER.info('Added HomeSeer remote-type device: {} (Ref: {})'.format(device.name, device.ref))


class HSRemote:
    """Link remote-type devices that should fire events rather than create entities to Home Assistant."""
    def __init__(self, hass, device):
        self._hass = hass
        self._device = device
        self._device.register_update_callback(self.update_callback, suppress_on_reconnect=True)
        self._event = 'homeseer_{}'.format(CONF_EVENT)

    def update_callback(self):
        """Fire the event."""
        data = {CONF_ID: self._device.ref, CONF_EVENT: self._device.value}
        self._hass.bus.async_fire(self._event, data, EventOrigin.remote)
