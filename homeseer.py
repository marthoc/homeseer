"""Provides the base representation for all HomeSeer entities."""
from libhomeseer import (
    HomeSeerBasicDevice,
    HomeSeerSwitchableDevice,
    HomeSeerLockableDevice,
    HomeSeerDimmableDevice,
    get_datetime_from_last_change,
)
from typing import Union

from homeassistant.helpers.entity import Entity

from . import HomeSeerConnection
from .const import (
    ATTR_REF,
    ATTR_LOCATION,
    ATTR_LOCATION2,
    ATTR_VALUE,
    ATTR_STATUS,
    ATTR_DEVICE_TYPE_STRING,
    ATTR_LAST_CHANGE,
)


class HomeSeerEntity(Entity):
    """Base representation for all HomeSeer entities."""

    def __init__(
        self,
        device: Union[
            HomeSeerBasicDevice,
            HomeSeerSwitchableDevice,
            HomeSeerDimmableDevice,
            HomeSeerLockableDevice,
        ],
        connection: HomeSeerConnection,
    ):
        self._device = device
        self._connection = connection

    @property
    def available(self) -> bool:
        """Return True if the HomeSeer connection is listening."""
        return self._connection.api.available

    @property
    def device_state_attributes(self) -> dict:
        """Return a dictionary of state attributes."""
        attr = {
            ATTR_REF: self._device.ref,
            ATTR_LOCATION2: self._device.location2,
            ATTR_LOCATION: self._device.location,
            ATTR_DEVICE_TYPE_STRING: self._device.device_type_string,
            ATTR_VALUE: self._device.value,
            ATTR_STATUS: self._device.status,
            ATTR_LAST_CHANGE: get_datetime_from_last_change(self._device.last_change)
            .astimezone(self.hass.config.time_zone)
            .isoformat("T", "seconds"),
        }
        return attr

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the device."""
        return f"{self._connection.namespace}-{self._device.ref}"

    @property
    def name(self) -> str:
        """Return the name of the device rendered from the user-supplied template."""
        return self._connection.name_template.async_render(device=self._device)

    @property
    def should_poll(self) -> bool:
        """No polling necessary for HomeSeer."""
        return False

    async def async_added_to_hass(self) -> None:
        """Register update callback."""
        self._device.register_update_callback(self.async_schedule_update_ha_state)
