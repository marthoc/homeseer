"""Support for HomeSeer light-type devices."""
import logging
from libhomeseer import DEVICE_ZWAVE_SWITCH_MULTILEVEL

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS,
    LightEntity,
)

from .const import DOMAIN
from .homeseer import HomeSeerEntity

_LOGGER = logging.getLogger(__name__)

LIGHT_TYPES = [DEVICE_ZWAVE_SWITCH_MULTILEVEL]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up HomeSeer light-type devices."""
    light_entities = []
    homeseer = hass.data[DOMAIN]

    for device in homeseer.devices:
        if (
            device.device_type_string in LIGHT_TYPES
            and device.ref not in homeseer.forced_covers
        ):
            entity = HSLight(device, homeseer)
            light_entities.append(entity)
            _LOGGER.info(
                f"Added HomeSeer light-type device: {entity.name} ({entity.device_state_attributes})"
            )

    if light_entities:
        async_add_entities(light_entities)


class HSLight(HomeSeerEntity, LightEntity):
    """Representation of a HomeSeer light-type device."""

    def __init__(self, device, connection):
        HomeSeerEntity.__init__(self, device, connection)

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
