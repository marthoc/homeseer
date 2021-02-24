"""Support for HomeSeer lock-type devices."""

import logging

from homeassistant.components.lock import LockEntity

from .const import DOMAIN
from .homeseer import HomeSeerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up HomeSeer lock-type devices."""
    lock_entities = []
    bridge = hass.data[DOMAIN]

    for device in bridge.devices["lock"]:
        entity = HomeSeerLock(device, bridge)
        lock_entities.append(entity)
        _LOGGER.info(
            f"Added HomeSeer lock-type device: {entity.name} ({entity.device_state_attributes})"
        )

    if lock_entities:
        async_add_entities(lock_entities)


class HomeSeerLock(HomeSeerEntity, LockEntity):
    """Representation of a HomeSeer lock device."""

    @property
    def is_locked(self):
        """Return true if device is locked."""
        return self._device.is_locked

    async def async_lock(self, **kwargs):
        await self._device.lock()

    async def async_unlock(self, **kwargs):
        await self._device.unlock()
