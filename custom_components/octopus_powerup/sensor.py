import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.util import dt as dt_util
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.components.recorder import get_instance, history
from .const import DOMAIN, EVENT_UPDATE_WINDOW, CONF_SOURCE_SENSOR

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    source_sensor = entry.data.get(CONF_SOURCE_SENSOR)
    
    # Registra ENTRAMBI i sensori: la media storica e il live!
    async_add_entities([
        OctopusPowerUpBaselineSensor(hass, source_sensor),
        OctopusPowerUpLiveConsumptionSensor(hass, source_sensor)
    ], True)


# ==============================================================================
# SENSORE 1: LA TUA MEDIA (BASELINE) - BASATA SUL TUO VECCHIO CODICE
# ==============================================================================
class OctopusPowerUpBaselineSensor(SensorEntity):
    def __init__(self, hass, source_sensor):
        self.hass = hass
        self._source_sensor = source_sensor
        self._attr_name = "PowerUp Baseline Media"
        # NOMI FORZATI PER LA TUA CARD GRAFICA
        self.entity_id = "sensor.octopus_powerup_baseline_media"
        self._attr_unique_id = "octopus_powerup_baseline_media"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_icon = "mdi:chart-line"
        self._state = 0.0

    @property
    def state(self):
        return self._state

    async def async_added_to_hass(self):
        self.hass.bus.async_listen(EVENT_UPDATE_WINDOW, self._handle_window_update)
        self.hass.async_create_task(self.async_update())

    async def _handle_window_update(self, event):
        await self.async_update()

    async def async_update(self):
        """Calcola la media interrogando il DB distinguendo feriali da festivi (Codice Originale)."""
        # Legge le variabili impostate dalla UI grafica
        date_entity = self.hass.states.get("date.data_powerup")
        start_entity = self.hass.states.get("time.inizio_powerup")
        end_entity = self.hass.states.get("time.fine_powerup")

        # Fallback sicuro se le entità non sono ancora pronte al primo avvio
        target_date_str = date_entity.state if date_entity and date_entity.state not in ["unknown", "unavailable"] else str(dt_util.now().date())
        start_time_str = start_entity.state if start_entity and start_entity.state not in ["unknown", "unavailable"] else "13:00:00"
        end_time_str = end_entity.state if end_entity and end_entity.state not in ["unknown", "unavailable"] else "14:00:00"

        try:
            target_date = dt_util.parse_date(target_date_str)
        except ValueError:
            target_date = dt_util.now().date()

        # Determina se il giorno SCELTO NELLA CARD è Feriale o Festivo/Weekend
        is_target_weekend = target_date.weekday() >= 5
        days_data = []

        def fetch_history(start_dt, end_dt):
            # IL TUO MOTORE PERFETTO CON include_start_time_state=True
            return history.state_changes_during_period(
                self.hass, start_dt, end_dt, self._source_sensor, include_start_time_state=True
            )

        days_checked = 1
        valid_days_found = 0

        # Torna indietro nel tempo fino a trovare 10 giorni della STESSA TIPOLOGIA
        while valid_days_found < 10 and days_checked <= 30:
            past_date = target_date - timedelta(days=days_checked)
            is_past_weekend = past_date.weekday() >= 5

            if is_target_weekend == is_past_weekend:
                start_str = f"{past_date} {start_time_str}"
                end_str = f"{past_date} {end_time_str}"

                start_dt = dt_util.parse_datetime(start_str)
                end_dt = dt_util.parse_datetime(end_str)

                if start_dt and end_dt:
                    # Forza il fuso orario UTC per non far incazzare il database di Home Assistant
                    start_dt = dt_util.as_utc(start_dt)
                    end_dt = dt_util.as_utc(end_dt)

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

                # Incrementiamo i giorni validi SOLO se era del tipo giusto (feriale con feriale)
                valid_days_found += 1

            days_checked += 1

        if days_data:
            self._state = round(sum(days_data) / len(days_data), 3)
            self.async_write_ha_state()
        else:
            self._state = 0.0
            self.async_write_ha_state()


# ==============================================================================
# SENSORE 2: CONSUMO IN TEMPO REALE (IL "RACCOGLI BOTTINO")
# ==============================================================================
class OctopusPowerUpLiveConsumptionSensor(SensorEntity):
    def __init__(self, hass, source_sensor):
        self.hass = hass
        self._source_sensor = source_sensor
        self._attr_name = "PowerUp Consumo Live"
        self.entity_id = "sensor.octopus_powerup_live_consumption"
        self._attr_unique_id = "octopus_powerup_live_consumption"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_icon = "mdi:lightning-bolt-circle"
        self._state = 0.0
        
        self._reference_value = None
        self._reference_date = None

    @property
    def state(self):
        return self._state

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._source_sensor], self._async_source_changed
            )
        )
        self.hass.bus.async_listen(EVENT_UPDATE_WINDOW, self._handle_window_update)

    async def _handle_window_update(self, event):
        self._evaluate_state(None)

    async def _async_source_changed(self, event):
        new_state = event.data.get("new_state")
        if new_state is None or new_state.state in ["unknown", "unavailable"]:
            return
        
        try:
            current_val = float(new_state.state)
        except ValueError:
            return

        self._evaluate_state(current_val)

    def _evaluate_state(self, current_val):
        now = dt_util.now()
        date_entity = self.hass.states.get("date.data_powerup")
        if not date_entity or date_entity.state in ["unknown", "unavailable"]:
            return
            
        try:
            target_date = dt_util.parse_date(date_entity.state)
        except ValueError:
            return

        start_entity = self.hass.states.get("time.inizio_powerup")
        end_entity = self.hass.states.get("time.fine_powerup")
        
        start_str = start_entity.state if start_entity else "13:00:00"
        end_str = end_entity.state if end_entity else "14:00:00"

        start_time_obj = dt_util.parse_time(start_str)
        end_time_obj = dt_util.parse_time(end_str)

        if not start_time_obj or not end_time_obj:
            return

        start_dt = now.replace(
            hour=start_time_obj.hour, minute=start_time_obj.minute, 
            second=0, microsecond=0
        )
        end_dt = now.replace(
            hour=end_time_obj.hour, minute=end_time_obj.minute, 
            second=0, microsecond=0
        )

        if now.date() != target_date or now < start_dt or now >= end_dt:
            if self._state != 0.0 or self._reference_value is not None:
                self._state = 0.0
                self._reference_value = None
                self.async_write_ha_state()
            return

        if start_dt <= now < end_dt and current_val is not None:
            if self._reference_value is None or self._reference_date != now.date():
                self._reference_value = current_val
                self._reference_date = now.date()
                self._state = 0.0
            else:
                self._state = round(current_val - self._reference_value, 3)
            
            self.async_write_ha_state()