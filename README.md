# Nimbus Weather CLI

**Nimbus** is a cross-platform weather application for your terminal. Its short command is `wf` (“Weather Forecast”). Look up live conditions, hourly and multi-day forecasts, and air quality without an API key.

> The executable remains `wf` to preserve the requested command interface.

## What it does

- Retrieves current conditions, today's high/low forecast, hourly data, and up to 16 forecast days from Open-Meteo.
- Resolves city names with Open-Meteo geocoding.
- Shows US AQI and available pollutant readings on request.
- Uses Celsius by default, with Fahrenheit support.
- Offers a styled terminal view, a clean plain-text mode, and JSON for scripts.
- Saves preferences in TOML; caches responses briefly and retries transient API failures.
- Uses free, keyless services for weather and geocoding.

## Installation

Requires Python 3.11 or newer. PyPI publication and release downloads have **not** been performed from this checkout.

### Install from source

```sh
git clone https://github.com/olympus-mons26/nimbus.git
cd nimbus
python -m pip install .
wf London
```

The package installs `wf` and the short aliases `wi`, `wd`, `ws`, `wai`, and `wh`, plus the long-form `weather` entry point. If the Python scripts directory is not on `PATH`, add it to your shell's `PATH`.

### Install for development

```sh
git clone https://github.com/olympus-mons26/nimbus.git
cd nimbus
python -m pip install -e ".[test]"
pytest
```

Once published to PyPI, the intended isolated install will be:

```sh
pipx install nimbus-weather-cli
```

This command is not available until the package is published. Homebrew, DMG, Windows installer, DEB, and RPM installation are also not yet published; the Homebrew formula is a clearly marked template.

## Quick start

```sh
wf London
wf Tokyo -h -f
wf Hyderabad -d5 -aqi -v
wf London -json > weather.json
wf London -nocolor
```

With no city argument, `wf` uses your saved default city. Set or clear that value with `wd London` or `wd --clear`.

### Example output

The readings below illustrate the layout only; the application always fetches actual API values.

```text
  ____  _         _
 / ___|| | ___   | |_   _ _ __   ___
 \___ \| |/ / | | | | | | | '_ \ / _ \
  ___) |   <| |_| | | |_| | |_) |  __/
 |____/|_|\_\__,_|_|\__, | .__/ \___|
                      |___/|_|
  NIMBUS WEATHER

╭──────────────────────────────────────────────────────────╮
│ Hyderabad, Telangana, India                              │
╰──────────────────────────────────────────────────────────╯
☀️  Clear sky
Current temperature: 29°C
Current observation: 2026-11-24T10:00
Data source: live Open-Meteo data

             Today's forecast
 Maximum: 31°C    Minimum: 22°C
 Rain probability: 10%

╭─ Nimbus says ────────────────────────────────────────────╮
│ Go touch some grass, dev. 🌱                              │
╰──────────────────────────────────────────────────────────╯

Weather data: Open-Meteo
```

On terminals that support it, Nimbus uses ANSI colors and condition icons. `NO_COLOR`, non-interactive output, or `TERM=dumb` disables ANSI color. `-nocolor` disables colors, emojis, the ASCII logo, and decorative panels/tables for plain output. JSON output never contains terminal decorations.

## Commands and options

### Main forecast command

```text
wf [CITY] [OPTIONS]

  -h                 Hourly forecast for the next 12 hours (not help)
  -dN                Forecast for N days, from 1 to 16; for example -d5
  -aqi               Include current air quality (US AQI standard)
  -c                 Display temperatures in Celsius
  -f                 Display temperatures in Fahrenheit; -c and -f conflict
  -v                 Add available humidity, UV, wind, pressure, visibility,
                     sunrise/sunset, cloud cover, and feels-like values
  -json              Emit JSON only; supports pipes and redirection
  -nocolor           Plain text without logo, emoji, colors, or decoration
  --help             Show main-command help
  --version          Show version
```

