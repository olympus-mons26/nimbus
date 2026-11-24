from io import StringIO

from rich.console import Console

from nimbus.formatting import format_weather
from nimbus.models import Location


def test_plain_output_has_no_branding_emoji_or_rich_decoration():
    output = StringIO()
    console = Console(file=output, force_terminal=False, no_color=True)
    weather = {
        "current": {"time": "2026-01-01T10:00", "weather_code": 0, "temperature_2m": 20},
        "daily": {
            "time": ["2026-01-01"],
            "temperature_2m_max": [22],
            "temperature_2m_min": [12],
            "precipitation_probability_max": [5],
        },
        "current_units": {"temperature_2m": "°C"},
    }

    format_weather(
        console,
        Location("London", 51.5, -0.1, "United Kingdom"),
        weather,
        unit="°C",
        hourly=False,
        days=1,
        verbose=False,
        show_aqi=False,
        air_quality=None,
        color=False,
        emoji=False,
        suggestions=False,
        cached=False,
        stale=False,
        plain=True,
    )

    text = output.getvalue()
    assert "NIMBUS WEATHER" not in text
    assert "☀" not in text
    assert "Today's forecast" in text
    assert "Maximum: 22°C" in text
