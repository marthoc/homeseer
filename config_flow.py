import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
)

from .const import (
    CONF_ALLOW_EVENTS,
    CONF_ALLOWED_EVENT_GROUPS,
    CONF_ASCII_PORT,
    CONF_FORCED_COVERS,
    CONF_HTTP_PORT,
    CONF_NAME_TEMPLATE,
    CONF_NAMESPACE,
    DEFAULT_ALLOW_EVENTS,
    DEFAULT_ALLOWED_EVENT_GROUPS,
    DEFAULT_ASCII_PORT,
    DEFAULT_FORCED_COVERS,
    DEFAULT_HTTP_PORT,
    DEFAULT_NAME_TEMPLATE,
    DEFAULT_NAMESPACE,
    DEFAULT_PASSWORD,
    DEFAULT_USERNAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

ENTRY_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_NAMESPACE, default=DEFAULT_NAMESPACE): str,
        vol.Required(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
        vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
        vol.Required(CONF_HTTP_PORT, default=DEFAULT_HTTP_PORT): int,
        vol.Required(CONF_ASCII_PORT, default=DEFAULT_ASCII_PORT): int,
        vol.Required(CONF_NAME_TEMPLATE, default=DEFAULT_NAME_TEMPLATE): str,
        vol.Required(CONF_ALLOW_EVENTS, default=DEFAULT_ALLOW_EVENTS): bool,
        vol.Optional(CONF_ALLOWED_EVENT_GROUPS): str,
        vol.Optional(CONF_FORCED_COVERS): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a HomeSeer config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        errors = {}
        if self._async_current_entries():
            # Config entry already exists, only one allowed.
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:

            return self.async_create_entry(
                title=user_input[CONF_HOST],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user", data_schema=ENTRY_SCHEMA, errors=errors
        )
