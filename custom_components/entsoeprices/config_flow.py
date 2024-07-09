"""Config flow for ENTSO-E Prices integration."""
import logging
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import DOMAIN, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

class EntsoePricesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ENTSO-E Prices."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        _LOGGER.debug("Starting config flow step 'user'")
        errors = {}
        if user_input is not None:
            _LOGGER.debug("Received user input: %s", user_input)
            return self.async_create_entry(title="ENTSO-E Prices", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_API_KEY): str
        })

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        _LOGGER.debug("Starting options flow")
        return EntsoePricesOptionsFlowHandler(config_entry)

class EntsoePricesOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        _LOGGER.debug("Starting options flow step 'init'")
        if user_input is not None:
            _LOGGER.debug("Received user input for options: %s", user_input)
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_API_KEY, default=self.config_entry.data.get(CONF_API_KEY)): str
        })

        return self.async_show_form(
            step_id="init", data_schema=schema
        )
