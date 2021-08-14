"""Provides HomeSeer specific implementations for bridges, entities, and remotes."""

from libhomeseer import (
    HomeSeer,
    HomeSeerStatusDevice,
    HomeSeerSwitchableDevice,
    HomeSeerLockableDevice,
    HomeSeerDimmableDevice,
    get_datetime_from_last_change,
    RELATIONSHIP_CHILD,
    RELATIONSHIP_ROOT,
)
import logging
from typing import Optional, Union

from homeassistant.const import CONF_EVENT, CONF_ID
from homeassistant.core import EventOrigin, HomeAssistant
from homeassistant.helpers import aiohttp_client, template
from homeassistant.helpers.entity import Entity

from .const import (
    ATTR_REF,
    ATTR_LOCATION,
    ATTR_LOCATION2,
    ATTR_NAME,
    ATTR_VALUE,
    ATTR_STATUS,
    ATTR_DEVICE_TYPE_STRING,
    ATTR_LAST_CHANGE,
    DEFAULT_INTERFACE_NAME,
    DOMAIN,
)
from .homeseer_quirks import HOMESEER_QUIRKS

_LOGGER = logging.getLogger(__name__)

DEVICES_MODEL = {
    "binary_sensor": [],
    "cover": [],
    "light": [],
    "lock": [],
    "remote": [],
    "sensor": [],
    "scene": [],
    "switch": [],
}


