"""HTTP access to Open-Meteo APIs with bounded retries and caching."""

from __future__ import annotations

import time
from typing import Any

import httpx

from nimbus.cache import ResponseCache
from nimbus.constants import (
    AIR_QUALITY_URL,
    CACHE_TTL_SECONDS,
    GEOCODING_URL,
    USER_AGENT,
    WEATHER_URL,
)
from nimbus.errors import NetworkError
from nimbus.models import Location


class WeatherClient:
    def __init__(
        self,
        cache: ResponseCache | None = None,
        timeout: float = 10.0,
        retries: int = 2,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.cache = cache or ResponseCache()
        self.timeout = timeout
        self.retries = retries
        self.transport = transport

    def _get(self, url: str, params: dict[str, Any]) -> tuple[dict[str, Any], bool, bool]:
        cached = self.cache.read(url, params)
        if cached and cached[1] <= CACHE_TTL_SECONDS:
            return cached[0], True, False

        headers = {"User-Agent": USER_AGENT}
        try:
            with httpx.Client(
                timeout=self.timeout, headers=headers, transport=self.transport
            ) as client:
                for attempt in range(self.retries + 1):
                    try:
                        response = client.get(url, params=params)
                        if response.status_code == 429 or response.status_code >= 500:
                            if attempt < self.retries:
                                retry_after = response.headers.get("Retry-After")
                                try:
                                    delay = min(float(retry_after), 4.0) if retry_after else 0.4 * (2**attempt)
                                except ValueError:
                                    delay = 0.4 * (2**attempt)
                                time.sleep(max(delay, 0))
                                continue
                        response.raise_for_status()
                        payload = response.json()
                        if not isinstance(payload, dict):
                            raise NetworkError("The weather service returned an unexpected response.")
                        self.cache.write(url, params, payload)
                        return payload, False, False
                    except (httpx.TimeoutException, httpx.TransportError) as exc:
                        if attempt >= self.retries:
                            raise NetworkError(f"Could not reach the weather service: {exc}") from exc
                        time.sleep(0.4 * (2**attempt))
                    except httpx.HTTPStatusError as exc:
                        status = exc.response.status_code
                        if status == 429:
                            raise NetworkError("The weather service rate limit was reached; try again shortly.") from exc
                        raise NetworkError(f"The weather service returned HTTP {status}.") from exc
                    except ValueError as exc:
                        raise NetworkError("The weather service returned invalid JSON.") from exc
        except NetworkError:
            if cached and cached[1] <= 24 * 60 * 60:
                return cached[0], True, True
            raise
        raise NetworkError("The weather request could not be completed.")

    def geocode(self, city: str) -> tuple[Location, bool, bool]:
        payload, cached, stale = self._get(
            GEOCODING_URL,
            {"name": city, "count": 1, "language": "en", "format": "json"},
        )
        results = payload.get("results") or []
        if not results:
            from nimbus.errors import CityNotFoundError

            raise CityNotFoundError(f"No matching city found for '{city}'. Check the spelling and try again.")
        return Location.from_geocoding(results[0]), cached, stale

    def forecast(
        self, location: Location, unit: str, days: int
    ) -> tuple[dict[str, Any], bool, bool]:
        current_fields = ",".join(
            (
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "is_day",
                "precipitation",
                "rain",
                "weather_code",
                "cloud_cover",
                "pressure_msl",
                "wind_speed_10m",
                "wind_direction_10m",
                "visibility",
            )
        )
        hourly_fields = ",".join(
            (
                "temperature_2m",
                "precipitation_probability",
                "weather_code",
                "wind_speed_10m",
            )
        )
        daily_fields = ",".join(
            (
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_max",
                "sunrise",
                "sunset",
                "uv_index_max",
            )
        )
        return self._get(
            WEATHER_URL,
            {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "current": current_fields,
                "hourly": hourly_fields,
                "daily": daily_fields,
                "temperature_unit": unit,
                "wind_speed_unit": "kmh",
                "timezone": location.timezone or "auto",
                "forecast_days": days,
            },
        )

    def air_quality(self, location: Location) -> tuple[dict[str, Any], bool, bool]:
        return self._get(
            AIR_QUALITY_URL,
            {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "current": "us_aqi,pm2_5,pm10,ozone,nitrogen_dioxide,sulphur_dioxide,carbon_monoxide",
                "timezone": location.timezone or "auto",
            },
        )

    def approximate_location(self) -> tuple[dict[str, Any], bool, bool]:
        return self._get("https://ipapi.co/json/", {})
