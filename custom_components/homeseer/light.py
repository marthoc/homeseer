"""Support for HomeSeer light-type devices."""

import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS,
    LightEntity,
)

from .const import DOMAIN
from .homeseer import HomeSeerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up HomeSeer light-type devices."""
    light_entities = []
    bridge = hass.data[DOMAIN]

    for device in bridge.devices["light"]:
        entity = HomeSeerLight(device, bridge)
        light_entities.append(entity)
        _LOGGER.info(
            f"Added HomeSeer light-type device: {entity.name} ({entity.device_state_attributes})"
        )

    if light_entities:
        async_add_entities(light_entities)


class HomeSeerLight(HomeSeerEntity, LightEntity):
    """Representation of a HomeSeer light-type device."""

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS

    @property
    def brightness(self):
        """Return the brightness of the light."""
        bri = self._device.dim_percent * 255
        if bri > 255:
            return 255
        return bri

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._device.is_on

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        percent = int(brightness / 255 * 100)
        await self._device.dim(percent)

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        await self._device.off()
