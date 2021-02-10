"""
Custom integration for interacting with a HomeSeer software installation.
For more details please refer to the documentation at https://github.com/marthoc/homeseer
"""
import asyncio
import logging

import voluptuous as vol
from libhomeseer import HomeSeer, DEVICE_ZWAVE_CENTRAL_SCENE

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_EVENT,
    CONF_HOST,
    CONF_ID,
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.core import EventOrigin
from homeassistant.helpers import aiohttp_client, template

from .const import (
    ATTR_REF,
    ATTR_VALUE,
    CONF_ALLOWED_EVENT_GROUPS,
    CONF_ALLOW_EVENTS,
    CONF_ASCII_PORT,
    CONF_FORCED_COVERS,
    CONF_HTTP_PORT,
    CONF_NAME_TEMPLATE,
    CONF_NAMESPACE,
    DOMAIN,
    HOMESEER_PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)

SERVICE_CONTROL_DEVICE_BY_VALUE = "control_device_by_value"

SERVICE_CONTROL_DEVICE_BY_VALUE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_REF): cv.positive_int,
        vol.Required(ATTR_VALUE): cv.positive_int,
    }
)


async def async_setup(hass, config):
    """HomeSeer is configured via config entry."""
    return True


async def async_setup_entry(hass, config_entry):
    """Set up a HomeSeer config entry."""
    config = config_entry.data

    host = config[CONF_HOST]
    namespace = config[CONF_NAMESPACE]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    http_port = config[CONF_HTTP_PORT]
    ascii_port = config[CONF_ASCII_PORT]
    name_template = template.Template(str(config[CONF_NAME_TEMPLATE]))
    allow_events = config[CONF_ALLOW_EVENTS]
    allowed_event_groups = config[CONF_ALLOWED_EVENT_GROUPS]
    forced_covers = config[CONF_FORCED_COVERS]

    name_template.hass = hass

    homeseer = HomeSeerConnection(
        hass,
        host,
        username,
        password,
        http_port,
        ascii_port,
        namespace,
        name_template,
        allowed_event_groups,
        forced_covers,
    )

    await homeseer.api.initialize()

    if not homeseer.devices and not homeseer.events:
        _LOGGER.error(
            f"No supported HomeSeer devices or events found, aborting entry setup for {host}."
        )
        return False

    await homeseer.api.start_listener()
    attempts = 0
    while not homeseer.api.available:
        if attempts < 5:
            attempts += 1
            await asyncio.sleep(1)
            continue
        _LOGGER.error(
            f"Failed to connect to HomeSeer ASCII connection at {host}:{ascii_port}, aborting entry setup."
        )
        await homeseer.api.stop_listener()
        return False

    homeseer.add_remotes()

    if not allow_events and len(allowed_event_groups) == 0:
        HOMESEER_PLATFORMS.remove("scene")

    hass.bus.async_listen_once("homeassistant_stop", homeseer.api.stop_listener)

    async def control_device_by_value(call):
        ref = call.data[ATTR_REF]
        value = call.data[ATTR_VALUE]

        await homeseer.api.control_device_by_value(ref, value)

    hass.services.async_register(
        DOMAIN,
        SERVICE_CONTROL_DEVICE_BY_VALUE,
        control_device_by_value,
        schema=SERVICE_CONTROL_DEVICE_BY_VALUE_SCHEMA,
    )

    hass.data[DOMAIN] = homeseer

    tasks = []
    for platform in HOMESEER_PLATFORMS:
        tasks.append(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
        )

    return all(await asyncio.gather(*tasks))


class HomeSeerConnection:
    """Manages a connection between HomeSeer and Home Assistant."""

    def __init__(
        self,
        hass,
        host,
        username,
        password,
        http_port,
        ascii_port,
        namespace,
        name_template,
        allowed_event_groups,
        forced_covers,
    ):
        self._hass = hass
        self._session = aiohttp_client.async_get_clientsession(self._hass)
        self.api = HomeSeer(
            host,
            self._session,
            username=username,
            password=password,
            http_port=http_port,
            ascii_port=ascii_port,
        )
        self._namespace = namespace
        self._name_template = name_template
        self._allowed_event_groups = allowed_event_groups
        self._forced_covers = forced_covers
        self.remotes = []

    @property
    def devices(self):
        return self.api.devices.values()

    @property
    def events(self):
        return self.api.events

    @property
    def namespace(self):
        return self._namespace

    @property
    def name_template(self):
        return self._name_template

    @property
    def allowed_event_groups(self):
        return self._allowed_event_groups

    @property
    def forced_covers(self):
        return self._forced_covers

    async def start(self):
        """Start listening to HomeSeer for device updates."""
        await self.api.start_listener()

    async def stop(self, *args):
        """Stop listening to HomeSeer for device updates."""
        await self.api.stop_listener()

    def add_remotes(self):
        for device in self.devices:
            if device.device_type_string == DEVICE_ZWAVE_CENTRAL_SCENE:
                self.remotes.append(HomeSeerRemote(self._hass, device))
                _LOGGER.info(
                    f"Added HomeSeer remote-type device: {device.name} (Ref: {device.ref})"
                )


class HomeSeerRemote:
    """Link remote-type devices that should fire events rather than create entities to Home Assistant."""

    def __init__(self, hass, device):
        self._hass = hass
        self._device = device
        self._device.register_update_callback(
            self.update_callback, suppress_on_connection=True
        )
        self._event = f"homeseer_{CONF_EVENT}"

    def update_callback(self):
        """Fire the event."""
        data = {CONF_ID: self._device.ref, CONF_EVENT: self._device.value}
        self._hass.bus.async_fire(self._event, data, EventOrigin.remote)


async def async_unload_entry(hass, config_entry):
    """Unload the config entry and platforms."""
    homeseer = hass.data.pop(DOMAIN)
    await homeseer.stop()

    tasks = []
    for platform in HOMESEER_PLATFORMS:
        tasks.append(
            hass.config_entries.async_forward_entry_unload(config_entry, platform)
        )

    return all(await asyncio.gather(*tasks))
