""" Met.no API."""
from __future__ import annotations
import logging
import requests
from .const import NotFound

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://api.met.no/weatherapi/locationforecast/2.0"
REQUEST_HEADER = {
    "User-Agent": "home-assistant-met-next-6-hours-forecast https://github.com/toringer/home-assistant-met-next-6-hours-forecast"
}


class MetApi:
    """Met.no API"""

    def __init__(self) -> None:
        """Init"""

    def get_complete(self, lat: float, lon: float):
        """Get complete forecast"""
        url = f"{BASE_URL}/complete"
        param = {"lat": lat, "lon": lon}
        response = requests.get(url=url, params=param, headers=REQUEST_HEADER)
        if response.status_code != 200:
            raise NotFound

        data = response.json()
        return data
