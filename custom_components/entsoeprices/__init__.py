"""The ENTSO-E Prices integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ENTSO-E Prices from a config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    async def handle_update(call):
        """Handle the service call to update data."""
        coordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "update", handle_update)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload ENTSO-E Prices config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.services.async_remove(DOMAIN, "update")
    return True
