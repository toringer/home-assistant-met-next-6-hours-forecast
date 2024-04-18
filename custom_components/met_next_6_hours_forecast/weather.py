"""Support for Met.no next 6 hours forecast service."""
import logging
import json
from datetime import datetime, timedelta
from random import randrange
import pytz



from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    UnitOfTemperature,
    UnitOfSpeed,
    UnitOfLength,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.util import dt as dt_util
from homeassistant.components.weather import (
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from .met_api import MetApi
from .const import ATTR_FORECAST_JSON, ATTRIBUTION, DOMAIN, NAME, CONDITIONS_MAP

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=randrange(40, 50))


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup weather platform."""
    api: MetApi = hass.data[DOMAIN]["api"]
    lat = entry.data[CONF_LATITUDE]
    lon = entry.data[CONF_LONGITUDE]
    name = entry.data[CONF_NAME]
    sensors = [SixHoursWeather(hass, api, name, lat, lon)]
    async_add_entities(sensors, True)


def format_condition(condition: str) -> str:
    """Return condition from dict CONDITIONS_MAP."""
    for key, value in CONDITIONS_MAP.items():
        if condition in value:
            return key
    return condition


class SixHoursWeather(WeatherEntity):
    """Representation of a Met.no next 6 hours forecast sensor."""

    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND
    _attr_native_precipitation_unit = UnitOfLength.MILLIMETERS
    _attr_supported_features = WeatherEntityFeature.FORECAST_HOURLY

    def __init__(
        self,
        hass: HomeAssistant,
        met_api: MetApi,
        location_name: str,
        lat: float,
        lon: float,
    ) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._met_api = met_api
        self.location_name = location_name
        self.lat = lat
        self.lon = lon
        self._raw_data = None
        self._forecast: list[Forecast] = None
        self._first_timeserie = None
        self._forecast_json = {}

    @property
    def force_update(self) -> str:
        """Force update."""
        return True

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"six-hours-forecast-{self.location_name}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{NAME}: {self.location_name}"

    @property
    def condition(self) -> str:
        """Return the current condition."""
        condition = self._first_timeserie["data"]["next_1_hours"]["summary"][
            "symbol_code"
        ]
        return format_condition(condition)

    @property
    def native_temperature(self) -> float:
        """Return the temperature."""
        return self._first_timeserie["data"]["instant"]["details"]["air_temperature"]

    @property
    def native_pressure(self) -> float:
        """Return the pressure."""
        return self._first_timeserie["data"]["instant"]["details"][
            "air_pressure_at_sea_level"
        ]

    @property
    def humidity(self) -> float:
        """Return the humidity."""
        return self._first_timeserie["data"]["instant"]["details"]["relative_humidity"]

    @property
    def native_wind_speed(self) -> float:
        """Return the wind speed."""
        return self._first_timeserie["data"]["instant"]["details"]["wind_speed"]

    @property
    def wind_bearing(self) -> float:
        """Return the wind direction."""
        return self._first_timeserie["data"]["instant"]["details"][
            "wind_from_direction"
        ]

    @property
    def attribution(self) -> str:
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_FORECAST_JSON: self._forecast_json
        }

    @property
    def forecast(self) -> list[Forecast]:
        """Return the forecast array."""
        return self._forecast

    @property
    def device_info(self):
        """Return the device_info of the device."""
        device_info = DeviceInfo(
            identifiers={(DOMAIN, self.location_name)},
            entry_type=DeviceEntryType.SERVICE,
            name=f"{NAME}: {self.location_name}",
            manufacturer="Met.no",
            model="Met.no next 6 hours forecast",
            configuration_url="https://www.met.no/en",
        )
        return device_info

    def serialize_datetime(self, obj):
        """serialize datetime to json"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError("Type not serializable")

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast in native units.
        Only implement this method if `WeatherEntityFeature.FORECAST_HOURLY` is set
        """
        return self._forecast

    async def async_update(self):
        """Retrieve latest state."""
        self._raw_data = await self._hass.async_add_executor_job(
            self._met_api.get_complete, self.lat, self.lon
        )

        timeseries = self._raw_data["properties"]["timeseries"]
        self._forecast = []
        last_added_time = None
        for timeserie in timeseries:
            time = dt_util.parse_datetime(timeserie["time"])

            if time < datetime.utcnow().replace(tzinfo=pytz.UTC):
                # skip forecast in the past
                continue

            if last_added_time is None or time >= last_added_time + timedelta(hours=6):
                if "next_6_hours" not in timeserie["data"]:
                    _LOGGER.debug("next_6_hours not found %s", time)
                    continue

                summary = timeserie["data"]["next_6_hours"]["summary"]
                condition = format_condition(summary["symbol_code"])
                details = timeserie["data"]["next_6_hours"]["details"]
                current = timeserie["data"]["instant"]["details"]

                self._forecast.append(
                    Forecast(
                        native_temperature=details["air_temperature_max"],
                        native_templow=details["air_temperature_min"],
                        native_precipitation=details["precipitation_amount"],
                        precipitation_probability=details[
                            "probability_of_precipitation"
                        ]
                        if "probability_of_precipitation" in details
                        else None,
                        datetime=time.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                        condition=condition,
                        native_pressure=current["air_pressure_at_sea_level"],
                        wind_bearing=current["wind_from_direction"],
                        native_wind_speed=current["wind_speed"],
                    )
                )
                last_added_time = time
        self._forecast_json = json.dumps(
            self._forecast, default=self.serialize_datetime
        )
        self._first_timeserie = self._raw_data["properties"]["timeseries"][0]
        _LOGGER.info("%s updated", self.location_name)
