"""Support for HomeSeer lock-type devices."""

import logging
from libhomeseer import DEVICE_ZWAVE_DOOR_LOCK

from homeassistant.components.lock import LockEntity

from .const import DOMAIN
from .homeseer import HomeSeerEntity

_LOGGER = logging.getLogger(__name__)

LOCK_TYPES = [DEVICE_ZWAVE_DOOR_LOCK]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up HomeSeer lock-type devices."""
    lock_entities = []
    homeseer = hass.data[DOMAIN]

    for device in homeseer.devices:
        if device.device_type_string in LOCK_TYPES:
            entity = HomeSeerLock(device, homeseer)
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
