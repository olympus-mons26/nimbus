"""Terminal presentation for weather and app information."""

from __future__ import annotations

import os
import sys
from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from nimbus.constants import AQI_CATEGORIES, APP_NAME, WEATHER_CODES
from nimbus.models import Location
from nimbus.suggestions import activity_suggestion

LOGO = r"""  ____  _         _
 / ___|| | ___   | |_   _ _ __   ___
 \___ \| |/ / | | | | | | | '_ \ / _ \
  ___) |   <| |_| | | |_| | |_) |  __/
 |____/|_|\_\__,_|_|\__, | .__/ \___|
                      |___/|_|"""

WEATHER_ICONS = {
    0: ("☀️", "yellow"),
    1: ("🌤️", "yellow"),
    2: ("⛅", "yellow"),
    3: ("☁️", "white"),
    45: ("🌫️", "bright_black"),
    48: ("🌫️", "bright_black"),
    51: ("🌧️", "blue"),
    53: ("🌧️", "blue"),
    55: ("🌧️", "blue"),
    56: ("🌧️", "blue"),
    57: ("🌧️", "blue"),
    61: ("🌧️", "blue"),
    63: ("🌧️", "blue"),
    65: ("🌧️", "blue"),
    66: ("🌧️", "blue"),
    67: ("🌧️", "blue"),
    71: ("❄️", "cyan"),
    73: ("❄️", "cyan"),
    75: ("❄️", "cyan"),
    77: ("❄️", "cyan"),
    80: ("🌧️", "blue"),
    81: ("🌧️", "blue"),
    82: ("🌧️", "blue"),
    85: ("❄️", "cyan"),
    86: ("❄️", "cyan"),
    95: ("⛈️", "red"),
    96: ("⛈️", "red"),
    99: ("⛈️", "red"),
}


def make_console(no_color: bool = False) -> tuple[Console, bool]:
    terminal = bool(getattr(sys.stdout, "isatty", lambda: False)())
    term = os.environ.get("TERM", "").casefold()
    term_supports_color = bool(term and term not in {"dumb", "unknown"})
    color = terminal and term_supports_color and not no_color and "NO_COLOR" not in os.environ
    return Console(file=sys.stdout, no_color=not color, force_terminal=color), color


def weather_icon(code: int | None) -> tuple[str, str]:
    return WEATHER_ICONS.get(code, ("", "cyan"))


def print_logo(console: Console, color: bool) -> None:
    console.print(Text(LOGO, style="bold cyan" if color else None))
    console.print(Text("  NIMBUS WEATHER", style="bold bright_white" if color else None))


