"""
Support for HomeSeer lock-type devices.
"""

from pyhs3 import HASS_LOCKS, STATE_LISTENING

from homeassistant.components.lock import LockDevice

from .const import _LOGGER, DOMAIN

DEPENDENCIES = ["homeseer"]


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up HomeSeer lock-type devices."""
    lock_devices = []
    homeseer = hass.data[DOMAIN]

    for device in homeseer.devices:
        if device.device_type_string in HASS_LOCKS:
            dev = HSLock(device, homeseer)
            lock_devices.append(dev)
            _LOGGER.info(f"Added HomeSeer lock-type device: {dev.name}")

    async_add_entities(lock_devices)


class HSLock(LockDevice):
    """Representation of a HomeSeer lock device."""

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
    def name(self):
        """Return the name of the device."""
        if self._connection.location_names:
            return (
                f"{self._device.location2} {self._device.location} {self._device.name}"
            )
        return self._device.name

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def is_locked(self):
        """Return true if device is locked."""
        return self._device.is_locked

    async def async_lock(self, **kwargs):
        await self._device.lock()

    async def async_unlock(self, **kwargs):
        await self._device.unlock()

    async def async_added_to_hass(self):
        """Register value update callback."""
        self._device.register_update_callback(self.async_schedule_update_ha_state)
