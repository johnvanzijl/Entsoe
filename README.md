ENTSO-E Prices Home Assistant Integration
This is a custom Home Assistant integration that fetches day-ahead electricity prices from the ENTSO-E API and calculates consumer prices. It supports manual data update requests and normal polling at regular intervals.

Features
Fetches day-ahead electricity prices from the ENTSO-E API.
Calculates consumer prices based on wholesale prices.
Allows manual data update requests via a service call.
Polls for updates every 15 minutes after the initial update.
Installation
Manual Installation
Download the integration files and place them in the custom_components/entsoeprices directory within your Home Assistant configuration directory.

Ensure your directory structure looks like this:

markdown
Code kopiëren
custom_components/
└── entsoeprices/
    ├── __init__.py
    ├── config_flow.py
    ├── const.py
    ├── manifest.json
    └── sensor.py
Configuration
Add the ENTSO-E Prices integration via the Home Assistant UI:

Go to Configuration -> Integrations.
Click the Add Integration button.
Search for "ENTSO-E Prices" and follow the setup instructions.
Add the following to your configuration.yaml to expose the update service:

yaml
Code kopiëren
homeassistant:
  customize:
    sensor.entsoe_prices:
      service: entsoeprices.update
Service Call
The integration provides a service to manually trigger a data update:

Service Name: entsoeprices.update
To use this service:

Go to Developer Tools -> Services.
Select the entsoeprices.update service.
Click Call Service.
Files Overview
__init__.py
Sets up and unloads the integration. Registers the service for manual data updates.

config_flow.py
Handles the configuration flow for the integration, allowing users to set it up via the Home Assistant UI.

const.py
Defines constants used throughout the integration.

manifest.json
Provides metadata about the integration.

sensor.py
Contains the logic for fetching and updating data from the ENTSO-E API and defining the sensor entity.

Logging
The integration uses the Home Assistant logging system. Logs can be found in the Home Assistant log file. To enable debugging for this integration, add the following to your configuration.yaml:

yaml
Code kopiëren
logger:
  default: info
  logs:
    custom_components.entsoeprices: debug
Issues
If you encounter any issues, please check the Home Assistant logs for errors and ensure your configuration is correct. If problems persist, feel free to open an issue on the project's GitHub page.

License
This project is licensed under the MIT License. See the LICENSE file for more details.

