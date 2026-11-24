import pytest

from nimbus.config import Settings, load_settings, save_settings, update_setting
from nimbus.errors import ConfigurationError


def test_settings_round_trip(tmp_path):
    path = tmp_path / "config.toml"
    settings = Settings(city="New York", unit="fahrenheit", days=5, aqi=True)

    save_settings(settings, path)

    assert load_settings(path) == settings


def test_invalid_setting_does_not_change_unit():
    settings = Settings()

    with pytest.raises(ConfigurationError, match="Unit must"):
        update_setting(settings, "unit", "kelvin")

    assert settings.unit == "celsius"


def test_malformed_toml_has_actionable_error(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("[general\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Cannot read configuration"):
        load_settings(path)


def test_non_string_unit_in_config_is_rejected(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("[general]\nunit = [1, 2]\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="unit must be"):
        load_settings(path)
