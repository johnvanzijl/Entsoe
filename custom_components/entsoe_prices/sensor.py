"""Sensor platform for ENTSO-E Prices."""
from datetime import datetime, timedelta
import logging
import requests

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import Throttle

from .const import DOMAIN, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

API_URL = 'https://transparency.entsoe.eu/api'
MIN_TIME_BETWEEN_UPDATES = timedelta(hours=24)

def fetch_day_ahead_prices(api_key, start_date, end_date):
    params = {
        'documentType': 'A44',
        'in_Domain': '10YNL----------L',
        'out_Domain': '10YNL----------L',
        'periodStart': start_date.strftime('%Y%m%d%H%M'),
        'periodEnd': end_date.strftime('%Y%m%d%H%M'),
        'securityToken': api_key
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.text  # This needs to be parsed into actual prices
    else:
        raise UpdateFailed(f"Failed to retrieve data: {response.status_code}")

def calculate_consumer_price(groothandelsprijs_per_mwh):
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
    return consumentenprijs_per_kwh

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""
    api_key = config_entry.data[CONF_API_KEY]
    coordinator = EntsoeDataUpdateCoordinator(hass, api_key)
    await coordinator.async_refresh()
    async_add_entities([EntsoeSensor(coordinator)], True)

class EntsoeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the ENTSO-E API."""

    def __init__(self, hass, api_key):
        """Initialize."""
        self.api_key = api_key
        super().__init__(
            hass,
            _LOGGER,
            name="EntsoeDataUpdateCoordinator",
            update_method=self._async_update_data,
            update_interval=MIN_TIME_BETWEEN_UPDATES,
        )

    async def _async_update_data(self):
        """Fetch data from ENTSO-E."""
        today = datetime.now()
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        end_date = start_date + timedelta(days=1)

        try:
            data = fetch_day_ahead_prices(self.api_key, start_date, end_date)
            groothandelsprijzen = [50]  # Example wholesale prices in €/MWh, should parse the XML data
            consumentenprijzen = [calculate_consumer_price(prijs) for prijs in groothandelsprijzen]
            return consumentenprijzen
        except Exception as e:
            raise UpdateFailed(f"Error fetching data: {e}")

class EntsoeSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return "ENTSO-E Consumer Prices"

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data[0]  # Example: returning the first price
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "€/kWh"

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self.coordinator.data:
            return {"prices": self.coordinator.data}
        return {}

    async def async_update(self):
        """Update the sensor."""
        await self.coordinator.async_request_refresh()
