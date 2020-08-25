"""ColorDetection"""
import io
import logging
import time
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
# from homeassistant.const import CONF_TIMEOUT
from homeassistant.core import split_entity_id
# from homeassistant.helpers import template
# import homeassistant.helpers.config_validation as cv

from colorthief import ColorThief

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA
)

from urllib.request import urlopen
from urllib.error import HTTPError

_LOGGER = logging.getLogger(__name__)

DOMAIN = "colordetection"

CONF_COLOR_COUNT = "color_count"
CONF_QUALITY = "quality"
CONF_SOURCE = "source"


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_COLOR_COUNT): cv.positive_int,
        vol.Required(CONF_QUALITY): cv.positive_int,
        vol.Required(CONF_SOURCE): cv.string,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    entity = [ColorDetectionSensor(hass, config)]
    _LOGGER.error(f"creating entity {entity}")
    add_entities(entity)


class ColorDetectionSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass, entity_config):
        """Initialize the sensor."""
        self._state = None
        self._entity_id = entity_config[CONF_SOURCE]
        self._color_count = entity_config[CONF_COLOR_COUNT]
        self._quality = entity_config[CONF_QUALITY]
        self._attributes = {
            CONF_SOURCE: self._entity_id,
            CONF_COLOR_COUNT:  self._color_count,
            CONF_QUALITY: self._quality
        }

        self._unique_id = f'{DOMAIN}_{self._entity_id}'

    @ property
    def name(self):
        """Return the name of the sensor."""
        return self._unique_id

    @ property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        return self._attributes

    @ property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return None

    def update(self):
        self._attributes.pop("error", None)
        source = self.hass.states.get(self._entity_id)
        _LOGGER.debug(source)
        instance_url = "localhost:8123"

        pic_path = source.attributes["entity_picture"]
        fullurl = f"http://{instance_url}{pic_path}"
        self._attributes["path"] = pic_path
        try:
            fd = urlopen(fullurl)
            with io.BytesIO(fd.read()) as f:
                color_thief = ColorThief(f)
                palette = color_thief.get_palette(
                    color_count=self._attributes[CONF_COLOR_COUNT], quality=self._attributes[CONF_QUALITY]
                )
                self._attributes["palette"] = palette
                self._state = "observing"
                _LOGGER.debug(self._attributes)
        except HTTPError as e:
            self._attributes["error"] = f"{e}"
            _LOGGER.debug(f"error occurred looking up {fullurl} error {e}")
