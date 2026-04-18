import logging
from datetime import time
from homeassistant.components.time import TimeEntity
from .const import DOMAIN, EVENT_UPDATE_WINDOW

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Crea le entità orario."""
    async_add_entities([
        OctopusPowerUpTime(hass, "Inizio PowerUp", "inizio", time(13, 0), "mdi:clock-start"),
        OctopusPowerUpTime(hass, "Fine PowerUp", "fine", time(14, 0), "mdi:clock-end")
    ])

class OctopusPowerUpTime(TimeEntity):
    def __init__(self, hass, name, time_id, default_value, icon):
        self.hass = hass
        self._attr_name = name
        self._attr_unique_id = f"octopus_powerup_{time_id}"
        self._attr_native_value = default_value
        self._attr_icon = icon

    async def async_set_value(self, value: time) -> None:
        """Salva il nuovo orario quando lo cambi dalla plancia."""
        self._attr_native_value = value
        self.async_write_ha_state()

        # Avvisa il sensore che l'orario è cambiato e deve ricalcolare!
        self.hass.bus.async_fire(EVENT_UPDATE_WINDOW)
