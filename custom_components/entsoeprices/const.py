"""Constants for the ENTSO-E Prices integration."""
DOMAIN = "entsoeprices"
PLATFORMS = ["sensor", "button"]
CONF_API_KEY = "api_key"
DEVICE_NAME = "ENTSO-E Prices"

API_URL = 'https://web-api.tp.entsoe.eu/api'
NETWERKKOSTEN_PER_KWH = 0.05
BELASTINGEN_EN_HEFFINGEN_PER_KWH = 0.12
ODE_PER_KWH = 0.02
MARGE_EN_ADMINISTRATIEKOSTEN_PER_KWH = 0.03

DEFAULT_API_KEY = '324a1d9b-34c5-4308-8946-d858a78061ad'
