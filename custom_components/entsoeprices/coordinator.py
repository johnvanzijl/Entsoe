"""Coordinator for ENTSO-E Prices."""
from datetime import datetime, timedelta
import logging
import aiohttp
from lxml import etree

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

API_URL = 'https://web-api.tp.entsoe.eu/api'
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)
INITIAL_UPDATE_INTERVAL = timedelta(seconds=10)

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
            return parse_day_ahead_prices(data)

def parse_day_ahead_prices(xml_data):
    """Parse the XML data and extract prices."""
    _LOGGER.debug("Parsing XML data")
    try:
        root = etree.fromstring(bytes(xml_data, 'utf-8'))
        ns = {'ns': 'urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0'}
        
        # List to hold the data
        data = []
        
        # Extract TimeSeries data
        for ts in root.findall('ns:TimeSeries', namespaces=ns):
            period = ts.find('ns:Period', namespaces=ns)
            start = period.find('ns:timeInterval/ns:start', namespaces=ns).text
            
            for point in period.findall('ns:Point', namespaces=ns):
                position = float(point.find('ns:position', namespaces=ns).text)
                price_amount = point.find('ns:price.amount', namespaces=ns).text
                
                datum = datetime.strptime(start, '%Y-%m-%dT%H:%MZ') + timedelta(hours=(position-1))
                data.append({
                    'date': datum,
                    'price_amount': float(price_amount)
                })
        
        _LOGGER.debug("Parsed data: %s", data)
        return data
    except Exception as e:
        _LOGGER.error("Error parsing XML data: %s", e)
        raise UpdateFailed(f"Error parsing XML data: {e}")

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

class EntsoeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the ENTSO-E API."""

    def __init__(self, hass: HomeAssistant, api_key: str):
        """Initialize."""
        _LOGGER.debug("Initializing EntsoeDataUpdateCoordinator")
        self.api_key = api_key
        self.update_interval = INITIAL_UPDATE_INTERVAL
        super().__init__(
            hass,
            _LOGGER,
            name="EntsoeDataUpdateCoordinator",
            update_method=self._async_update_data,
            update_interval=self.update_interval,
        )
        _LOGGER.debug("EntsoeDataUpdateCoordinator initialized")

    async def _async_update_data(self):
        """Fetch data from ENTSO-E."""
        _LOGGER.debug("Updating data from ENTSO-E")
        today = datetime.now()
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=-1)
        end_date = start_date + timedelta(days=3)

        try:
            data = await fetch_day_ahead_prices(self.api_key, start_date, end_date)
            _LOGGER.debug("Fetched data: %s", data)  # Log the raw data
            groothandelsprijzen = [entry['price_amount'] for entry in data]  # Extracting prices
            _LOGGER.debug("Parsed wholesale prices: %s", groothandelsprijzen)
            consumentenprijzen = [calculate_consumer_price(prijs) for prijs in groothandelsprijzen]
            _LOGGER.debug("Calculated consumer prices: %s", consumentenprijzen)
            # Update the polling interval after the initial update
            self.update_interval = MIN_TIME_BETWEEN_UPDATES
            #return consumentenprijzen
            return data
        except Exception as e:
            _LOGGER.error("Error fetching data: %s", e)
            raise UpdateFailed(f"Error fetching data: {e}")
