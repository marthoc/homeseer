"""
Constants for the HomeSeer component.
"""

import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "homeseer"

CONF_HTTP_PORT = 'http_port'
CONF_ASCII_PORT = 'ascii_port'
CONF_ALLOW_EVENTS = 'allow_events'
CONF_NAMESPACE = 'namespace'

DEFAULT_HTTP_PORT = 80
DEFAULT_PASSWORD = 'default'
DEFAULT_USERNAME = 'default'
DEFAULT_ASCII_PORT = 11000
DEFAULT_ALLOW_EVENTS = True

HOMESEER_PLATFORMS = ['binary_sensor', 'cover', 'light', 'lock', 'scene', 'sensor', 'switch']
