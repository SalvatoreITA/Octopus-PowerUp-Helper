import logging
from datetime import time
from homeassistant.components.time import TimeEntity
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN, EVENT_UPDATE_WINDOW

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Crea le entità orario per il Power Up."""
    async_add_entities([
        OctopusPowerUpTime(hass, "Inizio PowerUp", "inizio_powerup", time(13, 0), "mdi:clock-start"),
        OctopusPowerUpTime(hass, "Fine PowerUp", "fine_powerup", time(14, 0), "mdi:clock-end")
    ])

class OctopusPowerUpTime(TimeEntity, RestoreEntity):
    """Entità orario che mantiene lo stato dopo il riavvio."""
    def __init__(self, hass, name, time_id, default_value, icon):
        self.hass = hass
        self._attr_name = name
        self._attr_unique_id = f"octopus_{time_id}"
        self.entity_id = f"time.{time_id}"
        self._attr_native_value = default_value
        self._attr_icon = icon

    async def async_added_to_hass(self) -> None:
        """Recupera l'ultimo stato salvato prima del riavvio."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state not in (None, "unknown", "unavailable"):
            try:
                self._attr_native_value = time.fromisoformat(last_state.state)
            except ValueError:
                pass

    async def async_set_value(self, value: time) -> None:
        """Salva il nuovo orario e avvisa il sistema."""
        self._attr_native_value = value
        self.async_write_ha_state()
        self.hass.bus.async_fire(EVENT_UPDATE_WINDOW)