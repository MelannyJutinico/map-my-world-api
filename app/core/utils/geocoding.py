"""
Utility module for reverse geocoding using the OpenCageData API.

This module defines functions to transform geographic coordinates into
address components, such as formatted address, city, and country.
"""

import httpx
from typing import Optional, Dict
from app.core.config import settings

async def reverse_geocode(
    latitude: float,
    longitude: float
) -> Optional[Dict[str, str]]:
    """
    Perform reverse geocoding to obtain address details for given coordinates.

    Sends a request to the OpenCageData API and returns a dictionary with:
      - formatted address
      - country name
      - city (or town/village) name

    :param latitude: Latitude in decimal degrees.
    :param longitude: Longitude in decimal degrees.
    :return: A dict with keys 'address', 'country', and 'city', or None if
             the API call fails or no results are found.
    """
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "key": settings.OPENCAGE_API_KEY,
        "q": f"{latitude},{longitude}",
        "language": "en",
        "pretty": 0
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results")
            if results:
                top = results[0]
                components = top.get("components", {})
                return {
                    "address": top.get("formatted"),
                    "country": components.get("country"),
                    "city": (
                        components.get("city") or
                        components.get("town") or
                        components.get("village")
                    )
                }
    return None
