"""Support for HomeSeer switch-type devices."""

import logging

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN
from .homeseer import HomeSeerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up HomeSeer switch-type devices."""
    switch_entities = []
    bridge = hass.data[DOMAIN]

    for device in bridge.devices["switch"]:
        entity = HomeSeerSwitch(device, bridge)
        switch_entities.append(entity)
        _LOGGER.info(
            f"Added HomeSeer switch-type device: {entity.name} ({entity.device_state_attributes})"
        )

    if switch_entities:
        async_add_entities(switch_entities)


class HomeSeerSwitch(HomeSeerEntity, SwitchEntity):
    """Representation of a HomeSeer switch-type device."""

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._device.is_on

    async def async_turn_on(self, **kwargs):
        await self._device.on()

    async def async_turn_off(self, **kwargs):
        await self._device.off()
