"""Sensor platform for ENTSO-E Prices."""
from datetime import datetime, timedelta
import logging
import aiohttp

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, CONF_API_KEY, DEVICE_NAME
from .coordinator import EntsoeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

API_URL = 'https://web-api.tp.entsoe.e/api'
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)
INITIAL_UPDATE_INTERVAL = timedelta(minutes=1)

async def fetch_day_ahead_prices(api_key, start_date, end_date):
    _LOGGER.debug("Fetching day ahead prices from ENTSO-E API")
    params = {
        'documentType': 'A44',
        'in_Domain': '10YNL----------L',
        'out_Domain': '10YNL----------L',
        'periodStart': start_date.strftime('%Y%m%d%H%M'),
        'periodEnd': end_date.strftime('%Y%m%d%H%M'),
        'securityToken': api_key
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL, params=params) as response:
            if response.status != 200:
                _LOGGER.error("Failed to retrieve data: %s", response.status)
                raise UpdateFailed(f"Failed to retrieve data: {response.status}")
            data = await response.text()
            _LOGGER.debug("Successfully fetched data from ENTSO-E API: %s", data)
            return data

def calculate_consumer_price(groothandelsprijs_per_mwh):
    _LOGGER.debug("Calculating consumer price for wholesale price: %s", groothandelsprijs_per_mwh)
    netwerkkosten_per_kwh = 0.05
    belastingen_en_heffingen_per_kwh = 0.12
    ode_per_kwh = 0.02
    marge_en_administratiekosten_per_kwh = 0.03

    groothandelsprijs_per_kwh = groothandelsprijs_per_mwh / 1000
    consumentenprijs_per_kwh = (
        groothandelsprijs_per_kwh +
        netwerkkosten_per_kwh +
        belastingen_en_heffingen_per_kwh +
        ode_per_kwh +
        marge_en_administratiekosten_per_kwh
    )
    _LOGGER.debug("Calculated consumer price: %s", consumentenprijs_per_kwh)
    return consumentenprijs_per_kwh

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the sensor platform."""
    api_key = config_entry.data[CONF_API_KEY]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    await coordinator.async_refresh()
    async_add_entities([EntsoeSensor(coordinator)], True)

class EntsoeSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator: EntsoeDataUpdateCoordinator):
        """Initialize the sensor."""
        self.coordinator = coordinator
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

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            _LOGGER.debug("Returning state: %s", self.coordinator.data[0])
            return self.coordinator.data[0]  # Example: returning the first price
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "€/kWh"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if self.coordinator.data:
            _LOGGER.debug("Returning state attributes: %s", self.coordinator.data)
            return {"prices": self.coordinator.data}
        return {}

    async def async_update(self):
        """Update the sensor."""
        _LOGGER.debug("Updating sensor")
        await self.coordinator.async_request_refresh()
