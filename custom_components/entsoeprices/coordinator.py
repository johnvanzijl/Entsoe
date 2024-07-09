"""Coordinator for ENTSO-E Prices."""
from datetime import datetime, timedelta
import logging
import aiohttp
import xml.etree.ElementTree as ET

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant

from .const import *

_LOGGER = logging.getLogger(__name__)

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
                response_text = await response.text()
                _LOGGER.error("Failed to retrieve data: %s, Response: %s", response.status, response_text)
                raise UpdateFailed(f"Failed to retrieve data: {response.status}")
            data = await response.text()
            _LOGGER.debug("Successfully fetched data from ENTSO-E API: %s", data)
            return data

def parse_prices(data):
    """Parse the XML data to extract prices."""
    root = ET.fromstring(data)
    timeseries = []
    for period in root.findall('.//Period'):
        _LOGGER.debug("Period: %s", period)
        start_time = period.find('timeInterval/start').text
        _LOGGER.debug("start_time: %s", start_time)
        end_time = period.find('timeInterval/end').text
        for point in period.findall('Point'):
            position = point.find('position').text
            _LOGGER.debug("position: %s", position)
            price = point.find('price.amount').text
            _LOGGER.debug("price: %s", price)
            timeseries.append({
                'start_time': start_time,
                'end_time': end_time,
                'position': position,
                'price': float(price)
            })
    _LOGGER.debug("timeseries: %s", timeseries)
    return timeseries

def calculate_consumer_price(groothandelsprijs_per_mwh):
    _LOGGER.debug("Calculating consumer price for wholesale price: %s", groothandelsprijs_per_mwh)
    groothandelsprijs_per_kwh = groothandelsprijs_per_mwh / 1000
    consumentenprijs_per_kwh = (
        groothandelsprijs_per_kwh +
        NETWERKKOSTEN_PER_KWH +
        BELASTINGEN_EN_HEFFINGEN_PER_KWH +
        ODE_PER_KWH +
        MARGE_EN_ADMINISTRATIEKOSTEN_PER_KWH
    )
    _LOGGER.debug("Calculated consumer price: %s", consumentenprijs_per_kwh)
    return consumentenprijs_per_kwh

class EntsoeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the ENTSO-E API."""

    def __init__(self, hass: HomeAssistant, api_key: str):
        """Initialize."""
        self.api_key = api_key
        self.update_interval = INITIAL_UPDATE_INTERVAL
        super().__init__(
            hass,
            _LOGGER,
            name="EntsoeDataUpdateCoordinator",
            update_method=self._async_update_data,
            update_interval=self.update_interval,
        )

    async def _async_update_data(self):
        """Fetch data from ENTSO-E."""
        _LOGGER.debug("Updating data from ENTSO-E")
        today = datetime.now()
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        end_date = start_date + timedelta(days=2)

        try:
            data = await fetch_day_ahead_prices(self.api_key, start_date, end_date)
            _LOGGER.debug("Fetched data: %s", data)  # Log the raw data
            timeseries = parse_prices(data)
            _LOGGER.debug("Parsed timeseries: %s", timeseries)
            # Calculate consumer prices
            consumentenprijzen = [calculate_consumer_price(point['price']) for point in timeseries]
            for i, point in enumerate(timeseries):
                point['consumer_price'] = consumentenprijzen[i]
            return timeseries
        except Exception as e:
            _LOGGER.error("Error fetching data: %s", e)
            raise UpdateFailed(f"Error fetching data: {e}")
