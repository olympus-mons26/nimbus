# Nimbus Weather CLI

Nimbus is a cross-platform weather application for your terminal. Use `wf` to get live forecasts and air-quality information from Open-Meteo.

## Install

### Requirements

- Python 3.11 or newer
- Internet access for live weather, geocoding, and air-quality requests

### Install from GitHub

```sh
git clone https://github.com/olympus-mons26/nimbus.git
cd nimbus
python -m pip install .
```

The package installs `wf` and the command aliases `wi`, `wd`, `ws`, `wai`, `wh`, and `weather`. Make sure Python's scripts directory is on your `PATH`.

### Install for development

```sh
git clone https://github.com/olympus-mons26/nimbus.git
cd nimbus
python -m pip install -e ".[test]"
pytest
```

Nimbus has not yet been published to PyPI, Homebrew, or other package repositories. The Homebrew formula in `installers/homebrew/` is a template, not an available published formula.

## Run locally

From the project directory, create and activate a virtual environment, then install Nimbus in editable mode:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

Now run the CLI from the repository:

```sh
wd London
wf
wf Tokyo -h -f
```

Run the test suite with `python -m pytest -v`. To leave the environment, run `deactivate`.

## Use

### Get a forecast

```sh
wf London
wf Tokyo -h -f
wf Hyderabad -d5 -aqi -v
```

If you omit the city, `wf` uses your saved default city. Set or clear that value with:

```sh
wd London
wf
wd --clear
```

### Save preferences

```sh
ws set city London
ws set unit fahrenheit
ws set forecast hourly
ws set days 5
ws set aqi true
ws set verbose true
ws set color false
ws set emoji false
ws set suggestions false
ws
ws reset
```

Preferences are stored in TOML in your platform's user configuration directory:

- macOS: `~/Library/Application Support/nimbus-weather/config.toml`
- Windows: `%APPDATA%/nimbus-weather/config.toml`
- Linux: `$XDG_CONFIG_HOME/nimbus-weather/config.toml` or `~/.config/nimbus-weather/config.toml`

Command-line options override saved preferences for the current run.

### JSON and plain text

```sh
wf London -json > weather.json
wf London -nocolor
```

JSON includes location information, the useful raw API fields, units, timestamps, attribution, and cache status. Errors in JSON mode are returned as JSON too. `-nocolor` removes ANSI colors, emojis, logos, and visual decoration.

### Location lookup

`wi` or `weather info` asks for consent before using an approximate location derived from your public IP via ipapi.co. It does not use GPS. If lookup is unavailable or not approved, Nimbus uses the configured default city when possible. For non-interactive terminals, configure a default city or pass one directly to `wf`.

Weather and geocoding data are provided by [Open-Meteo](https://open-meteo.com/). Its applicable terms, attribution requirements, and non-commercial use conditions apply. Air-quality results use the **US AQI** standard; the information is general, not medical advice.

## Supported arguments and commands

### `wf [CITY] [OPTIONS]`

| Argument | Description |
| --- | --- |
| `-h` | Show the next 12 hours of hourly forecast. This is not help. |
| `-dN` | Show `N` forecast days (1–16), for example `-d5`. `-d` without a number selects 3 days. |
| `-aqi` | Include current air quality and pollutant readings using the US AQI scale. |
| `-c` | Display temperatures in Celsius (the default). |
| `-f` | Display temperatures in Fahrenheit. Mutually exclusive with `-c`. |
| `-v` | Show available feels-like temperature, humidity, UV index, wind, pressure, visibility, sunrise/sunset, and cloud cover. |
| `-json` | Emit machine-readable JSON without terminal decoration. |
| `-nocolor` | Disable colors, emojis, logo, borders, panels, and tables. |
| `--help` | Show forecast-command help. |
| `--version` | Show application version. |

Options can be combined in any order. Current temperature is distinguished from daily forecast maximum and minimum values.

### Commands

| Short command | Long command | Purpose |
| --- | --- | --- |
| `wi` | `weather info` | Ask permission, then show weather for your approximate location. |
| `wd CITY` | `weather default CITY` | Set your default city. Use `wd --clear` to remove it. |
| `ws` | `weather settings` | Display saved preferences. |
| `ws set KEY VALUE` | `weather settings set KEY VALUE` | Update a preference. Keys: `city`, `unit`, `forecast`, `days`, `verbose`, `aqi`, `color`, `emoji`, `suggestions`. |
| `ws reset` | `weather settings reset` | Restore default preferences. |
| `wai` | `weather appinfo` | Show app metadata; accepts `--version`, `--credits`, and `--license`. |
| `wh` | `weather help` | Show help and examples. |

### Examples

```sh
wf London
wf London -h
wf Tokyo -d7 -f
wf Hyderabad -aqi -v -nocolor
wf London -json | python -m json.tool
wd "New York"
ws set unit celsius
wai --credits
wh
```

## Example output

Illustrative values only; Nimbus displays actual values returned by the API.

```text
 _   _   ___   __  __   ____   _   _  _____
| \ | | |_ _| |  \/  | | __ ) | | | |/ ____|
|  \| |  | |  | |\/| | |  _ \ | | | | (___
| |\  |  | |  | |  | | | |_) || |_| |\___ \
|_| \_| |___| |_|  |_| |____/  \___/ |_____|
  NIMBUS WEATHER

╭──────────────────────────────────────────────────────────╮
│ Hyderabad, Telangana, India                              │
╰──────────────────────────────────────────────────────────╯
☀️  Clear sky
Time checked: 2026-11-24 10:00:00 (Asia/Kolkata)
Current temperature: 29°C
Data source: live Open-Meteo data

             Today's forecast
 Maximum: 31°C    Minimum: 22°C
 Rain probability: 10%

╭─ Nimbus says ────────────────────────────────────────────╮
│ Go touch some grass, dev. 🌱                              │
╰──────────────────────────────────────────────────────────╯

Weather data: Open-Meteo
```

This same NIMBUS ASCII wordmark appears in normal terminal reports. On supported interactive terminals, Nimbus adds color, condition icons, panels, and tables. Color is suppressed for non-interactive output, `NO_COLOR`, and terminals that do not support ANSI colors. JSON never includes terminal styling.
