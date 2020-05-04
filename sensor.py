"""
Support for HomeSeer sensor-type devices.
"""
import logging

from homeassistant.const import (DEVICE_CLASS_BATTERY, DEVICE_CLASS_TEMPERATURE, DEVICE_CLASS_HUMIDITY,
                                 DEVICE_CLASS_ILLUMINANCE)
from homeassistant.helpers.entity import Entity
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['homeseer']


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up HomeSeer sensor-type devices."""
    from pyhs3 import (HASS_SENSORS, DEVICE_ZWAVE_BATTERY, DEVICE_ZWAVE_TEMPERATURE,
                       DEVICE_ZWAVE_RELATIVE_HUMIDITY, DEVICE_ZWAVE_LUMINANCE,
                       DEVICE_ZWAVE_FAN_STATE, DEVICE_ZWAVE_OPERATING_STATE)

    sensor_devices = []
    homeseer = hass.data[DOMAIN]
    units = hass.config.units.name

    for device in homeseer.devices:
        if device.device_type_string in HASS_SENSORS:
            if device.device_type_string == DEVICE_ZWAVE_BATTERY:
                dev = HSBattery(device, homeseer)
            elif device.device_type_string == DEVICE_ZWAVE_TEMPERATURE:
                dev = HSTemperature(device, homeseer, units)
            elif device.device_type_string == DEVICE_ZWAVE_RELATIVE_HUMIDITY:
                dev = HSHumidity(device, homeseer)
            elif device.device_type_string == DEVICE_ZWAVE_LUMINANCE:
                dev = HSLuminance(device, homeseer)
            elif device.device_type_string == DEVICE_ZWAVE_FAN_STATE:
                dev = HSFanState(device, homeseer)
            elif device.device_type_string == DEVICE_ZWAVE_OPERATING_STATE:
                dev = HSOperatingState(device, homeseer)
            else:
                dev = HSSensor(device, homeseer)
            sensor_devices.append(dev)
            _LOGGER.info('Added HomeSeer sensor-type device: {}'.format(dev.name))

    async_add_entities(sensor_devices)


class HSSensor(Entity):
    """Representation of a HomeSeer sensor-type device."""
    def __init__(self, device, connection, units=None):
        self._device = device
        self._connection = connection
        self._units = units

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
        if self._connection.location_names:
            return '{} {} {}'.format(self._device.location2, self._device.location, self._device.name)
        else:
            return self._device.name

    @property
    def state(self):
        """Return the state of the device."""
        return self._device.value

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    async def async_added_to_hass(self):
        """Register value update callback."""
        self._device.register_update_callback(self.async_schedule_update_ha_state)


class HSBattery(HSSensor):
    """Representation of a HomeSeer battery sensor device."""
    @property
    def unit_of_measurement(self):
        return '%'

    @property
    def icon(self):
        if self.state == 100:
            return 'mdi:battery'
        elif self.state > 89:
            return 'mdi:battery-90'
        elif self.state > 79:
            return 'mdi:battery-80'
        elif self.state > 69:
            return 'mdi:battery-70'
        elif self.state > 59:
            return 'mdi:battery-60'
        elif self.state > 49:
            return 'mdi:battery-50'
        elif self.state > 39:
            return 'mdi:battery-40'
        elif self.state > 29:
            return 'mdi:battery-30'
        elif self.state > 19:
            return 'mdi:battery-20'
        elif self.state > 9:
            return 'mdi:battery-10'

    @property
    def device_class(self):
        return DEVICE_CLASS_BATTERY


class HSTemperature(HSSensor):
    """Representation of a HomeSeer temperature sensor device."""

    @property
    def unit_of_measurement(self):
        if self._units is not None:
            if str(self._units) == 'imperial':
                return "°F"
            elif str(self._units) == 'metric':
                return "°C"
            else:
                return "?"
        else:
            return '?'

    @property
    def icon(self):
        if self._units is not None:
            if str(self._units) == 'imperial':
                if self.state < 50:
                    return 'mdi:thermomter-low'
                elif self.state > 90:
                    return 'mdi:thermometer-high'
                else:
                    return 'mdi:thermometer'
            elif str(self._units) == 'metric':
                if self.state < 10:
                    return 'mdi:thermomter-low'
                elif self.state > 33:
                    return 'mdi:thermometer-high'
                else:
                    return 'mdi:thermometer'
            else:
                return 'mdi:thermometer'
        else:
            return 'mdi: thermometer'

    @property
    def device_class(self):
        return DEVICE_CLASS_TEMPERATURE


class HSHumidity(HSSensor):
    """Representation of a HomeSeer humidity sensor device."""

    @property
    def unit_of_measurement(self):
        return '%'

    @property
    def device_class(self):
        return DEVICE_CLASS_HUMIDITY


class HSLuminance(HSSensor):
    """Representation of a HomeSeer light level sensor device."""

    @property
    def unit_of_measurement(self):
        return '%'

    @property
    def device_class(self):
        return DEVICE_CLASS_ILLUMINANCE


class HSFanState(HSSensor):
    """Representation of a HomeSeer HVAC fan state sensor device."""

    @property
    def icon(self):
        if self.state == 0:
            return 'mdi:fan-off'
        else:
            return 'mdi:fan'


class HSOperatingState(HSSensor):
    """Representation of a HomeSeer HVAC operating state sensor device."""

    @property
    def icon(self):
        if self.state == 0:         # Idle
            return 'mdi:fan-off'
        elif self.state == 1:       # Heating
            return 'mdi:flame'
        elif self.state == 2:       # Cooling
            return 'mdi:snowflake'
        else:                       # Fan Only
            return 'mdi:fan'
