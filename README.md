# Nimbus Weather CLI

**NOTE: Please use Homebrew only to install Nimbus, not the .dmg, as it does not work yet. Apologies.**

---


Nimbus is a cross-platform weather application for your terminal. Use `wf` to get live forecasts and air-quality information from Open-Meteo.

## Install

### Requirements

- Python 3.11 or newer for installation from source
- Homebrew and macOS Apple Silicon for the Homebrew package
- Internet access for live weather, geocoding, and air-quality requests

### Install with Homebrew (macOS Apple Silicon)

Once Nimbus has been published to the Homebrew tap, install it with one command:

```sh
brew install olympus-mons26/tap/nimbus
```

Homebrew will add the tap automatically. If the formula is not available yet, the repository owner needs to complete the one-time setup in the [Homebrew publishing guide](docs/HOMEBREW.md) and publish the first release.

### Install from source with Python

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

Homebrew publishing is automated but requires a tap repository and the `HOMEBREW_TAP_TOKEN` secret. Follow [the Homebrew publishing guide](docs/HOMEBREW.md) before pushing to `main`; the one-command install above works once the first release is published. The current tap build supports macOS Apple Silicon only. PyPI publication has not been configured.

## Update or uninstall

### Homebrew

Update Homebrew's package information, then upgrade Nimbus:

```sh
brew update
brew upgrade olympus-mons26/tap/nimbus
```

Uninstall it with:

```sh
brew uninstall olympus-mons26/tap/nimbus
```

### Python installation

To update an installation made from a local Git checkout, pull the latest changes and reinstall:

```sh
cd /path/to/nimbus
git pull
python -m pip install --upgrade .
```

Uninstall the Python package from the same Python environment where it was installed:

```sh
python -m pip uninstall nimbus-weather-cli
```

Uninstalling Nimbus does not remove its saved preferences or weather cache. These are stored separately from the executable; remove them only if you also want to delete your Nimbus settings and cached data. Their locations are listed under [Save preferences](#save-preferences).

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

### Build a standalone executable

Install the build dependency and run the shared build script:

```sh
python -m pip install ".[build]"
python scripts/build.py
```

The script builds `dist/wf`, packages it with the README and license in a platform-specific archive under `dist/`, and writes a matching `.sha256` checksum file. It does not create a DMG. To check the executable, run `./dist/wf --version` (on Windows, run `.\dist\wf.exe --version`).

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

Run `wh` or `wf --help` for help. In Nimbus, `-h` means hourly forecast; it is not the help option.

### Run with Docker

Docker is optional. Build the image from the repository root:

```sh
docker build -t nimbus-weather .
docker run --rm nimbus-weather London
docker run --rm nimbus-weather London -json
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

Cached weather responses are stored separately:

- macOS: `~/Library/Caches/nimbus-weather`
- Windows: `%LOCALAPPDATA%/nimbus-weather`
- Linux: `$XDG_CACHE_HOME/nimbus-weather` or `~/.cache/nimbus-weather`

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
| `-aqi`, `--aqi` | Include current air quality and pollutant readings using the US AQI scale. |
| `-c` | Display temperatures in Celsius (the default). |
| `-f` | Display temperatures in Fahrenheit. Mutually exclusive with `-c`. |
| `-v` | Show available feels-like temperature, humidity, UV index, wind, pressure, visibility, sunrise/sunset, and cloud cover. |
| `-json`, `--json` | Emit machine-readable JSON without terminal decoration. |
| `-nocolor`, `--nocolor` | Disable colors, emojis, logo, borders, panels, and tables. |
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

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for development and contribution guidance.
