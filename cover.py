"""
Support for HomeSeer cover-type devices.
"""

from pyhs3 import (
    STATE_LISTENING,
    DEVICE_ZWAVE_BARRIER_OPERATOR,
    DEVICE_ZWAVE_SWITCH_MULTILEVEL,
)

from homeassistant.components.cover import (
    CoverEntity,
    ATTR_POSITION,
    DEVICE_CLASS_BLIND,
    DEVICE_CLASS_GARAGE,
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    SUPPORT_SET_POSITION,
)
from homeassistant.const import STATE_CLOSED, STATE_CLOSING, STATE_OPENING

from .const import _LOGGER, DOMAIN

DEPENDENCIES = ["homeseer"]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up HomeSeer cover-type devices."""
    cover_devices = []
    homeseer = hass.data[DOMAIN]

    for device in homeseer.devices:
        if device.device_type_string == DEVICE_ZWAVE_BARRIER_OPERATOR:
            """Device is a garage-door opener."""
            dev = HSGarage(device, homeseer)
            cover_devices.append(dev)
            _LOGGER.info(f"Added HomeSeer garage-type device: {dev.name}")
        elif device.device_type_string == DEVICE_ZWAVE_SWITCH_MULTILEVEL and int(device.ref) in homeseer.forced_covers:
            """Device is a blind."""
            dev = HSBlind(device, homeseer)
            cover_devices.append(dev)
            _LOGGER.info(f"Added HomeSeer blind-type device: {dev.name}")

    async_add_entities(cover_devices)


class HSCover(CoverEntity):
    """Base representation of a HomeSeer cover-type device."""

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

    async def async_added_to_hass(self):
        """Register value update callback."""
        self._device.register_update_callback(self.async_schedule_update_ha_state)


class HSGarage(HSCover):
    """Representation of a garage door opener device."""

    @property
    def supported_features(self):
        """Return the features supported by the device."""
        features = SUPPORT_OPEN | SUPPORT_CLOSE
        return features

    @property
    def device_class(self):
        """Return the device class for the device."""
        return DEVICE_CLASS_GARAGE

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


class HSBlind(HSCover):
    """Representation of a window-covering device."""

    @property
    def supported_features(self):
        """Return the features supported by the device."""
        return SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_SET_POSITION

    @property
    def device_class(self):
        """Return the device class for the device."""
        return DEVICE_CLASS_BLIND

    @property
    def current_cover_position(self):
        """Return the current position of the cover."""
        return int(self._device.dim_percent * 100)

    @property
    def is_closed(self):
        """Return if the cover is closed or not."""
        return not self._device.is_on

    async def async_open_cover(self, **kwargs):
        await self._device.on()

    async def async_close_cover(self, **kwargs):
        await self._device.off()

    async def async_set_cover_position(self, **kwargs):
        await self._device.dim(kwargs.get(ATTR_POSITION, 0))
