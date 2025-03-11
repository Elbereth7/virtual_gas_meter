from homeassistant import config_entries
import voluptuous as vol
from homeassistant.helpers import entity_registry as er
from .const import DOMAIN, CONF_BOILER_ENTITY, CONF_BOILER_AVERAGE, CONF_LATEST_GAS_DATA, DEFAULT_BOILER_AV_H, DEFAULT_LATEST_GAS_DATA

class GasMeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Virtual Gas Meter integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the user input step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title="Virtual Gas Meter",
                data=user_input,
            )

        # Get list of switch.xxx entities
        boiler_entities = await self._get_switch_entities()

        if not boiler_entities:
            errors["base"] = "no_switches_found"

        schema = vol.Schema({
            vol.Required(CONF_BOILER_ENTITY, description={"translate": "boiler_entity"}): vol.In(boiler_entities),
            vol.Optional(CONF_BOILER_AVERAGE, default=DEFAULT_BOILER_AV_H, description={"translate": "boiler_average"}): vol.Coerce(float),
            vol.Optional(CONF_LATEST_GAS_DATA, default=DEFAULT_LATEST_GAS_DATA, description={"translate": "latest_gas_data"}): vol.Coerce(float),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def _get_switch_entities(self):
        """Retrieve switch.xxx entities from the entity registry."""
        entity_registry = er.async_get(self.hass)

        return [
            entity.entity_id for entity in entity_registry.entities.values()
            if entity.entity_id.startswith("switch.")
        ]
