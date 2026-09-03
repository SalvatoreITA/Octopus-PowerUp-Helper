import logging
from datetime import date
from homeassistant.components.date import DateEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util
from .const import DOMAIN, EVENT_UPDATE_WINDOW

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Crea l'entità data per il Power Up."""
    async_add_entities([
        OctopusPowerUpDate(hass, "Data PowerUp", "data_powerup", "mdi:calendar-star")
    ])

class OctopusPowerUpDate(DateEntity, RestoreEntity):
    """Entità data che mantiene lo stato dopo il riavvio."""
    def __init__(self, hass, name, date_id, icon):
        self.hass = hass
        self._attr_name = name
        self._attr_unique_id = f"octopus_powerup_{date_id}"
        self.entity_id = f"date.{date_id}"
        self._attr_native_value = dt_util.now().date()
        self._attr_icon = icon

    async def async_added_to_hass(self) -> None:
        """Recupera l'ultimo stato salvato prima del riavvio."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()

        if last_state is not None and last_state.state not in (None, "unknown", "unavailable"):
            try:
                self._attr_native_value = date.fromisoformat(last_state.state)
            except ValueError:
                pass

    async def async_set_value(self, value: date) -> None:
        """Salva la nuova data e avvisa il sistema."""
        self._attr_native_value = value
        self.async_write_ha_state()
        self.hass.bus.async_fire(EVENT_UPDATE_WINDOW)