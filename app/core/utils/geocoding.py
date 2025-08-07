import httpx
from typing import Optional, Dict
from app.core.config import settings

async def reverse_geocode(latitude: float, longitude: float) -> Optional[Dict[str, str]]:
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
            if data["results"]:
                components = data["results"][0]["components"]
                return {
                    "address": data["results"][0]["formatted"],
                    "country": components.get("country"),
                    "city": components.get("city") or components.get("town") or components.get("village")
                }
    return None
