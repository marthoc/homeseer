"""Config flow support for the HomeSeer integration."""

import asyncio
import logging
from libhomeseer import (
    HomeSeer,
    HomeSeerSwitchableDevice,
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
    CONF_ALLOWED_INTERFACES,
    CONF_ASCII_PORT,
    CONF_FORCED_COVERS,
    CONF_HTTP_PORT,
    CONF_NAME_TEMPLATE,
    CONF_NAMESPACE,
    DEFAULT_ALLOW_EVENTS,
    DEFAULT_NAME_TEMPLATE,
    DEFAULT_NAMESPACE,
    DEFAULT_INTERFACE_NAME,
    DOMAIN,
)
from .homeseer_quirks import HOMESEER_QUIRKS

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
        self._all_devices = []
        self._all_events = []
        self._interfaces = []
        self._switches = []
        self._event_groups = []
        self._allowed_interfaces = []
        self._group_flag = True
        self._allowed_groups = []
        self._cover_flag = True
        self._forced_covers = []

    async def async_step_user(self, user_input=None):
        """Basic data for the HomeSeer instance is provided by the user."""
        errors = {}
        if self._async_current_entries():
            # Config entry already exists, only one allowed for now.
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            bridge = HomeSeer(
                user_input[CONF_HOST],
                async_get_clientsession(self.hass),
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                user_input[CONF_HTTP_PORT],
                user_input[CONF_ASCII_PORT],
            )

            try:
                await asyncio.wait_for(bridge.initialize(), 20)
            except asyncio.TimeoutError:
                _LOGGER.error(
                    f"Could not connect to HomeSeer at {user_input[CONF_HOST]}"
                )

            if bridge.devices or bridge.events:
                self._host = user_input[CONF_HOST]
                self._username = user_input[CONF_USERNAME]
                self._password = user_input[CONF_PASSWORD]
                self._http_port = user_input[CONF_HTTP_PORT]
                self._ascii_port = user_input[CONF_ASCII_PORT]

                for device in bridge.devices.values():
                    self._all_devices.append(device)
                for event in bridge.events:
                    self._all_events.append(event)

                return await self.async_step_config()
            errors["base"] = "initialize_failed"

        return self.async_show_form(
            step_id="user", data_schema=USER_STEP_SCHEMA, errors=errors
        )

    async def async_step_config(self, user_input=None):
        """Initial configuration options are provided by the user."""
        errors = {}
        if user_input is not None:
            self._namespace = user_input[CONF_NAMESPACE]
            self._allow_events = user_input[CONF_ALLOW_EVENTS]

            try:
                cv.template(str(user_input[CONF_NAME_TEMPLATE]))
                self._name_template = user_input[CONF_NAME_TEMPLATE]
                return await self.async_step_interfaces()

            except (vol.Invalid, TemplateError):
                errors["base"] = "template_failed"

        return self.async_show_form(
            step_id="config", data_schema=CONFIG_STEP_SCHEMA, errors=errors
        )

    async def async_step_interfaces(self, user_input=None):
        """Allowed HomeSeer device interfaces are selected by the user."""
        if user_input is not None:
            self._allowed_interfaces = user_input[CONF_ALLOWED_INTERFACES]
            return await self.handle_next_step()

        for device in self._all_devices:
            iname = (
                device.interface_name
                if device.interface_name is not None
                else DEFAULT_INTERFACE_NAME
            )
            if iname not in self._interfaces:
                self._interfaces.append(iname)

        self._interfaces.sort()

        return self.async_show_form(
            step_id="interfaces",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ALLOWED_INTERFACES, default=self._interfaces
                    ): cv.multi_select(self._interfaces),
                }
            ),
        )

    async def async_step_groups(self, user_input=None):
        """Allowed HomeSeer event groups are selected by the user."""
        if user_input is not None:
            if user_input.get(CONF_ALLOWED_EVENT_GROUPS) is not None:
                self._allowed_groups = user_input[CONF_ALLOWED_EVENT_GROUPS]

            return await self.handle_next_step()

        for event in self._all_events:
            if event.group not in self._event_groups:
                self._event_groups.append(event.group)

        self._event_groups.sort()

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

    async def async_step_covers(self, user_input=None):
        """Devices to force as covers are selected by the user."""
        if user_input is not None:
            if user_input.get(CONF_FORCED_COVERS) is not None:
                self._forced_covers = user_input[CONF_FORCED_COVERS]

            return await self.handle_next_step()

        default_covers = []

        for device in self._all_devices:
            iname = (
                device.interface_name
                if device.interface_name is not None
                else "HomeSeer"
            )
            if iname in self._allowed_interfaces and isinstance(
                device, HomeSeerSwitchableDevice
            ):
                self._switches.append(device.ref)
                try:
                    if HOMESEER_QUIRKS[device.device_type_string] == "cover":
                        default_covers.append(device.ref)
                except KeyError:
                    pass

        self._switches.sort()

        return self.async_show_form(
            step_id="covers",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_FORCED_COVERS, default=default_covers
                    ): cv.multi_select(self._switches)
                }
            ),
        )

    async def handle_next_step(self):
        """Determine which step to show to the user next based on available data."""
        if self._group_flag and self._allow_events:
            self._group_flag = False
            return await self.async_step_groups()
        elif self._cover_flag:
            self._cover_flag = False
            return await self.async_step_covers()
        return self.finalize_config_entry_flow()

    def finalize_config_entry_flow(self):
        return self.async_create_entry(
            title=f"{self._host}:{self._http_port}",
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
                CONF_ALLOWED_INTERFACES: self._allowed_interfaces,
            },
        )