Options can be combined in any order. Celsius is the default. `-h` is intentionally reserved for hourly forecast; use `wh` or `weather help` for help. Invalid cities, day counts, mutually exclusive units, configuration errors, API failures, and network errors produce actionable messages and nonzero exit status. JSON failures produce a JSON error object.

### Special commands

| Short form | Long form | Description |
| --- | --- | --- |
| `wi` | `weather info` | Ask permission before approximate public-IP location lookup, then show weather. |
| `wd CITY` | `weather default CITY` | Save the default city. `wd --clear` removes it. |
| `ws` | `weather settings` | Display current preferences. |
| `ws set KEY VALUE` | `weather settings set KEY VALUE` | Change a saved preference. |
| `ws reset` | `weather settings reset` | Restore default preferences. |
| `wai` | `weather appinfo` | Show application metadata. Supports `--version`, `--credits`, `--license`. |
| `wh` | `weather help` | Show help and examples. |

`ws set` accepts `city`, `unit`, `verbose`, `aqi`, `color`, `emoji`, `forecast`, `days`, and `suggestions`:

```sh
wd "New York"
ws set unit fahrenheit
ws set verbose true
ws set aqi true
ws set color false
ws set emoji false
ws set forecast hourly
ws set days 5
ws set suggestions false
ws reset
```

Configuration is written to `config.toml` in the platform's user configuration directory:

- macOS: `~/Library/Application Support/nimbus-weather/`
- Windows: `%APPDATA%/nimbus-weather/`
- Linux: `$XDG_CONFIG_HOME/nimbus-weather/` or `~/.config/nimbus-weather/`

Example:

```toml
[general]
city = "London"
unit = "celsius"

[display]
forecast = "daily"
days = 1
verbose = false
aqi = false
color = true
emoji = true
suggestions = true
```

Command-line options override saved preferences for that invocation and do not rewrite the configuration.

### Location privacy

`wi` uses an approximate location inferred from your public IP via ipapi.co; it does not use GPS. It requests interactive consent before making the lookup. If permission is declined or the lookup is unavailable, Nimbus uses the configured default city when possible. Ordinary `wf CITY` requests do not perform location lookup. In non-interactive use, `wi` falls back to the configured default or returns an error.

## Data, attribution, and caching

Weather forecasts, geocoding, and air quality are provided by [Open-Meteo](https://open-meteo.com/). Data is subject to Open-Meteo's current terms, attribution requirements, and non-commercial usage conditions. Review the applicable terms before redistribution or commercial use. Air quality is labelled **US AQI**; category text is general information, not medical advice.

Successful API responses are cached for 10 minutes to reduce repeated requests. If a request fails, a cached response up to 24 hours old may be used and is explicitly labelled as stale. JSON includes location, raw API fields, units and timestamps, attribution, and cache status.

## Docker

Docker is optional and is not required for normal use:

```sh
docker build -t nimbus-weather .
docker run --rm nimbus-weather London
docker run --rm nimbus-weather London -json
```

## Packaging and releases

Build a standalone executable for the current host platform and architecture:

```sh
python -m pip install ".[build]"
python scripts/build.py
```

The GitHub Actions definitions test Linux, macOS, and Windows with multiple Python versions. Tag-triggered release builds use native runners for macOS arm64, macOS x86_64, Windows x64, and Linux x86_64, then attach binaries/archives and checksums to a GitHub Release. Release publication, signing, notarization, a Homebrew tap, PyPI, APT, DEB/RPM packages, and a Windows installer still require external publishing setup and credentials; they are not claimed as completed.

## Development

```sh
python -m pip install -e ".[test]"
pytest
python -m nimbus London -json
```

The code is organized under `nimbus/` with separate modules for API access, settings, caching, formatting, suggestions, and CLI dispatch. Tests use mock API responses and do not make real weather requests.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance. Do not include API credentials or personal location data in issues.

## License

Nimbus Weather CLI is licensed under the MIT License. See [LICENSE](LICENSE).
