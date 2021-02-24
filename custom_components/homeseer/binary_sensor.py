"""Support for HomeSeer binary-sensor-type devices."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import DOMAIN
from .homeseer import HomeSeerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up HomeSeer binary-sensor-type devices."""
    binary_sensor_entities = []
    bridge = hass.data[DOMAIN]

    for device in bridge.devices["binary_sensor"]:
        entity = HomeSeerBinarySensor(device, bridge)
        binary_sensor_entities.append(entity)
        _LOGGER.info(
            f"Added HomeSeer binary-sensor-type device: {entity.name} ({entity.device_state_attributes})"
        )

    if binary_sensor_entities:
        async_add_entities(binary_sensor_entities)


class HomeSeerBinarySensor(HomeSeerEntity, BinarySensorEntity):
    """Representation of a HomeSeer binary-sensor-type device."""

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._device.value > 0
