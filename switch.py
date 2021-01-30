"""
Support for HomeSeer switch-type devices.
"""

from pyhs3 import HASS_SWITCHES, STATE_LISTENING

from homeassistant.components.switch import SwitchEntity

from .const import _LOGGER, DOMAIN

DEPENDENCIES = ["homeseer"]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up HomeSeer switch-type devices."""
    switch_devices = []
    homeseer = hass.data[DOMAIN]

    for device in homeseer.devices:
        if device.device_type_string in HASS_SWITCHES:
            dev = HSSwitch(device, homeseer)
            switch_devices.append(dev)
            _LOGGER.info(f"Added HomeSeer switch-type device: {dev.name}")

    async_add_entities(switch_devices)


class HSSwitch(SwitchEntity):
    """Representation of a HomeSeer switch-type device."""

    def __init__(self, device, connection):
        self._device = device
        self._connection = connection
        self._rendered_name = None

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
        return self._connection.name_template.async_render(device=self._device)

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._device.is_on

    async def async_turn_on(self, **kwargs):
        await self._device.on()

    async def async_turn_off(self, **kwargs):
        await self._device.off()

    async def async_added_to_hass(self):
        """Register value update callback."""
        self._device.register_update_callback(self.async_schedule_update_ha_state)
