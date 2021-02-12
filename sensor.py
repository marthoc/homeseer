"""Support for HomeSeer sensor-type devices."""

import logging
from libhomeseer import (
    DEVICE_ZWAVE_BATTERY,
    DEVICE_ZWAVE_FAN_STATE,
    DEVICE_ZWAVE_LUMINANCE,
    DEVICE_ZWAVE_OPERATING_STATE,
    DEVICE_ZWAVE_RELATIVE_HUMIDITY,
    DEVICE_ZWAVE_SENSOR_MULTILEVEL,
    HS_UNIT_CELSIUS,
    HS_UNIT_FAHRENHEIT,
    HS_UNIT_LUX,
    HS_UNIT_PERCENTAGE,
    get_uom_from_status,
)

from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_TEMPERATURE,
    LIGHT_LUX,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    PERCENTAGE,
)

from .const import DOMAIN
from .homeseer import HomeSeerEntity

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = [
    DEVICE_ZWAVE_BATTERY,
    DEVICE_ZWAVE_FAN_STATE,
    DEVICE_ZWAVE_LUMINANCE,
    DEVICE_ZWAVE_OPERATING_STATE,
    DEVICE_ZWAVE_RELATIVE_HUMIDITY,
    DEVICE_ZWAVE_SENSOR_MULTILEVEL,
]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up HomeSeer sensor-type devices."""
    sensor_entities = []
    homeseer = hass.data[DOMAIN]

    for device in homeseer.devices:
        if device.device_type_string in SENSOR_TYPES:
            entity = get_sensor_entity(device, homeseer)
            sensor_entities.append(entity)
            _LOGGER.info(
                f"Added HomeSeer sensor-type device: {entity.name} ({entity.device_state_attributes}"
            )

    if sensor_entities:
        async_add_entities(sensor_entities)


class HomeSeerSensor(HomeSeerEntity):
    """Base representation of a HomeSeer sensor-type device."""

    @property
    def state(self):
        return self._device.value


class HomeSeerBattery(HomeSeerSensor):
    """Representation of a HomeSeer device that reports battery level."""

    @property
    def unit_of_measurement(self):
        return PERCENTAGE

    @property
    def icon(self):
        if self.state == 100:
            return "mdi:battery"
        elif self.state > 89:
            return "mdi:battery-90"
        elif self.state > 79:
            return "mdi:battery-80"
        elif self.state > 69:
            return "mdi:battery-70"
        elif self.state > 59:
            return "mdi:battery-60"
        elif self.state > 49:
            return "mdi:battery-50"
        elif self.state > 39:
            return "mdi:battery-40"
        elif self.state > 29:
            return "mdi:battery-30"
        elif self.state > 19:
            return "mdi:battery-20"
        elif self.state > 9:
            return "mdi:battery-10"
        return None

    @property
    def device_class(self):
        return DEVICE_CLASS_BATTERY


class HomeSeerHumidity(HomeSeerSensor):
    """Representation of a HomeSeer humidity sensor device."""

    @property
    def unit_of_measurement(self):
        return PERCENTAGE

    @property
    def device_class(self):
        return DEVICE_CLASS_HUMIDITY


class HomeSeerLuminance(HomeSeerSensor):
    """Representation of a HomeSeer light level sensor device."""

    @property
    def unit_of_measurement(self):
        return PERCENTAGE

    @property
    def device_class(self):
        return DEVICE_CLASS_ILLUMINANCE


class HomeSeerFanState(HomeSeerSensor):
    """Representation of a HomeSeer HVAC fan state sensor device."""

    @property
    def state(self):
        """Return the state of the device."""
        if self._device.value == 0:
            return "Off"
        elif self._device.value == 1:
            return "On"
        elif self._device.value == 2:
            return "On High"
        elif self._device.value == 3:
            return "On Medium"
        elif self._device.value == 4:
            return "On Circulation"
        elif self._device.value == 5:
            return "On Humidity Circulation"
        elif self._device.value == 6:
            return "On Right-Left Circulation"
        elif self._device.value == 7:
            return "On Up-Down Circulation"
        elif self._device.value == 8:
            return "On Quiet Circulation"
        return None

    @property
    def icon(self):
        if self.state == 0:
            return "mdi:fan-off"
        return "mdi:fan"


class HomeSeerOperatingState(HomeSeerSensor):
    """Representation of a HomeSeer HVAC operating state sensor device."""

    @property
    def state(self):
        """Return the state of the device."""
        if self._device.value == 0:
            return "Idle"
        elif self._device.value == 1:
            return "Heating"
        elif self._device.value == 2:
            return "Cooling"
        elif self._device.value == 3:
            return "Fan Only"
        elif self._device.value == 4:
            return "Pending Heat"
        elif self._device.value == 5:
            return "Pending Cool"
        elif self._device.value == 6:
            return "Vent-Economizer"
        return None

    @property
    def icon(self):
        if self.state == "Idle":
            return "mdi:fan-off"
        elif self.state == "Heating":
            return "mdi:flame"
        elif self.state == "Cooling":
            return "mdi:snowflake"
        return "mdi:fan"


class HomeSeerSensorMultilevel(HomeSeerSensor):
    """Representation of a HomeSeer multi-level sensor."""

    @property
    def device_class(self):
        if self.unit_of_measurement == HS_UNIT_LUX:
            return DEVICE_CLASS_ILLUMINANCE
        if (
            self.unit_of_measurement == HS_UNIT_CELSIUS
            or self.unit_of_measurement == HS_UNIT_FAHRENHEIT
        ):
            return DEVICE_CLASS_TEMPERATURE
        return None

    @property
    def unit_of_measurement(self):
        uom = get_uom_from_status(self._device.status)
        if uom == HS_UNIT_LUX:
            return LIGHT_LUX
        if uom == HS_UNIT_CELSIUS:
            return TEMP_CELSIUS
        if uom == HS_UNIT_FAHRENHEIT:
            return TEMP_FAHRENHEIT
        if uom == HS_UNIT_PERCENTAGE:
            return PERCENTAGE
        return None


def get_sensor_entity(device, connection):
    """Return the proper sensor object based on device type."""
    if device.device_type_string == DEVICE_ZWAVE_BATTERY:
        return HomeSeerBattery(device, connection)
    elif device.device_type_string == DEVICE_ZWAVE_RELATIVE_HUMIDITY:
        return HomeSeerHumidity(device, connection)
    elif device.device_type_string == DEVICE_ZWAVE_LUMINANCE:
        return HomeSeerLuminance(device, connection)
    elif device.device_type_string == DEVICE_ZWAVE_FAN_STATE:
        return HomeSeerFanState(device, connection)
    elif device.device_type_string == DEVICE_ZWAVE_OPERATING_STATE:
        return HomeSeerOperatingState(device, connection)
    elif device.device_type_string == DEVICE_ZWAVE_SENSOR_MULTILEVEL:
        return HomeSeerSensorMultilevel(device, connection)
    return HomeSeerSensor(device, connection)
