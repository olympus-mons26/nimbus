import httpx

from nimbus.cache import ResponseCache
from nimbus.client import WeatherClient
from nimbus.constants import GEOCODING_URL


def test_geocoding_uses_api_response_and_caches_it(tmp_path):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(
            200,
            json={
                "results": [{
                    "name": "London",
                    "latitude": 51.5,
                    "longitude": -0.1,
                    "country": "United Kingdom",
                    "timezone": "Europe/London",
                }]
            },
        )

    client = WeatherClient(
        cache=ResponseCache(tmp_path),
        transport=httpx.MockTransport(handler),
        retries=0,
    )
    location, cached, stale = client.geocode("London")
    client.geocode("London")

    assert location.label == "London, United Kingdom"
    assert not cached and not stale
    assert len(calls) == 1
    assert calls[0].url.host == "geocoding-api.open-meteo.com"
    assert calls[0].url.path == "/v1/search"


def test_transport_retries_then_returns_real_payload(tmp_path):
    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(503, json={"error": "temporary"})
        return httpx.Response(200, json={"current": {"temperature_2m": 12}})

    client = WeatherClient(
        cache=ResponseCache(tmp_path),
        transport=httpx.MockTransport(handler),
        retries=1,
    )

    payload, cached, stale = client._get(GEOCODING_URL, {"name": "test"})

    assert payload == {"current": {"temperature_2m": 12}}
    assert not cached and not stale
    assert attempts == 2
