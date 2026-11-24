"""Weather-code based activity suggestions."""

from typing import Any


def activity_suggestion(
    weather_code: int | None,
    temperature_c: float | None,
    rain_chance: int | None,
    wind_kmh: float | None = None,
) -> str:
    if weather_code in {95, 96, 99}:
        return "The outdoors can wait, dev. ⛈️"
    if weather_code in {65, 67, 82, 86} or (rain_chance is not None and rain_chance >= 70):
        return "Maybe keep that keyboard indoors today. 🌧️"
    if wind_kmh is not None and wind_kmh >= 50:
        return "Stay sheltered from the strong winds. 🌬️"
    if temperature_c is not None and temperature_c >= 38:
        return "Perhaps touch some grass later. ☀️"
    if weather_code in {71, 73, 75, 77, 85}:
        return "Bundle up before heading out. ❄️"
    return "Go touch some grass, dev. 🌱"
