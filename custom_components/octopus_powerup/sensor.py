import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.util import dt as dt_util
from homeassistant.components.recorder import get_instance, history
from .const import DOMAIN, EVENT_UPDATE_WINDOW, CONF_SOURCE_SENSOR

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    source_sensor = entry.data.get(CONF_SOURCE_SENSOR)
    async_add_entities([OctopusBaselineSensor(hass, source_sensor)], True)

class OctopusBaselineSensor(SensorEntity):
    def __init__(self, hass, source_sensor):
        self.hass = hass
        self._source_sensor = source_sensor
        self._attr_name = "Baseline Octopus 10 Giorni"
        self._attr_unique_id = "octopus_baseline_10_days"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_icon = "mdi:flash-outline"
        self._state = 0.0
        self._start_time = "13:00:00"
        self._end_time = "14:00:00"
        self._days_calculated = 0

    async def async_added_to_hass(self):
        """Si mette in ascolto di eventuali cambi di orario."""
        self.hass.bus.async_listen(EVENT_UPDATE_WINDOW, self._handle_window_update)

    async def _handle_window_update(self, event):
        """Forza il ricalcolo quando cambi i selettori."""
        await self.async_update_ha_state(force_refresh=True)

    @property
    def state(self):
        return self._state

    async def async_update(self):
        """Calcola la media interrogando il DB distinguendo feriali da festivi."""
        now = dt_util.now()
        days_data = []

        # Determina se oggi è un giorno Feriale (0-4: Lun-Ven) o Festivo/Weekend (5-6: Sab-Dom)
        is_target_weekend = now.weekday() >= 5

        # Legge gli orari dalle entità
        start_entity = self.hass.states.get("time.inizio_powerup")
        end_entity = self.hass.states.get("time.fine_powerup")
        self._start_time = start_entity.state if start_entity else "13:00:00"
        self._end_time = end_entity.state if end_entity else "14:00:00"

        def fetch_history(start_dt, end_dt):
            return history.state_changes_during_period(
                self.hass, start_dt, end_dt, self._source_sensor, include_start_time_state=True
            )

        days_checked = 1
        valid_days_found = 0

        # Torna indietro nel tempo fino a trovare 10 giorni della STESSA TIPOLOGIA
        # (Feriale con Feriale, Weekend con Weekend). Mettiamo un limite di 30 giorni
        # per evitare loop infiniti nel database.
        while valid_days_found < 10 and days_checked <= 30:
            target_date = now - timedelta(days=days_checked)
            is_past_weekend = target_date.weekday() >= 5

            # Controlla se il giorno passato è della stessa tipologia di oggi
            if is_target_weekend == is_past_weekend:
                start_str = f"{target_date.date()} {self._start_time}"
                end_str = f"{target_date.date()} {self._end_time}"

                start_dt = dt_util.parse_datetime(start_str)
                end_dt = dt_util.parse_datetime(end_str)

                if start_dt and end_dt:
                    states = await get_instance(self.hass).async_add_executor_job(
                        fetch_history, start_dt, end_dt
                    )

                    if self._source_sensor in states:
                        entity_states = states[self._source_sensor]
                        if len(entity_states) > 0:
                            try:
                                first_val = float(entity_states[0].state)
                                last_val = float(entity_states[-1].state)
                                consumo_giorno = last_val - first_val
                                if consumo_giorno >= 0:
                                    days_data.append(consumo_giorno)
                            except ValueError:
                                pass

                # Incrementiamo i giorni validi trovati solo se il giorno era del tipo giusto
                valid_days_found += 1

            days_checked += 1

        self._days_calculated = len(days_data)
        if days_data:
            self._state = round(sum(days_data) / len(days_data), 3)
        else:
            self._state = 0.0
