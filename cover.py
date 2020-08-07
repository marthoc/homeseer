"""
Support for HomeSeer cover-type devices.
"""

from pyhs3 import HASS_COVERS, STATE_LISTENING

from homeassistant.components.cover import CoverEntity
from homeassistant.const import STATE_CLOSED, STATE_CLOSING, STATE_OPENING

from .const import _LOGGER, DOMAIN

DEPENDENCIES = ["homeseer"]


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up HomeSeer cover-type devices."""
    cover_devices = []
    homeseer = hass.data[DOMAIN]

    for device in homeseer.devices:
        if device.device_type_string in HASS_COVERS:
            dev = HSCover(device, homeseer)
            cover_devices.append(dev)
            _LOGGER.info(f"Added HomeSeer cover-type device: {dev.name}")

    async_add_entities(cover_devices)


class HSCover(CoverEntity):
    """Representation of a HomeSeer cover-type device."""

    def __init__(self, device, connection):
        self._device = device
        self._connection = connection

    @property
    def available(self):
        """Return whether the device is available."""
        return self._connection.api.state == STATE_LISTENING

    @property
    def device_state_attributes(self):
        attr = {
            "Device Ref": self._device.ref,
            "Location": self._device.location,
            "Location 2": self._device.location2,
        }
        return attr

    @property
    def unique_id(self):
        """Return a unique ID for the device."""
        return f"{self._connection.namespace}-{self._device.ref}"

    @property
    def name(self):
        """Return the name of the device."""
        return self._connection.name_template.async_render(device=self._device).strip()

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
