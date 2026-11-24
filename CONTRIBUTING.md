# Contributing

Thanks for helping improve Nimbus Weather CLI.

1. Use Python 3.11 or newer.
2. Install development dependencies with `python -m pip install -e ".[test]"`.
3. Add or update focused tests for behavior changes.
4. Run `pytest` before opening a pull request.
5. Keep API responses and location data out of committed test fixtures unless they are sanitized and necessary.

Use the existing project style, keep errors actionable, and do not add a paid API or commit credentials. Changes involving Open-Meteo should preserve attribution and comply with its current usage terms.
