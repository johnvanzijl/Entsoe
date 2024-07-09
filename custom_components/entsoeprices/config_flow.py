"""Config flow for ENTSO-E Prices integration."""
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import DOMAIN, CONF_API_KEY, DEFAULT_API_KEY

class EntsoePricesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ENTSO-E Prices."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="ENTSO-E Prices", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY, default=DEFAULT_API_KEY): str,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema)
