"""Command-line entry point for Nimbus Weather CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from rich.console import Console

from nimbus import __version__
from nimbus.client import WeatherClient
from nimbus.config import Settings, load_settings, save_settings, settings_as_dict, update_setting
from nimbus.constants import (
    APP_NAME,
    DEVELOPER,
    LICENSE_NAME,
    MAX_FORECAST_DAYS,
    REPOSITORY,
)
from nimbus.errors import ConfigurationError, NetworkError, NimbusError, UsageError
from nimbus.formatting import format_weather, make_console, print_logo, print_settings
from nimbus.models import Location

HELP = """Usage: wf [CITY] [OPTIONS]

Fetch current conditions and today's forecast, or choose another view.

Options:
  -h                 Show the next 12 hours (hourly forecast)
  -dN                Show N days (1-16), e.g. -d5
  -aqi               Include current air quality (US AQI)
  -c, -f             Use Celsius or Fahrenheit (mutually exclusive)
  -v                 Include additional weather details
  -json              Emit machine-readable JSON only
  -nocolor           Plain text; disable logo, emoji, color and decoration
  --help             Show this help
  --version          Show the application version

Commands:
  wi / weather info                    Weather for an explicitly approved location
  wd CITY / weather default CITY       Set the default city
  wd --clear                           Clear the default city
  ws / weather settings                Show preferences
  ws set KEY VALUE                     Change a preference
  ws reset                             Restore default preferences
  wai / weather appinfo                Application, credits and license information
  wh / weather help                    Show help

Examples:
  wf London
  wf Tokyo -h -f
  wf Hyderabad -d5 -aqi -v
  wf London -json > weather.json
  wd "New York"
  ws set unit fahrenheit

