"""
Support for HomeSeer sensor-type devices.
"""

from pyhs3 import (
    DEVICE_ZWAVE_BATTERY,
    DEVICE_ZWAVE_FAN_STATE,
    DEVICE_ZWAVE_LUMINANCE,
    DEVICE_ZWAVE_OPERATING_STATE,
    DEVICE_ZWAVE_RELATIVE_HUMIDITY,
    DEVICE_ZWAVE_SENSOR_MULTILEVEL,
    HASS_SENSORS,
    STATE_LISTENING,
    HS_UNIT_CELSIUS,
    HS_UNIT_FAHRENHEIT,
    HS_UNIT_LUX,
    HS_UNIT_PERCENTAGE,
    parse_uom
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

from homeassistant.helpers.entity import Entity

from .const import _LOGGER, DOMAIN

DEPENDENCIES = ["homeseer"]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up HomeSeer sensor-type devices."""
    sensor_devices = []
    homeseer = hass.data[DOMAIN]

    for device in homeseer.devices:
        if device.device_type_string in HASS_SENSORS:
            dev = get_sensor_device(device, homeseer)
            sensor_devices.append(dev)
            _LOGGER.info(f"Added HomeSeer sensor-type device: {dev.name}")

    async_add_entities(sensor_devices)


class HSSensor(Entity):
    """Base representation of a HomeSeer sensor-type device."""

    def __init__(self, device, connection):
        self._device = device
        self._connection = connection
        self._uom = None

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
        return self._connection.name_template.async_render(device=self._device).strip()

    @property
    def state(self):
        """Return the state of the device."""
        return self._device.value

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    async def async_added_to_hass(self):
        """Register value update callback and cache unit of measure."""
        self._device.register_update_callback(self.async_schedule_update_ha_state)
        self._uom = await parse_uom(self._device)


class HSBattery(HSSensor):
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


class HSHumidity(HSSensor):
    """Representation of a HomeSeer humidity sensor device."""

    @property
    def unit_of_measurement(self):
        return PERCENTAGE

    @property
    def device_class(self):
        return DEVICE_CLASS_HUMIDITY


class HSLuminance(HSSensor):
    """Representation of a HomeSeer light level sensor device."""

    @property
    def unit_of_measurement(self):
        return PERCENTAGE

    @property
    def device_class(self):
        return DEVICE_CLASS_ILLUMINANCE


class HSFanState(HSSensor):
    """Representation of a HomeSeer HVAC fan state sensor device."""

    @property
    def icon(self):
        if self.state == 0:
            return "mdi:fan-off"
        return "mdi:fan"

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


class HSOperatingState(HSSensor):
    """Representation of a HomeSeer HVAC operating state sensor device."""

    @property
    def icon(self):
        if self.state == "Idle":
            return "mdi:fan-off"
        elif self.state == "Heating":
            return "mdi:flame"
        elif self.state == "Cooling":
            return "mdi:snowflake"
        return "mdi:fan"

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


class HSSensorMultilevel(HSSensor):
    """Representation of a HomeSeer multi-level sensor."""

    @property
    def device_class(self):
        if self._uom == HS_UNIT_LUX:
            return DEVICE_CLASS_ILLUMINANCE
        if self._uom == HS_UNIT_CELSIUS:
            return DEVICE_CLASS_TEMPERATURE
        if self._uom == HS_UNIT_FAHRENHEIT:
            return DEVICE_CLASS_TEMPERATURE
        return None

    @property
    def unit_of_measurement(self):
        if self._uom == HS_UNIT_LUX:
            return LIGHT_LUX
        if self._uom == HS_UNIT_CELSIUS:
            return TEMP_CELSIUS
        if self._uom == HS_UNIT_FAHRENHEIT:
            return TEMP_FAHRENHEIT
        if self._uom == HS_UNIT_PERCENTAGE:
            return PERCENTAGE
        return None


def get_sensor_device(device, homeseer):
    """Return the proper sensor object based on device type."""
    if device.device_type_string == DEVICE_ZWAVE_BATTERY:
        return HSBattery(device, homeseer)
    elif device.device_type_string == DEVICE_ZWAVE_RELATIVE_HUMIDITY:
        return HSHumidity(device, homeseer)
    elif device.device_type_string == DEVICE_ZWAVE_LUMINANCE:
        return HSLuminance(device, homeseer)
    elif device.device_type_string == DEVICE_ZWAVE_FAN_STATE:
        return HSFanState(device, homeseer)
    elif device.device_type_string == DEVICE_ZWAVE_OPERATING_STATE:
        return HSOperatingState(device, homeseer)
    elif device.device_type_string == DEVICE_ZWAVE_SENSOR_MULTILEVEL:
        return HSSensorMultilevel(device, homeseer)
    return HSSensor(device, homeseer)
