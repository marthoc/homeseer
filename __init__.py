"""
Custom integration for interacting with a HomeSeer software installation.
For more details please refer to the documentation at https://github.com/marthoc/homeseer
"""

import asyncio
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
)

from homeassistant.helpers import template

from .const import (
    ATTR_REF,
    ATTR_VALUE,
    CONF_ALLOWED_EVENT_GROUPS,
    CONF_ALLOWED_INTERFACES,
    CONF_ALLOW_EVENTS,
    CONF_ASCII_PORT,
    CONF_FORCED_COVERS,
    CONF_HTTP_PORT,
    CONF_NAME_TEMPLATE,
    CONF_NAMESPACE,
    DOMAIN,
    HOMESEER_PLATFORMS,
)
from .homeseer import HomeSeerBridge

_LOGGER = logging.getLogger(__name__)

SERVICE_CONTROL_DEVICE_BY_VALUE = "control_device_by_value"

SERVICE_CONTROL_DEVICE_BY_VALUE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_REF): cv.positive_int,
        vol.Required(ATTR_VALUE): cv.positive_int,
    }
)


async def async_setup(hass, config):
    """HomeSeer is configured via config entry."""
    return True


async def async_setup_entry(hass, config_entry):
    """Set up a HomeSeer config entry."""
    config = config_entry.data

    host = config[CONF_HOST]
    namespace = config[CONF_NAMESPACE]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    http_port = config[CONF_HTTP_PORT]
    ascii_port = config[CONF_ASCII_PORT]
    name_template = template.Template(str(config[CONF_NAME_TEMPLATE]))
    allow_events = config[CONF_ALLOW_EVENTS]
    allowed_event_groups = config[CONF_ALLOWED_EVENT_GROUPS]
    forced_covers = config[CONF_FORCED_COVERS]
    allowed_interfaces = config[CONF_ALLOWED_INTERFACES]

    name_template.hass = hass

    bridge = HomeSeerBridge(
        hass,
        host,
        username,
        password,
        http_port,
        ascii_port,
        namespace,
        name_template,
        allowed_event_groups,
        forced_covers,
        allowed_interfaces,
    )

    try:
        if not await asyncio.wait_for(bridge.setup(), 60):
            _LOGGER.error(
                f"No supported HomeSeer devices or events found, aborting entry setup for {host}."
            )
    except asyncio.TimeoutError:
        _LOGGER.error(f"Could not connect to HomeSeer at {host}, aborting entry setup.")
        return False

    await bridge.start()
    attempts = 0
    while not bridge.api.available:
        if attempts < 5:
            attempts += 1
            await asyncio.sleep(5)
            continue
        _LOGGER.error(
            f"Failed to connect to HomeSeer ASCII connection at {host}:{ascii_port}, aborting entry setup."
        )
        await bridge.stop()
        return False

    if not allow_events:
        HOMESEER_PLATFORMS.remove("scene")

    hass.data[DOMAIN] = bridge

    for platform in HOMESEER_PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
        )

    hass.bus.async_listen_once("homeassistant_stop", bridge.stop)

    async def control_device_by_value(call):
        ref = call.data[ATTR_REF]
        value = call.data[ATTR_VALUE]

        await bridge.api.control_device_by_value(ref, value)

    hass.services.async_register(
        DOMAIN,
        SERVICE_CONTROL_DEVICE_BY_VALUE,
        control_device_by_value,
        schema=SERVICE_CONTROL_DEVICE_BY_VALUE_SCHEMA,
    )

    return True


async def async_unload_entry(hass, config_entry):
    """Unload the config entry and platforms."""
    bridge = hass.data.pop(DOMAIN)
    await bridge.stop()

    tasks = []
    for platform in HOMESEER_PLATFORMS:
        tasks.append(
            hass.config_entries.async_forward_entry_unload(config_entry, platform)
        )

    return all(await asyncio.gather(*tasks))
