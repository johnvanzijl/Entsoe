"""The ENTSO-E Prices integration."""
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "entsoe_prices"
SCAN_INTERVAL = timedelta(hours=24)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the ENTSO-E Prices component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ENTSO-E Prices from a config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload ENTSO-E Prices config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True
