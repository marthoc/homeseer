"""
Constants for the HomeSeer component.
"""

import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "homeseer"

CONF_HTTP_PORT = 'http_port'
CONF_ASCII_PORT = 'ascii_port'
CONF_LOCATION_NAMES = 'location_names'
CONF_ALLOW_EVENTS = 'allow_events'

DEFAULT_HTTP_PORT = 80
DEFAULT_PASSWORD = 'default'
DEFAULT_USERNAME = 'default'
DEFAULT_ASCII_PORT = 11000
DEFAULT_LOCATION_NAMES = False
DEFAULT_ALLOW_EVENTS = True

HOMESEER_PLATFORMS = ['binary_sensor', 'cover', 'light', 'lock', 'scene', 'sensor', 'switch']
