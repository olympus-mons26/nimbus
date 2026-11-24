from nimbus.main import _app_info


def test_appinfo_license_is_available_from_installed_package(capsys):
    assert _app_info(["--license"]) == 0
    output = capsys.readouterr().out

    assert "MIT License" in output
    assert "Copyright (c) 2026 olympus-mons26" in output