class HomeSeerBridge:
    """Manages a single connection between HomeSeer and Home Assistant."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        username: str,
        password: str,
        http_port: int,
        ascii_port: int,
        namespace: str,
        name_template: template,
        allowed_event_groups: list,
        forced_covers: list,
        allowed_interfaces: list,
    ):
        self._hass = hass
        self._session = aiohttp_client.async_get_clientsession(self._hass)
        self.api = HomeSeer(
            host,
            self._session,
            username=username,
            password=password,
            http_port=http_port,
            ascii_port=ascii_port,
        )
        self._namespace = namespace
        self._name_template = name_template
        self._allowed_event_groups = allowed_event_groups
        self._forced_covers = forced_covers
        self._allowed_interfaces = allowed_interfaces
        self._devices = DEVICES_MODEL
        self.remotes = []

    @property
    def devices(self) -> dict:
        return self._devices

    @property
    def namespace(self) -> str:
        return self._namespace

    @property
    def name_template(self) -> template.Template:
        return self._name_template

    @property
    def allowed_event_groups(self) -> list:
        return self._allowed_event_groups

    @property
    def forced_covers(self) -> list:
        return self._forced_covers

    @property
    def allowed_interfaces(self) -> list:
        return self._allowed_interfaces

    async def setup(self) -> bool:
        """Initialize the HomeSeer API and sort devices."""
        await self.api.initialize()
        if not self.api.devices and not self.api.events:
            return False

        for device in self.api.devices.values():
            platform = self._get_ha_platform_for_homeseer_device(device)
            if platform is not None:
                self._devices[platform].append(device)

        for event in self.api.events:
            if (
                self.allowed_event_groups
                and event.group not in self.allowed_event_groups
            ):
                continue
            self._devices["scene"].append(event)

        for device in self.devices["remote"]:
            self.remotes.append(HomeSeerRemote(self._hass, device))
            _LOGGER.info(
                f"Added HomeSeer remote-type device: "
                f"{device.location2} {device.location} {device.name } ({device.ref})"
            )

        return True

    async def start(self) -> None:
        """Start listening to HomeSeer for device updates."""
        await self.api.start_listener()

    async def stop(self, *args) -> None:
        """Stop listening to HomeSeer for device updates."""
        await self.api.stop_listener()

    def _get_ha_platform_for_homeseer_device(
        self,
        device: Union[
            HomeSeerStatusDevice,
            HomeSeerSwitchableDevice,
            HomeSeerDimmableDevice,
            HomeSeerLockableDevice,
        ],
    ) -> Optional[str]:
        """
        Return the correct platform for the given device.
        This method ensures that a HomeSeer device will only ever be represented in one platform,
        and filters out devices as required.
        """
        # Filter out devices from interfaces not selected during the Config Flow.
        iname = (
            device.interface_name
            if device.interface_name is not None
            else DEFAULT_INTERFACE_NAME
        )
        if iname not in self.allowed_interfaces:
            _LOGGER.debug(
                f"Device ref {device.ref} is from disabled interface {iname}, "
                f"not creating an entity for this device"
            )
            return None

        # Force certain devices selected during the Config Flow to be covers.
        if device.ref in self.forced_covers:
            _LOGGER.debug(
                f"Device ref {device.ref} is forced as a cover, "
                f"creating a cover entity for this device"
            )
            return "cover"

        # Some devices should be represented as a Home Assistant platform other than what the HS API data suggests
        # These devices can be "forced" into other platforms by adding their "device_type_string" to the
        # homeseer_quirks.py file.
        try:
            return HOMESEER_QUIRKS[device.device_type_string]
        except KeyError:
            _LOGGER.debug(
                f"No platform quirk found for device type string "
                f"{device.device_type_string}, "
                f"automatically assigning a platform for device ref {device.ref}"
            )

        # Return the platform for the device based on the libhomeseer device type
        if type(device) == HomeSeerSwitchableDevice:
            return "switch"
        elif type(device) == HomeSeerDimmableDevice:
            return "light"
        elif type(device) == HomeSeerLockableDevice:
            return "lock"
        elif type(device) == HomeSeerStatusDevice:
            return "sensor"

        _LOGGER.debug(
            f"No valid platform detected for device ref {device.ref} (type: {type(device)})"
        )
        return None


class HomeSeerEntity(Entity):
    """Base representation for all HomeSeer entities."""

    def __init__(
        self,
        device: Union[
            HomeSeerStatusDevice,
            HomeSeerSwitchableDevice,
            HomeSeerDimmableDevice,
            HomeSeerLockableDevice,
        ],
        bridge: HomeSeerBridge,
    ):
        self._device = device
        self._bridge = bridge

    @property
    def available(self) -> bool:
        """Return True if the HomeSeer connection is listening."""
        return self._bridge.api.available

    @property
    def device_state_attributes(self) -> dict:
        """Return a dictionary of state attributes."""
        dt = get_datetime_from_last_change(self._device.last_change)
        attr = {
            ATTR_REF: self._device.ref,
            ATTR_LOCATION2: self._device.location2,
            ATTR_LOCATION: self._device.location,
            ATTR_NAME: self._device.name,
            ATTR_DEVICE_TYPE_STRING: self._device.device_type_string,
            ATTR_VALUE: self._device.value,
            ATTR_STATUS: self._device.status,
            ATTR_LAST_CHANGE: (
                dt.astimezone().isoformat("T", "seconds") if dt is not None else None
            ),
        }
        return attr

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the device."""
        return f"{self._bridge.namespace}-{self._device.ref}"

    @property
    def name(self) -> str:
        """Return the name of the device rendered from the user-supplied template."""
        return self._bridge.name_template.async_render(device=self._device).strip()

    @property
    def device_info(self) -> dict:
        """Return device info for the parent device."""
        parent_ref = self._device.ref
        if self._device.relationship == RELATIONSHIP_CHILD:
            parent_ref = self._device.associated_devices[0]

        parent = self._bridge.api.devices[parent_ref]

        return {
            "identifiers": {(self._bridge.namespace, parent.ref)},
            "name": f"{parent.location2} {parent.location} {parent.name}",
            "model": parent.device_type_string,
            "manufacturer": parent.interface_name,
            "via_device": (DOMAIN, self._bridge.namespace),
        }

    @property
    def should_poll(self) -> bool:
        """No polling necessary for HomeSeer entities."""
        return False

    async def async_added_to_hass(self) -> None:
        """Register update callback."""
        self._device.register_update_callback(self.async_schedule_update_ha_state)


class HomeSeerRemote:
    """Link remote-type devices that should fire events rather than create entities to Home Assistant."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: Union[
            HomeSeerStatusDevice,
            HomeSeerSwitchableDevice,
            HomeSeerDimmableDevice,
            HomeSeerLockableDevice,
        ],
    ) -> None:
        self._hass = hass
        self._device = device
        self._device.register_update_callback(
            self.update_callback, suppress_on_connection=True
        )
        self._event = f"homeseer_{CONF_EVENT}"

    def update_callback(self):
        """Fire the event."""
        data = {CONF_ID: self._device.ref, CONF_EVENT: self._device.value}
        self._hass.bus.async_fire(self._event, data, EventOrigin.remote)
