"""
Support for HomeSeer cover-type devices.
"""
import logging

from homeassistant.components.cover import CoverDevice
from homeassistant.const import STATE_CLOSED, STATE_CLOSING, STATE_OPENING
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['homeseer']


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up HomeSeer cover-type devices."""
    from pyhs3 import HASS_COVERS

    cover_devices = []
    homeseer = hass.data[DOMAIN]

    for device in homeseer.devices:
        if device.device_type_string in HASS_COVERS:
            dev = HSCover(device, homeseer)
            cover_devices.append(dev)
            _LOGGER.info('Added HomeSeer cover device: {}'.format(dev.name))

    async_add_entities(cover_devices)


class HSCover(CoverDevice):
    """Representation of a HomeSeer cover device."""
    def __init__(self, device, connection):
        self._device = device
        self._connection = connection

    @property
    def available(self):
        """Return whether the device is available."""
        from pyhs3 import STATE_LISTENING
        return self._connection.api.state == STATE_LISTENING

    @property
    def device_state_attributes(self):
        attr = {
            'Device Ref': self._device.ref,
            'Location': self._device.location,
            'Location2': self._device.location2
        }
        return attr

    @property
    def name(self):
        """Return the name of the device."""
        if self._connection.location_names:
            return '{} {} {}'.format(self._device.location2, self._device.location, self._device.name)
        else:
            return self._device.name

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def is_opening(self):
        """Return if the cover is opening or not."""
        return self._device.current_state == STATE_OPENING

    @property
    def is_closing(self):
        """Return if the cover is closing or not."""
        return self._device.current_state == STATE_CLOSING

    @property
    def is_closed(self):
        """Return if the cover is closed or not."""
        return self._device.current_state == STATE_CLOSED

    async def async_open_cover(self, **kwargs):
        await self._device.open()

    async def async_close_cover(self, **kwargs):
        await self._device.close()

    async def async_added_to_hass(self):
        """Register value update callback."""
        self._device.register_update_callback(self.async_schedule_update_ha_state)
