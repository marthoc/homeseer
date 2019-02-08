"""
Support for HomeSeer Events.
"""
import logging

from . import DOMAIN
from homeassistant.components.scene import Scene

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['homeseer']


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up HomeSeer events as Home Assistant scenes."""
    scenes = []
    homeseer = hass.data[DOMAIN]

    for event in homeseer.events:
        dev = HSScene(event)
        scenes.append(dev)
        _LOGGER.info('Added HomeSeer event: {}'.format(dev.name))

    async_add_entities(scenes)


class HSScene(Scene):
    """Representation of a HomeSeer event."""

    def __init__(self, event):
        self._event = event
        self._group = self._event.group
        self._name = self._event.name
        self._scene_name = '{} {}'.format(self._group, self._name)

    @property
    def name(self):
        """Return the name of the scene."""
        return self._scene_name

    async def async_activate(self):
        """Activate the scene."""
        await self._event.run()
