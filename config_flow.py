"""Config flow support for the HomeSeer integration."""

import asyncio
import logging
from libhomeseer import (
    HomeSeer,
    DEVICE_ZWAVE_SWITCH_MULTILEVEL,
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
    DEFAULT_HTTP_PORT,
    DEFAULT_ASCII_PORT,
)
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_ALLOW_EVENTS,
    CONF_ALLOWED_EVENT_GROUPS,
    CONF_ASCII_PORT,
    CONF_FORCED_COVERS,
    CONF_HTTP_PORT,
    CONF_NAME_TEMPLATE,
    CONF_NAMESPACE,
    DEFAULT_ALLOW_EVENTS,
    DEFAULT_NAME_TEMPLATE,
    DEFAULT_NAMESPACE,
    DOMAIN,
)

USER_STEP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD, default=DEFAULT_PASSWORD): cv.string,
        vol.Required(CONF_HTTP_PORT, default=DEFAULT_HTTP_PORT): cv.positive_int,
        vol.Required(CONF_ASCII_PORT, default=DEFAULT_ASCII_PORT): cv.positive_int,
    }
)

CONFIG_STEP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAMESPACE, default=DEFAULT_NAMESPACE): cv.string,
        vol.Required(CONF_NAME_TEMPLATE, default=DEFAULT_NAME_TEMPLATE): cv.string,
        vol.Required(CONF_ALLOW_EVENTS, default=DEFAULT_ALLOW_EVENTS): cv.boolean,
    }
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a HomeSeer config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self):
        self._host = None
        self._username = None
        self._password = None
        self._http_port = None
        self._ascii_port = None
        self._namespace = None
        self._name_template = None
        self._allow_events = None
        self._switch_multilevels = []
        self._event_groups = []
        self._forced_covers = []
        self._allowed_groups = []

    async def async_step_user(self, user_input=None):
        errors = {}
        if self._async_current_entries():
            # Config entry already exists, only one allowed.
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            homeseer = HomeSeer(
                user_input[CONF_HOST],
                async_get_clientsession(self.hass),
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                user_input[CONF_HTTP_PORT],
                user_input[CONF_ASCII_PORT],
            )

            try:
                await asyncio.wait_for(homeseer.initialize(), 5)
            except asyncio.TimeoutError:
                _LOGGER.error(f"Could not connect to HomeSeer at {user_input[CONF_HOST]}")

            if homeseer.devices or homeseer.events:
                self._host = user_input[CONF_HOST]
                self._username = user_input[CONF_USERNAME]
                self._password = user_input[CONF_PASSWORD]
                self._http_port = user_input[CONF_HTTP_PORT]
                self._ascii_port = user_input[CONF_ASCII_PORT]

                for device in homeseer.devices.values():
                    if device.device_type_string == DEVICE_ZWAVE_SWITCH_MULTILEVEL:
                        self._switch_multilevels.append(device.ref)
                for event in homeseer.events:
                    if event.group not in self._event_groups:
                        self._event_groups.append(event.group)
                return await self.async_step_config()
            errors["base"] = "initialize_failed"

        return self.async_show_form(
            step_id="user", data_schema=USER_STEP_SCHEMA, errors=errors
        )

    async def async_step_config(self, user_input=None):
        errors = {}
        if user_input is not None:
            self._namespace = user_input[CONF_NAMESPACE]
            self._allow_events = user_input[CONF_ALLOW_EVENTS]

            try:
                cv.template(str(user_input[CONF_NAME_TEMPLATE]))
                self._name_template = user_input[CONF_NAME_TEMPLATE]
                if len(self._switch_multilevels) > 0:
                    return await self.async_step_multilevels()
                if len(self._event_groups) > 0 and self._allow_events:
                    return await self.async_step_groups()
                return self.finalize_config_entry_flow()
            except (vol.Invalid, TemplateError):
                errors["base"] = "template_failed"

        return self.async_show_form(
            step_id="config", data_schema=CONFIG_STEP_SCHEMA, errors=errors
        )

    async def async_step_multilevels(self, user_input=None):

        if user_input is not None:
            if user_input.get(CONF_FORCED_COVERS) is not None:
                self._forced_covers = user_input[CONF_FORCED_COVERS]

            if len(self._event_groups) > 0 and self._allow_events:
                return await self.async_step_groups()
            return self.finalize_config_entry_flow()

        return self.async_show_form(
            step_id="multilevels",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_FORCED_COVERS): cv.multi_select(
                        self._switch_multilevels
                    )
                }
            ),
        )

    async def async_step_groups(self, user_input=None):

        if user_input is not None:
            if user_input.get(CONF_ALLOWED_EVENT_GROUPS) is not None:
                self._allowed_groups = user_input[CONF_ALLOWED_EVENT_GROUPS]

            return self.finalize_config_entry_flow()

        return self.async_show_form(
            step_id="groups",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_ALLOWED_EVENT_GROUPS): cv.multi_select(
                        self._event_groups
                    )
                }
            ),
        )

    def finalize_config_entry_flow(self):
        return self.async_create_entry(
            title=self._host,
            data={
                CONF_HOST: self._host,
                CONF_USERNAME: self._username,
                CONF_PASSWORD: self._password,
                CONF_HTTP_PORT: self._http_port,
                CONF_ASCII_PORT: self._ascii_port,
                CONF_NAMESPACE: self._namespace,
                CONF_NAME_TEMPLATE: self._name_template,
                CONF_ALLOW_EVENTS: self._allow_events,
                CONF_FORCED_COVERS: self._forced_covers,
                CONF_ALLOWED_EVENT_GROUPS: self._allowed_groups,
            },
        )
