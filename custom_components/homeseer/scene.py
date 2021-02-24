"""Support for HomeSeer Events."""

import logging
from homeassistant.components.scene import Scene

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up HomeSeer events as Home Assistant scenes."""
    scenes = []
    bridge = hass.data[DOMAIN]

    for event in bridge.devices["scene"]:
        entity = HomeSeerScene(event)
        scenes.append(entity)
        _LOGGER.info(f"Added HomeSeer event: {entity.name}")

    if scenes:
        async_add_entities(scenes)


class HomeSeerScene(Scene):
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
