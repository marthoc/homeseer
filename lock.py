"""
Support for HomeSeer lock-type devices.
"""
import logging

from homeassistant.components.lock import LockDevice
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['homeseer']


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up HomeSeer lock-type devices."""
    from pyhs3 import HASS_LOCKS

    lock_devices = []
    homeseer = hass.data[DOMAIN]

    for device in homeseer.devices:
        if device.device_type_string in HASS_LOCKS:
            dev = HSLock(device, homeseer)
            lock_devices.append(dev)
            _LOGGER.info('Added HomeSeer lock device: {}'.format(dev.name))

    async_add_entities(lock_devices)


class HSLock(LockDevice):
    """Representation of a HomeSeer lock device."""
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
            'Device Ref': self._device.ref
        }
        return attr

    @property
    def name(self):
        """Return the name of the device."""
        return self._connection.name_template.render(device = self._device)

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
