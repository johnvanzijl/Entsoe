"""Sensor platform for ENTSO-E Prices."""
from datetime import datetime, timedelta
import logging
import aiohttp
import asyncio

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_API_KEY, DEVICE_NAME

_LOGGER = logging.getLogger(__name__)

API_URL = 'https://transparency.entsoe.eu/api'
MIN_TIME_BETWEEN_UPDATES = timedelta(hours=24)

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
    coordinator = EntsoeDataUpdateCoordinator(hass, api_key)
    await coordinator.async_refresh()
    async_add_entities([EntsoeSensor(coordinator)], True)

class EntsoeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the ENTSO-E API."""

    def __init__(self, hass: HomeAssistantType, api_key: str):
        """Initialize."""
        self.api_key = api_key
        super().__init__(
            hass,
            _LOGGER,
            name="EntsoeDataUpdateCoordinator",
            update_method=self._async_update_data,
            update_interval=MIN_TIME_BETWEEN