Install for development: python -m pip install -e '.[test]'
Documentation: https://github.com/olympus-mons26/nimbus
Weather data: Open-Meteo (https://open-meteo.com/). Terms apply.
"""


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise UsageError(message)


def _forecast_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="wf", add_help=False)
    parser.add_argument("city", nargs="*")
    parser.add_argument("-h", dest="hourly", action="store_true")
    parser.add_argument("-d", dest="days", type=int, nargs="?", const=3)
    parser.add_argument("-aqi", "--aqi", dest="aqi", action="store_true")
    units = parser.add_mutually_exclusive_group()
    units.add_argument("-c", dest="unit", action="store_const", const="celsius")
    units.add_argument("-f", dest="unit", action="store_const", const="fahrenheit")
    parser.add_argument("-v", dest="verbose", action="store_true")
    parser.add_argument("-json", "--json", dest="json_output", action="store_true")
    parser.add_argument("-nocolor", "--nocolor", dest="no_color", action="store_true")
    parser.add_argument("--help", action="store_true")
    parser.add_argument("--version", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        args = list(sys.argv[1:])
        invoked_as = Path(sys.argv[0]).name
        if invoked_as in {"wi", "wd", "ws", "wai", "wh", "weather"}:
            args.insert(0, invoked_as)
    else:
        args = list(argv)
    json_mode = "-json" in args or "--json" in args
    no_color = "-nocolor" in args or "--nocolor" in args
    try:
        if args and args[0] in {"wi", "wd", "ws", "wai", "wh", "weather"}:
            return _dispatch_special(args, json_mode)
        return _run_forecast(args, json_mode, no_color)
    except NimbusError as exc:
        return _error(str(exc), json_mode)
    except (OSError, ValueError) as exc:
        return _error(str(exc), json_mode)


def _dispatch_special(args: list[str], json_mode: bool) -> int:
    command = args.pop(0)
    if command == "weather":
        if not args:
            command = "wh"
        else:
            subcommand = args.pop(0)
            command = {
                "info": "wi",
                "default": "wd",
                "settings": "ws",
                "appinfo": "wai",
                "help": "wh",
            }.get(subcommand, "")
            if not command:
                raise UsageError(f"Unknown weather command: {subcommand}")
    if command == "wh":
        plain = "-nocolor" in args or "--nocolor" in args
        console, color = make_console(plain)
        if not plain:
            print_logo(console, color)
            console.print()
        console.print(HELP)
        return 0
    if command == "wai":
        return _app_info(args)
    if command == "wd":
        return _set_default([arg for arg in args if arg not in {"-nocolor", "--nocolor"}])
    if command == "ws":
        return _settings_command(args)
    if command == "wi":
        return _weather_info(args, json_mode)
    raise UsageError("Unknown command.")


def _run_forecast(args: list[str], json_mode: bool, no_color: bool) -> int:
    parsed = _forecast_parser().parse_args(args)
    if parsed.version:
        print(__version__)
        return 0
    if parsed.help:
        if not no_color:
            console, color = make_console()
            print_logo(console, color)
            console.print()
        print(HELP)
        return 0
    settings = load_settings()
    if parsed.days is not None and not 1 <= parsed.days <= MAX_FORECAST_DAYS:
        raise UsageError(f"Day count must be between 1 and {MAX_FORECAST_DAYS}.")
    city = " ".join(parsed.city).strip() or settings.city
    if not city:
        raise ConfigurationError("No city was provided. Set a default with: wd London")
    unit = parsed.unit or settings.unit
    days = parsed.days if parsed.days is not None else settings.days
    hourly = parsed.hourly or (parsed.days is None and settings.forecast == "hourly")
    show_aqi = parsed.aqi or settings.aqi
    verbose = parsed.verbose or settings.verbose
    client = WeatherClient()
    location, geo_cached, geo_stale = client.geocode(city)
    weather, weather_cached, weather_stale = client.forecast(location, unit, days)
    air_quality: dict[str, Any] | None = None
    aq_cached = aq_stale = False
    if show_aqi:
        air_quality, aq_cached, aq_stale = client.air_quality(location)
    cached = geo_cached or weather_cached or aq_cached
    stale = geo_stale or weather_stale or aq_stale
    if json_mode:
        result = {
            "location": {
                "name": location.name,
                "admin1": location.admin1 or None,
                "country": location.country or None,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "timezone": location.timezone,
            },
            "forecast": weather,
            "air_quality": air_quality,
            "meta": {
                "application": APP_NAME,
                "unit": unit,
                "cached": cached,
                "stale_cache": stale,
                "data_timestamp": weather.get("current", {}).get("time"),
                "attribution": "Open-Meteo",
            },
        }
        print(json.dumps(result, ensure_ascii=False))
        return 0
    console, color = make_console(no_color or not settings.color)
    format_weather(
        console,
        location,
        weather,
        unit="°F" if unit == "fahrenheit" else "°C",
        hourly=hourly,
        days=days,
        verbose=verbose,
        show_aqi=show_aqi,
        air_quality=air_quality,
        color=color,
        emoji=settings.emoji,
        suggestions=settings.suggestions,
        cached=cached,
        stale=stale,
        plain=no_color,
    )
    return 0


def _set_default(args: list[str]) -> int:
    settings = load_settings()
    if args == ["--clear"]:
        settings.city = None
        save_settings(settings)
        print("Default city cleared.")
        return 0
    city = " ".join(args).strip()
    if not city:
        raise UsageError("Usage: wd CITY or wd --clear")
    settings.city = city
    target = save_settings(settings)
    print(f"Default city set to {city}. ({target})")
    return 0


def _settings_command(args: list[str]) -> int:
    plain = "-nocolor" in args or "--nocolor" in args
    args = [arg for arg in args if arg not in {"-nocolor", "--nocolor"}]
    settings = load_settings()
    if not args:
        console, _ = make_console(plain)
        print_settings(console, settings_as_dict(settings), plain)
        return 0
    if args == ["reset"]:
        target = save_settings(Settings())
        print(f"Settings reset to defaults. ({target})")
        return 0
    if len(args) >= 3 and args[0] == "set":
        value = " ".join(args[2:]) if args[1] == "city" else " ".join(args[2:])
        update_setting(settings, args[1], value)
        target = save_settings(settings)
        print(f"Updated {args[1]} to {value}. ({target})")
        return 0
    raise UsageError("Usage: ws | ws set KEY VALUE | ws reset")


def _app_info(args: list[str]) -> int:
    no_color = "-nocolor" in args or "--nocolor" in args
    if "--version" in args:
        print(__version__)
        return 0
    if "--license" in args:
        from importlib.resources import files

        print(files("nimbus").joinpath("LICENSE").read_text(encoding="utf-8"))
        return 0
    credits = "--credits" in args
    if any(arg not in {"--credits", "-nocolor", "--nocolor"} for arg in args):
        raise UsageError("Usage: wai [--credits|--license|--version] [-nocolor]")
    console, color = make_console(no_color)
    if not no_color:
        print_logo(console, color)
    console.print(f"\n{APP_NAME} {__version__}")
    console.print(f"Developer: {DEVELOPER}")
    console.print(f"License: {LICENSE_NAME}")
    console.print("Programming language: Python")
    console.print("Weather API: Open-Meteo")
    console.print(f"Repository: {REPOSITORY}")
    console.print(f"Platform: {sys.platform}")
    if credits:
        console.print("Weather data and geocoding provided by Open-Meteo.")
        console.print("Approximate location (wi) uses ipapi.co only after user consent.")
    return 0


def _weather_info(args: list[str], json_mode: bool) -> int:
    settings = load_settings()
    if not sys.stdin.isatty():
        if settings.city:
            if not json_mode:
                print(f"Location detection needs interactive permission. Using configured city: {settings.city}")
            return _run_forecast([settings.city], json_mode, "-nocolor" in args)
        raise ConfigurationError("Location lookup requires interactive consent. Use wf CITY or set a default with wd CITY.")
    print("Allow an approximate location lookup using your public IP via ipapi.co? [y/N]: ", end="", file=sys.stderr)
    answer = input().strip().casefold()
    if answer not in {"y", "yes"}:
        if settings.city:
            if not json_mode:
                print(f"Using configured city: {settings.city}")
            return _run_forecast([settings.city], json_mode, "-nocolor" in args)
        raise ConfigurationError("Location lookup was not approved. Use wf CITY or set a default with wd CITY.")
    client = WeatherClient()
    try:
        location_data, _, _ = client.approximate_location()
        city = location_data.get("city")
        latitude = location_data.get("latitude")
        longitude = location_data.get("longitude")
        if not city or latitude is None or longitude is None:
            raise NetworkError("The location service did not return a usable location.")
        location = Location(
            name=str(city),
            latitude=float(latitude),
            longitude=float(longitude),
            country=str(location_data.get("country_name", "")),
            admin1=str(location_data.get("region", "")),
        )
        weather, cached, stale = client.forecast(location, settings.unit, settings.days)
        air = None
        if settings.aqi:
            air, aqi_cached, aqi_stale = client.air_quality(location)
            cached = cached or aqi_cached
            stale = stale or aqi_stale
        if json_mode:
            print(json.dumps({
                "location": {
                    "name": location.name, "admin1": location.admin1 or None,
                    "country": location.country or None, "latitude": location.latitude,
                    "longitude": location.longitude, "timezone": "auto",
                },
                "forecast": weather, "air_quality": air,
                "meta": {
                    "application": APP_NAME, "unit": settings.unit,
                    "cached": cached, "stale_cache": stale,
                    "data_timestamp": weather.get("current", {}).get("time"),
                    "attribution": "Open-Meteo",
                },
            }, ensure_ascii=False))
        else:
            console, color = make_console("-nocolor" in args)
            format_weather(
                console, location, weather,
                unit="°F" if settings.unit == "fahrenheit" else "°C",
                hourly=settings.forecast == "hourly", days=settings.days,
                verbose=settings.verbose, show_aqi=settings.aqi, air_quality=air,
                color=color, emoji=settings.emoji, suggestions=settings.suggestions,
                cached=cached, stale=stale, plain="-nocolor" in args,
            )
        return 0
    except NetworkError:
        if settings.city:
            if not json_mode:
                print(f"Location lookup failed; using configured city: {settings.city}", file=sys.stderr)
            return _run_forecast([settings.city], json_mode, "-nocolor" in args)
        raise


def _error(message: str, json_mode: bool) -> int:
    if json_mode:
        print(json.dumps({"error": {"message": message, "type": "NimbusError"}}))
    else:
        print(f"Error: {message}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
