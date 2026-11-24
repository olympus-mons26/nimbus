"""Build a standalone wf executable for the current runner platform."""

from __future__ import annotations

import shutil
import subprocess
import sys


def main() -> int:
    if shutil.which("pyinstaller") is None:
        print("PyInstaller is missing. Install build dependencies with: python -m pip install '.[build]'")
        return 2
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "--onefile",
        "--name",
        "wf",
        "--collect-all",
        "rich",
        "src/nimbus/__main__.py",
    ]
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
