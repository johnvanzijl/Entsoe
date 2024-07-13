"""Sensor platform for ENTSO-E Prices."""
from datetime import datetime, timedelta
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, CONF_API_KEY, DEVICE_NAME
from .coordinator import EntsoeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

API_URL = 'https://web-api.tp.entsoe.eu/api'
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)
INITIAL_UPDATE_INTERVAL = timedelta(minutes=1)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the sensor platform."""
    _LOGGER.debug("Setting up sensor platform")
    api_key = config_entry.data[CONF_API_KEY]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    await coordinator.async_refresh()
    async_add_entities([EntsoeHistoricalSensor(coordinator)], True)
    _LOGGER.debug("Sensor platform setup complete")

class EntsoeHistoricalSensor(CoordinatorEntity, SensorEntity):
    """Representation of a historical sensor."""

    def __init__(self, coordinator: EntsoeDataUpdateCoordinator):
        """Initialize the sensor."""
        _LOGGER.debug("Initializing EntsoeHistoricalSensor")
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.api_key)},
            name=DEVICE_NAME,
            manufacturer="ENTSO-E",
            model="Day Ahead Prices",
            sw_version="1.0",
        )
        self._attr_name = "ENTSO-E Consumer Prices"
        self._attr_unique_id = f"{coordinator.api_key}_consumer_prices"
        self._state = None
        self._attr_extra_state_attributes = {}
        _LOGGER.debug("EntsoeHistoricalSensor initialized")

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            _LOGGER.debug("Returning latest state data: %s", self.coordinator.data)
            latest_price = self.coordinator.data[-1] if self.coordinator.data else None
            if latest_price is not None:
                _LOGGER.debug("Returning latest state: %s", latest_price)
                return latest_price
        _LOGGER.debug("State not available")
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        _LOGGER.debug("Returning unit of measurement: €/kWh")
        return "€/kWh"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if self.coordinator.data:
            historical_data = {entry['date'].isoformat(): entry['price_amount'] for entry in self.coordinator.data}
            self._attr_extra_state_attributes.update(historical_data)
            _LOGGER.debug("Returning state attributes: %s", self._attr_extra_state_attributes)
        else:
            _LOGGER.debug("No state attributes to return")
        return self._attr_extra_state_attributes

    async def async_update(self):
        """Update the sensor."""
        _LOGGER.debug("Updating sensor")
        await self.coordinator.async_request_refresh()
        _LOGGER.debug("Sensor update complete")