def format_weather(
    console: Console,
    location: Location,
    weather: dict[str, Any],
    *,
    unit: str,
    hourly: bool,
    days: int,
    verbose: bool,
    show_aqi: bool,
    air_quality: dict[str, Any] | None,
    color: bool,
    emoji: bool,
    suggestions: bool,
    cached: bool,
    stale: bool,
    plain: bool,
) -> None:
    current = weather.get("current", {})
    daily = weather.get("daily", {})
    hourly_data = weather.get("hourly", {})
    units = weather.get("current_units", {})
    temperature_unit = units.get("temperature_2m", "°C")
    wind_unit = units.get("wind_speed_10m", "km/h")
    condition_code = _int_or_none(current.get("weather_code"))
    condition = WEATHER_CODES.get(condition_code, "Weather conditions unavailable")
    icon, condition_color = weather_icon(condition_code)
    if plain:
        icon = ""
    elif not emoji:
        icon = ""

    if not plain:
        print_logo(console, color)
        console.print()
        console.print(Panel(Text(location.label, style="bold" if color else None), border_style="cyan" if color else None))
        condition_line = f"{icon} {condition}".strip()
        console.print(Text(condition_line, style=condition_color if color else None))
    else:
        console.print(f"Location: {location.label}")
        console.print(f"Condition: {condition}")

    if current.get("time"):
        console.print(f"Current observation: {current['time']}")
    if current.get("temperature_2m") is not None:
        console.print(f"Current temperature: {current['temperature_2m']}{temperature_unit}")
    if cached:
        marker = " (stale cache)" if stale else ""
        console.print(f"Data source: cached Open-Meteo data{marker}")
    else:
        console.print("Data source: live Open-Meteo data")

    daily_dates = daily.get("time", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])
    rain = daily.get("precipitation_probability_max", [])
    if hourly:
        _print_hourly(console, hourly_data, temperature_unit, wind_unit, emoji, plain, color)
    elif days > 1:
        _print_daily(console, daily, days, temperature_unit, emoji, plain, color)
    elif highs and lows:
        values = (
            f"Maximum: {highs[0]}{temperature_unit}    Minimum: {lows[0]}{temperature_unit}\n"
            f"Rain probability: {_percent(rain[0] if rain else None)}"
        )
        if plain:
            console.print("\nToday's forecast\n" + values)
        else:
            console.print(Panel(values, title="Today's forecast", border_style="blue" if color else None))

    if verbose:
        details = []
        _add_detail(details, "Feels like", current.get("apparent_temperature"), temperature_unit)
        _add_detail(details, "Humidity", current.get("relative_humidity_2m"), "%")
        _add_detail(details, "Wind", current.get("wind_speed_10m"), f" {wind_unit}")
        _add_detail(details, "Wind direction", current.get("wind_direction_10m"), "°")
        _add_detail(details, "Pressure", current.get("pressure_msl"), " hPa")
        _add_detail(details, "Visibility", current.get("visibility"), " m")
        _add_detail(details, "Cloud cover", current.get("cloud_cover"), "%")
        _add_detail(details, "UV index", _first(daily.get("uv_index_max")), "")
        _add_detail(details, "Sunrise", _first(daily.get("sunrise")), "")
        _add_detail(details, "Sunset", _first(daily.get("sunset")), "")
        if details:
            if plain:
                console.print("\nAdditional conditions\n" + "\n".join(details))
            else:
                table = Table(title="Additional conditions", box=box.SIMPLE, show_header=False)
                for detail in details:
                    name, value = detail.split(": ", 1)
                    table.add_row(name, value)
                console.print(table)

    if show_aqi and air_quality:
        _print_air_quality(console, air_quality, plain, color)

    if suggestions:
        current_temp = current.get("temperature_2m")
        temp_c = _to_celsius(current_temp, unit)
        rain_chance = _int_or_none(_first(rain))
        advice = activity_suggestion(
            condition_code,
            temp_c,
            rain_chance,
            _float_or_none(current.get("wind_speed_10m")),
        )
        if plain or not emoji:
            advice = _without_emoji(advice)
        if plain:
            console.print(f"\nSuggestion: {advice}")
        else:
            console.print(Panel(Text(advice, style="green" if color else None), title="Nimbus says", border_style="green" if color else None))

    if not plain and color:
        console.print("\n[dim]Weather data: Open-Meteo[/dim]")
    else:
        console.print("\nWeather data: Open-Meteo")


def _print_hourly(
    console: Console, hourly: dict[str, Any], temp_unit: str, wind_unit: str,
    emoji: bool, plain: bool, color: bool,
) -> None:
    times = hourly.get("time", [])[:12]
    temps = hourly.get("temperature_2m", [])
    codes = hourly.get("weather_code", [])
    rain = hourly.get("precipitation_probability", [])
    wind = hourly.get("wind_speed_10m", [])
    if plain:
        rows = ["\nHourly forecast (next 12 hours)", "Time | Temp | Condition | Rain | Wind"]
        for index, timestamp in enumerate(times):
            code = _int_or_none(_at(codes, index))
            rows.append(
                f"{timestamp} | {_at(temps, index)}{temp_unit} | "
                f"{WEATHER_CODES.get(code, 'Unavailable')} | {_percent(_at(rain, index))} | "
                f"{_at(wind, index)} {wind_unit}"
            )
        console.print("\n".join(rows))
        return
    table = Table(title="Hourly forecast · next 12 hours", box=box.ROUNDED if color else box.SIMPLE)
    for heading in ("Time", "Temperature", "Conditions", "Rain", "Wind"):
        table.add_column(heading, style="cyan" if color else None)
    for index, timestamp in enumerate(times):
        code = _int_or_none(_at(codes, index))
        icon, _ = weather_icon(code)
        if not emoji:
            icon = ""
        table.add_row(
            str(timestamp)[11:16],
            f"{_at(temps, index)}{temp_unit}",
            f"{icon} {WEATHER_CODES.get(code, 'Unavailable')}".strip(),
            _percent(_at(rain, index)),
            f"{_at(wind, index)} {wind_unit}",
        )
    console.print(table)


