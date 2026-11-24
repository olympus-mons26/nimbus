"""Persistent TOML user preferences."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nimbus.errors import ConfigurationError


@dataclass
class Settings:
    city: str | None = None
    unit: str = "celsius"
    forecast: str = "daily"
    days: int = 1
    verbose: bool = False
    aqi: bool = False
    color: bool = True
    emoji: bool = True
    suggestions: bool = True


def config_path() -> Path:
    if sys.platform == "win32":
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "nimbus-weather" / "config.toml"


def load_settings(path: Path | None = None) -> Settings:
    target = path or config_path()
    if not target.exists():
        return Settings()
    try:
        with target.open("rb") as stream:
            raw = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigurationError(f"Cannot read configuration at {target}: {exc}") from exc

    general = raw.get("general", {})
    display = raw.get("display", {})
    if not isinstance(general, dict) or not isinstance(display, dict):
        raise ConfigurationError("Configuration sections [general] and [display] must be tables.")
    settings = Settings(
        city=general.get("city"),
        unit=general.get("unit", "celsius"),
        forecast=display.get("forecast", "daily"),
        days=display.get("days", 1),
        verbose=display.get("verbose", False),
        aqi=display.get("aqi", False),
        color=display.get("color", True),
        emoji=display.get("emoji", True),
        suggestions=display.get("suggestions", True),
    )
    validate_settings(settings)
    return settings


def validate_settings(settings: Settings) -> None:
    if settings.city is not None and (not isinstance(settings.city, str) or not settings.city.strip()):
        raise ConfigurationError("The configured city must be a non-empty string.")
    if not isinstance(settings.unit, str) or settings.unit not in {"celsius", "fahrenheit"}:
        raise ConfigurationError("The configured unit must be 'celsius' or 'fahrenheit'.")
    if not isinstance(settings.forecast, str) or settings.forecast not in {"daily", "hourly"}:
        raise ConfigurationError("The configured forecast must be 'daily' or 'hourly'.")
    if isinstance(settings.days, bool) or not isinstance(settings.days, int) or not 1 <= settings.days <= 16:
        raise ConfigurationError("The configured day count must be an integer from 1 to 16.")
    for key in ("verbose", "aqi", "color", "emoji", "suggestions"):
        if not isinstance(getattr(settings, key), bool):
            raise ConfigurationError(f"The configured {key} value must be true or false.")


def save_settings(settings: Settings, path: Path | None = None) -> Path:
    validate_settings(settings)
    target = path or config_path()
    contents = (
        "[general]\n"
        f"city = {json.dumps(settings.city, ensure_ascii=False)}\n"
        f"unit = {json.dumps(settings.unit)}\n\n"
        "[display]\n"
        f"forecast = {json.dumps(settings.forecast)}\n"
        f"days = {settings.days}\n"
        f"verbose = {_toml_bool(settings.verbose)}\n"
        f"aqi = {_toml_bool(settings.aqi)}\n"
        f"color = {_toml_bool(settings.color)}\n"
        f"emoji = {_toml_bool(settings.emoji)}\n"
        f"suggestions = {_toml_bool(settings.suggestions)}\n"
    )
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=target.parent, delete=False
        ) as stream:
            stream.write(contents)
            temporary = Path(stream.name)
        temporary.replace(target)
    except OSError as exc:
        raise ConfigurationError(f"Cannot save configuration at {target}: {exc}") from exc
    return target


def _toml_bool(value: bool) -> str:
    return "true" if value else "false"


def update_setting(settings: Settings, key: str, value: str) -> None:
    key = key.casefold()
    if key == "city":
        settings.city = value.strip() or None
    elif key == "unit":
        candidate = value.casefold()
        if candidate not in {"celsius", "fahrenheit"}:
            raise ConfigurationError("Unit must be 'celsius' or 'fahrenheit'.")
        settings.unit = candidate
    elif key == "forecast":
        candidate = value.casefold()
        if candidate not in {"daily", "hourly"}:
            raise ConfigurationError("Forecast must be 'daily' or 'hourly'.")
        settings.forecast = candidate
    elif key == "days":
        try:
            settings.days = int(value)
        except ValueError as exc:
            raise ConfigurationError("Days must be an integer from 1 to 16.") from exc
        if not 1 <= settings.days <= 16:
            raise ConfigurationError("Days must be an integer from 1 to 16.")
    elif key in {"verbose", "aqi", "color", "emoji", "suggestions"}:
        candidate = value.casefold()
        if candidate not in {"true", "false"}:
            raise ConfigurationError(f"{key} must be 'true' or 'false'.")
        setattr(settings, key, candidate == "true")
    else:
        raise ConfigurationError(f"Unknown setting: {key}")


def settings_as_dict(settings: Settings) -> dict[str, Any]:
    return {
        "city": settings.city,
        "unit": settings.unit,
        "forecast": settings.forecast,
        "days": settings.days,
        "verbose": settings.verbose,
        "aqi": settings.aqi,
        "color": settings.color,
        "emoji": settings.emoji,
        "suggestions": settings.suggestions,
    }
