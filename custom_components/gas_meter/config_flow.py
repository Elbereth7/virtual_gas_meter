from homeassistant import config_entries

DOMAIN = "gas_meter"

class GasMeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Virtual Gas Meter integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Since no user input is required, create a config entry immediately
        return self.async_create_entry(
            title="Virtual Gas Meter", 
            data={}
        )
