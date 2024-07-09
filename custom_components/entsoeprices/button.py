"""Button platform for ENTSO-E Prices."""
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DEVICE_NAME, CONF_API_KEY
from .coordinator import EntsoeDataUpdateCoordinator

class EntsoePricesUpdateButton(CoordinatorEntity, ButtonEntity):
    """Button to manually update ENTSO-E Prices."""

    def __init__(self, coordinator):
        """Initialize the button."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_name = "Update ENTSO-E Prices"
        self._attr_unique_id = f"{coordinator.api_key}_update_button"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_request_refresh()

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the button platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([EntsoePricesUpdateButton(coordinator)], True)
