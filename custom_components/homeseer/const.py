"""Constants for the HomeSeer integration."""

DOMAIN = "homeseer"

ATTR_REF = "ref"
ATTR_LOCATION = "location"
ATTR_LOCATION2 = "location2"
ATTR_NAME = "name"
ATTR_VALUE = "value"
ATTR_STATUS = "status"
ATTR_DEVICE_TYPE_STRING = "device_type_string"
ATTR_LAST_CHANGE = "last_change"

CONF_HTTP_PORT = "http_port"
CONF_ASCII_PORT = "ascii_port"
CONF_ALLOW_EVENTS = "allow_events"
CONF_NAMESPACE = "namespace"
CONF_NAME_TEMPLATE = "name_template"
CONF_ALLOWED_EVENT_GROUPS = "allowed_event_groups"
CONF_FORCED_COVERS = "forced_covers"
CONF_ALLOWED_INTERFACES = "allowed_interfaces"

DEFAULT_NAME_TEMPLATE = "{{ device.location2 }} {{ device.location }} {{ device.name }}"
DEFAULT_NAMESPACE = "homeseer"
DEFAULT_ALLOW_EVENTS = True
DEFAULT_ALLOWED_EVENT_GROUPS = []
DEFAULT_FORCED_COVERS = []
DEFAULT_INTERFACE_NAME = "HomeSeer"

HOMESEER_PLATFORMS = [
    "binary_sensor",
    "cover",
    "light",
    "lock",
    "scene",
    "sensor",
    "switch",
]
