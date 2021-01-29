"""
Constants for the HomeSeer component.
"""

import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "homeseer"

UNIT_PERCENTAGE = "%"

CONF_HTTP_PORT = "http_port"
CONF_ASCII_PORT = "ascii_port"
CONF_ALLOW_EVENTS = "allow_events"
CONF_NAMESPACE = "namespace"
CONF_NAME_TEMPLATE = "name_template"
CONF_ALLOWED_EVENT_GROUPS = "allowed_event_groups"
CONF_FORCED_COVERS = "forced_covers"

DEFAULT_HTTP_PORT = 80
DEFAULT_PASSWORD = "default"
DEFAULT_USERNAME = "default"
DEFAULT_ASCII_PORT = 11000
DEFAULT_NAME_TEMPLATE = "{{ device.location2 }} {{ device.location }} {{ device.name }}"
DEFAULT_ALLOW_EVENTS = True
DEFAULT_ALLOWED_EVENT_GROUPS = []
DEFAULT_FORCED_COVERS = []

HOMESEER_PLATFORMS = [
    "binary_sensor",
    "cover",
    "light",
    "lock",
    "scene",
    "sensor",
    "switch",
]
