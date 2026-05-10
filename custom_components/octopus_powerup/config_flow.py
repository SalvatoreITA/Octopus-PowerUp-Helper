import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from .const import DOMAIN, CONF_SOURCE_SENSOR

class OctopusPowerUpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestisce il flusso di configurazione per Octopus PowerUp da UI."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Assicura che non configuriamo la stessa integrazione due volte
            await self.async_set_unique_id(user_input[CONF_SOURCE_SENSOR])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="Octopus PowerUp Helper",
                data=user_input
            )

        # Genera il menu a tendina che filtra solo i sensori di energia
        data_schema = vol.Schema({
            vol.Required(
                CONF_SOURCE_SENSOR,
                default="sensor.energia_oggi_prelevata"
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="energy")
            ),
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
