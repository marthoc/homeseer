"""Support for HomeSeer binary-sensor-type devices."""

import logging
from libhomeseer import DEVICE_ZWAVE_SENSOR_BINARY

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import DOMAIN
from .homeseer import HomeSeerEntity

_LOGGER = logging.getLogger(__name__)

BINARY_SENSOR_TYPES = [DEVICE_ZWAVE_SENSOR_BINARY]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up HomeSeer binary-sensor-type devices."""
    binary_sensor_entities = []
    homeseer = hass.data[DOMAIN]

    for device in homeseer.devices:
        if device.device_type_string in BINARY_SENSOR_TYPES:
            entity = HomeSeerBinarySensor(device, homeseer)
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
