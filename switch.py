"""
Support for HomeSeer switch-type devices.
"""
import logging

from homeassistant.components.switch import SwitchDevice
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['homeseer']


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up HomeSeer switch-type devices."""
    from pyhs3 import HASS_SWITCHES

    switch_devices = []
    homeseer = hass.data[DOMAIN]

    for device in homeseer.devices:
        if device.device_type_string in HASS_SWITCHES:
            dev = HSSwitch(device, homeseer)
            switch_devices.append(dev)
            _LOGGER.info('Added HomeSeer switch device: {}'.format(dev.name))

    async_add_entities(switch_devices)


class HSSwitch(SwitchDevice):
    """Representation of a HomeSeer switch-type device."""
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
            'Device Ref': self._device.ref,
            'Location': self._device.location,
            'Location2': self._device.location2
        }
        return attr

    @property
    def name(self):
        """Return the name of the device."""
        if self._connection.location2_names and self._connection.location_names:
            return '{} {} {}'.format(self._device.location2, self._device.location, self._device.name)
        elif self._connection.location2_names:
            return '{} {}'.format(self._device.location2, self._device.name)
        elif self._connection.location_names:
            return '{} {}'.format(self._device.location, self._device.name)
        else:
            return self._device.name

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def is_on(self):
        """Return true if device is locked."""
        return self._device.is_on

    async def async_turn_on(self, **kwargs):
        await self._device.on()

    async def async_turn_off(self, **kwargs):
        await self._device.off()

    async def async_added_to_hass(self):
        """Register value update callback."""
        self._device.register_update_callback(self.async_schedule_update_ha_state)
