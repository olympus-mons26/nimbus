import pytest

from nimbus.errors import UsageError
from nimbus.main import _forecast_parser, main


def test_flags_are_order_independent_and_compact_days_parse():
    parsed = _forecast_parser().parse_args(["-d5", "New", "York", "-f", "-h", "-aqi"])

    assert parsed.city == ["New", "York"]
    assert parsed.days == 5
    assert parsed.unit == "fahrenheit"
    assert parsed.hourly
    assert parsed.aqi


def test_temperature_units_are_mutually_exclusive():
    with pytest.raises(UsageError):
        _forecast_parser().parse_args(["-c", "-f", "London"])


def test_bare_day_flag_uses_three_days():
    assert _forecast_parser().parse_args(["London", "-d"]).days == 3


def test_wh_help_includes_uninstall_instructions(capsys):
    assert main(["wh"]) == 0

    output = capsys.readouterr().out
    assert "brew uninstall olympus-mons26/tap/nimbus" in output
    assert "python -m pip uninstall nimbus-weather-cli" in output
