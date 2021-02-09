"""Support for HomeSeer switch-type devices."""
import logging
from libhomeseer import DEVICE_ZWAVE_SWITCH, DEVICE_ZWAVE_SWITCH_BINARY

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN
from .homeseer import HomeSeerEntity

_LOGGER = logging.getLogger(__name__)

SWITCH_TYPES = [DEVICE_ZWAVE_SWITCH, DEVICE_ZWAVE_SWITCH_BINARY]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up HomeSeer switch-type devices."""
    switch_entities = []
    homeseer = hass.data[DOMAIN]

    for device in homeseer.devices:
        if device.device_type_string in SWITCH_TYPES:
            entity = HomeSeerSwitch(device, homeseer)
            switch_entities.append(entity)
            _LOGGER.info(
                f"Added HomeSeer switch-type device: {entity.name} ({entity.device_state_attributes})"
            )

    if switch_entities:
        async_add_entities(switch_entities)


class HomeSeerSwitch(HomeSeerEntity, SwitchEntity):
    """Representation of a HomeSeer switch-type device."""

    def __init__(self, device, connection):
        HomeSeerEntity.__init__(self, device, connection)

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._device.is_on

    async def async_turn_on(self, **kwargs):
        await self._device.on()

    async def async_turn_off(self, **kwargs):
        await self._device.off()
