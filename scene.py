"""
Support for HomeSeer Events.
"""

from homeassistant.components.scene import Scene

from .const import _LOGGER, CONF_ALLOWED_EVENT_GROUPS, DOMAIN

DEPENDENCIES = ["homeseer"]


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up HomeSeer events as Home Assistant scenes."""
    scenes = []
    allowed_event_groups = discovery_info[CONF_ALLOWED_EVENT_GROUPS]
    homeseer = hass.data[DOMAIN]

    for event in homeseer.events:
        if len(allowed_event_groups) > 0 and event.group not in allowed_event_groups:
            continue
        dev = HSScene(event)
        scenes.append(dev)
        _LOGGER.info(f"Added HomeSeer event: {dev.name}")

    async_add_entities(scenes)


class HSScene(Scene):
    """Representation of a HomeSeer event."""

    def __init__(self, event):
        self._event = event
        self._group = self._event.group
        self._name = self._event.name
        self._scene_name = f"{self._group} {self._name}"

    @property
    def name(self):
        """Return the name of the scene."""
        return self._scene_name

    async def async_activate(self):
        """Activate the scene."""
        await self._event.run()
