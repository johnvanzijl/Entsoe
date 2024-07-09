"""Button platform for ENTSO-E Prices."""
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import *

class EntsoePricesUpdateButton(CoordinatorEntity, ButtonEntity):
    """Button to manually update ENTSO-E Prices."""

    def __init__(self, coordinator):
        """Initialize the button."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_name = "Update ENTSO-E Prices"
        self._attr_unique_id = f"{coordinator.api_key}_update_button"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.api_key)},
            name=DEVICE_NAME,
            manufacturer="ENTSO-E",
            model="Day Ahead Prices",
            sw_version="1.0",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_request_refresh()
