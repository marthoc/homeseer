"""
Constants for the HomeSeer component.
"""

import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "homeseer"

ATTR_REF = "ref"
ATTR_VALUE = "value"

CONF_HTTP_PORT = "http_port"
CONF_ASCII_PORT = "ascii_port"
CONF_ALLOW_EVENTS = "allow_events"
CONF_NAMESPACE = "namespace"
CONF_NAME_TEMPLATE = "name_template"

DEFAULT_HTTP_PORT = 80
DEFAULT_PASSWORD = "default"
DEFAULT_USERNAME = "default"
DEFAULT_ASCII_PORT = 11000
DEFAULT_NAME_TEMPLATE = "{{ device.location2 }} {{ device.location }} {{ device.name }}"
DEFAULT_ALLOW_EVENTS = True

HOMESEER_PLATFORMS = [
    "binary_sensor",
    "cover",
    "light",
    "lock",
    "scene",
    "sensor",
    "switch",
]
