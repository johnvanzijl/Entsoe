"""The ENTSO-E Prices integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ENTSO-E Prices from a config entry."""
    hass.config_entries.async_setup_platforms(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload ENTSO-E Prices config entry."""
    await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    return True
