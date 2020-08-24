"""Support for the DOODS service."""
import io
import logging
import time

import voluptuous as vol

from homeassistant.components.image_processing import (
    CONF_CONFIDENCE,
    CONF_ENTITY_ID,
    CONF_NAME,
    CONF_SOURCE,
    PLATFORM_SCHEMA,
    ImageProcessingEntity,
)
from homeassistant.const import CONF_TIMEOUT
from homeassistant.core import split_entity_id
from homeassistant.helpers import template
import homeassistant.helpers.config_validation as cv

from colorthief import ColorThief

_LOGGER = logging.getLogger(__name__)

CONF_COLOR_COUNT = "color_count"
CONF_QUALITY = "quality"


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_COLOR_COUNT, default=1): cv.positive_int,
        vol.Required(CONF_QUALITY, default=5): cv.positive_int,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    entities = []
    for camera in config[CONF_SOURCE]:
        entities.append(
            ColorDetectionEntity(
                hass, camera[CONF_ENTITY_ID], camera.get(CONF_NAME), config,
            )
        )
    add_entities(entities)


class ColorDetectionEntity(ImageProcessingEntity):
    """Color Detection Entity"""

    def __init__(self, hass, camera_entity, name, config):
        self.hass = hass
        self._camera_entity = camera_entity
        if name:
            self._name = name
        else:
            name = split_entity_id(camera_entity)[1]
            self._name = f"ColorDetection {name}"

        self._color_count = config(CONF_COLOR_COUNT)
        self._quality = config(CONF_QUALITY)
        self._color_results = {}

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera_entity

    @property
    def name(self):
        """Return the name of the image processor."""
        return self._name

    @property
    def state(self):
        """Return the state of the entity."""
        return self._color_results

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        return self._color_results

    def process_image(self, image):
        """Process the image."""
        color_thief = ColorThief(image)

        # Run detection
        start = time.monotonic()
        response = color_thief.get_palette(
            color_count=self._color_count, quality=self._quality
        )
        _LOGGER.debug(
            "colordetect: response: %s duration: %s",
            response,
            time.monotonic() - start,
        )
        self._color_results = response

