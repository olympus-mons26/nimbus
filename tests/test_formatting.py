from datetime import datetime, timezone
from io import StringIO

from rich.console import Console

from nimbus.formatting import LOGO, _plain_table, _print_hourly, format_weather, print_logo
from nimbus.models import Location


def test_plain_output_has_no_branding_emoji_or_rich_decoration():
    output = StringIO()
    console = Console(file=output, force_terminal=False, no_color=True)
    weather = {
        "current": {"time": "2026-01-01T10:00", "weather_code": 0, "temperature_2m": 20},
        "timezone": "Asia/Kolkata",
        "utc_offset_seconds": 19800,
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
    assert "╭" not in text
    assert "│" not in text
    assert "Today's forecast" in text
    assert "Maximum: 22°C" in text


def test_non_color_rich_output_renders_panels_without_ansi_styles():
    output = StringIO()
    console = Console(file=output, force_terminal=False, no_color=True)
    weather = {
        "current": {"weather_code": 0, "temperature_2m": 29},
        "daily": {
            "temperature_2m_max": [31],
            "temperature_2m_min": [22],
            "precipitation_probability_max": [10],
        },
    }

    format_weather(
        console,
        Location("Hyderabad", 17.4, 78.5, "India"),
        weather,
        unit="°C",
        hourly=False,
        days=1,
        verbose=False,
        show_aqi=False,
        air_quality=None,
        color=False,
        emoji=False,
        suggestions=True,
        cached=False,
        stale=False,
        plain=False,
    )

    text = output.getvalue()
    assert "Hyderabad, India" in text
    assert "Today's forecast" in text
    assert "Nimbus says" in text
    assert "\x1b[" not in text


def test_time_checked_uses_current_city_time_not_observation_time(monkeypatch):
    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 11, 24, 6, 0, tzinfo=timezone.utc).astimezone(tz)

    monkeypatch.setattr("nimbus.formatting.datetime", FixedDateTime)
    output = StringIO()
    console = Console(file=output, force_terminal=False, no_color=True)
    weather = {
        "current": {
            "time": "2026-11-24T10:00",
            "weather_code": 0,
            "temperature_2m": 20,
        },
        "timezone": "Asia/Kolkata",
        "utc_offset_seconds": 19800,
        "daily": {
            "time": ["2026-11-24"],
            "temperature_2m_max": [22],
            "temperature_2m_min": [12],
            "precipitation_probability_max": [5],
        },
    }

    format_weather(
        console,
        Location("Hyderabad", 17.4, 78.5, "India", timezone="Asia/Kolkata"),
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
    assert "Time checked: 2026-11-24 11:30:00 (Asia/Kolkata)" in text
    assert "Current observation:" not in text


def test_plain_tables_align_columns_with_variable_cell_lengths():
    rendered = _plain_table(
        ("Time", "Conditions", "Rain"),
        [("00:00", "Overcast", "0%"), ("01:00", "Partly cloudy", "25%")],
    )
    lines = rendered.splitlines()

    assert len({len(line) for line in lines}) == 1
    assert "Time   Conditions     Rain" in lines[0]


def test_styled_hourly_table_keeps_rows_aligned_without_emoji_width_variation():
    output = StringIO()
    console = Console(file=output, width=100, force_terminal=False, no_color=True)
    hourly = {
        "time": ["2026-11-24T00:00", "2026-11-24T01:00"],
        "temperature_2m": [24.6, 24.2],
        "weather_code": [3, 2],
        "precipitation_probability": [0, 25],
        "wind_speed_10m": [6.5, 9.0],
    }

    _print_hourly(console, hourly, "°C", "km/h", plain=False, color=False)

    lines = [line for line in output.getvalue().splitlines() if line.strip()]
    assert len({len(line) for line in lines}) == 1
    assert "Overcast" in output.getvalue()
    assert "Partly cloudy" in output.getvalue()


def test_styled_logo_displays_nimbus_wordmark():
    output = StringIO()
    console = Console(file=output, force_terminal=False, no_color=True)

    print_logo(console, color=False)

    text = output.getvalue()
    assert LOGO.startswith(" _   _   ___")
    assert "NIMBUS WEATHER" in text
    assert "  ____  _         _" not in text
