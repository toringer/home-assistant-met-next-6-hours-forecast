[![home-assistant-met-next-6-hours-forecast](https://img.shields.io/github/release/toringer/home-assistant-met-next-6-hours-forecast.svg?1)](https://github.com/toringer/home-assistant-met-next-6-hours-forecast)
[![Validate with hassfest](https://github.com/toringer/home-assistant-met-next-6-hours-forecast/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/toringer/home-assistant-met-next-6-hours-forecast/actions/workflows/hassfest.yaml)
[![HACS Validation](https://github.com/toringer/home-assistant-met-next-6-hours-forecast/actions/workflows/validate_hacs.yaml/badge.svg)](https://github.com/toringer/home-assistant-met-next-6-hours-forecast/actions/workflows/validate_hacs.yaml)
[![Maintenance](https://img.shields.io/maintenance/yes/2022.svg)](https://github.com/toringer/home-assistant-met-next-6-hours-forecast)
[![home-assistant-met-next-6-hours-forecast_downloads](https://img.shields.io/github/downloads/toringer/home-assistant-met-next-6-hours-forecast/total)](https://github.com/toringer/home-assistant-met-next-6-hours-forecast)
[![home-assistant-met-next-6-hours-forecast_downloads](https://img.shields.io/github/downloads/toringer/home-assistant-met-next-6-hours-forecast/latest/total)](https://github.com/toringer/home-assistant-met-next-6-hours-forecast)

# Met.no next 6 hours forecast component for Home Assistant

This component will add a weather sensor with data from [met.no](https://www.met.no/), similay to the default [met.no](https://www.home-assistant.io/integrations/met/) component, but using the next 6 hours forecast data.

The weather forecast is delivered by the Norwegian Meteorological Institute and the NRK.

![Weather card](weather.png)

## Installation

- Ensure that [HACS](https://hacs.xyz/) is installed.
- In HACS / Integrations / menu / Custom repositories, add the url the this repository.
- Search for and install the 'Met.no next 6 hours forecast' integration.
- Restart Home Assistant.

## Configuration

Configuration of the integration is done through Configuration > Integrations where you enter coordinates. 

Enter the latitude and longitude as decimals for the selected location.
![configure](configure.png)
