"""
Support for HomeSeer quirks.
Some devices should be represented as a Home Assistant platform other than what the HS API data suggests.
These devices can be "forced" into other platforms by adding their "device_type_string" to the dict below.
"""

from libhomeseer import (
    DEVICE_ZWAVE_BARRIER_OPERATOR,
    DEVICE_ZWAVE_CENTRAL_SCENE,
    DEVICE_ZWAVE_SENSOR_BINARY,
)

HOMESEER_QUIRKS = {
    DEVICE_ZWAVE_BARRIER_OPERATOR: "cover",
    DEVICE_ZWAVE_CENTRAL_SCENE: "remote",
    DEVICE_ZWAVE_SENSOR_BINARY: "binary_sensor",
}