def _print_daily(
    console: Console, daily: dict[str, Any], days: int, temp_unit: str,
    emoji: bool, plain: bool, color: bool,
) -> None:
    dates = daily.get("time", [])[:days]
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])
    codes = daily.get("weather_code", [])
    rain = daily.get("precipitation_probability_max", [])
    if plain:
        lines = [f"\n{days}-day forecast", "Date | Conditions | Maximum | Minimum | Rain"]
        for index, date in enumerate(dates):
            code = _int_or_none(_at(codes, index))
            lines.append(
                f"{date} | {WEATHER_CODES.get(code, 'Unavailable')} | "
                f"{_at(highs, index)}{temp_unit} | {_at(lows, index)}{temp_unit} | "
                f"{_percent(_at(rain, index))}"
            )
        console.print("\n".join(lines))
        return
    table = Table(title=f"{days}-day forecast · daily values", box=box.ROUNDED if color else box.SIMPLE)
    for heading in ("Date", "Conditions", "Maximum", "Minimum", "Rain"):
        table.add_column(heading, style="cyan" if color else None)
    for index, date in enumerate(dates):
        code = _int_or_none(_at(codes, index))
        icon, _ = weather_icon(code)
        if not emoji:
            icon = ""
        table.add_row(
            str(date),
            f"{icon} {WEATHER_CODES.get(code, 'Unavailable')}".strip(),
            f"{_at(highs, index)}{temp_unit}",
            f"{_at(lows, index)}{temp_unit}",
            _percent(_at(rain, index)),
        )
    console.print(table)


def _print_air_quality(console: Console, payload: dict[str, Any], plain: bool, color: bool) -> None:
    current = payload.get("current", {})
    aqi = _int_or_none(current.get("us_aqi"))
    category = next((name for limit, name in AQI_CATEGORIES if aqi is not None and aqi <= limit), "Beyond scale")
    values = [
        ("US AQI", f"{aqi} ({category})" if aqi is not None else "Unavailable"),
        ("PM2.5", _with_unit(current.get("pm2_5"), "µg/m³")),
        ("PM10", _with_unit(current.get("pm10"), "µg/m³")),
        ("Ozone", _with_unit(current.get("ozone"), "µg/m³")),
        ("Nitrogen dioxide", _with_unit(current.get("nitrogen_dioxide"), "µg/m³")),
        ("Sulphur dioxide", _with_unit(current.get("sulphur_dioxide"), "µg/m³")),
        ("Carbon monoxide", _with_unit(current.get("carbon_monoxide"), "µg/m³")),
    ]
    if plain:
        console.print("\nAir quality (US AQI)\n" + "\n".join(f"{key}: {value}" for key, value in values))
        console.print("Health note: Higher AQI values can affect health, especially for sensitive groups.")
    else:
        table = Table(title="Air quality · US AQI", box=box.ROUNDED if color else box.SIMPLE)
        table.add_column("Measure", style="cyan" if color else None)
        table.add_column("Reading")
        for key, value in values:
            table.add_row(key, value)
        console.print(table)
        console.print("Higher AQI values can affect health, especially for sensitive groups.")


def print_settings(console: Console, values: dict[str, Any], plain: bool) -> None:
    if plain:
        console.print("\n".join(f"{key}: {value}" for key, value in values.items()))
        return
    table = Table(title=APP_NAME + " settings", box=box.ROUNDED)
    table.add_column("Setting", style="cyan")
    table.add_column("Value")
    for key, value in values.items():
        table.add_row(key, str(value))
    console.print(table)


def _add_detail(details: list[str], name: str, value: Any, suffix: str) -> None:
    if value is not None:
        details.append(f"{name}: {value}{suffix}")


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _without_emoji(value: str) -> str:
    for symbol in ("⛈️", "🌧️", "🌬️", "☀️", "❄️", "🌱"):
        value = value.replace(symbol, "")
    return value.strip()


def _to_celsius(value: Any, unit: str) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return (numeric - 32) * 5 / 9 if unit.casefold() in {"fahrenheit", "°f"} else numeric


def _percent(value: Any) -> str:
    return f"{value}%" if value is not None else "Unavailable"


def _with_unit(value: Any, unit: str) -> str:
    return f"{value} {unit}" if value is not None else "Unavailable"


def _first(values: Any) -> Any:
    return values[0] if isinstance(values, list) and values else None


def _at(values: Any, index: int) -> Any:
    return values[index] if isinstance(values, list) and index < len(values) else "—"
