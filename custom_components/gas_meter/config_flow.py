from homeassistant import config_entries

# Import your integration's constants
from .const import DOMAIN

class YourIntegrationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Since no user input is required, create a config entry immediately
        return self.async_create_entry(
            title="Virtual Gas Meter", 
            data={}
        )
