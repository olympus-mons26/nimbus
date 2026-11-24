"""Build a standalone Nimbus executable and a platform release artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
DIST = ROOT / "dist"
BUILD = ROOT / "build" / "pyinstaller"

sys.path.insert(0, str(SOURCE))
from nimbus import __version__  # noqa: E402


def default_artifact_name() -> str:
    system = {
        "Darwin": "macos",
        "Linux": "linux",
        "Windows": "windows",
    }.get(platform.system(), platform.system().lower())
    architecture = {
        "aarch64": "arm64",
        "amd64": "x86_64",
        "arm64": "arm64",
        "x86_64": "x86_64",
    }.get(platform.machine().lower(), platform.machine().lower())
    return f"nimbus-{system}-{architecture}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default=__version__, help="Version embedded in the executable.")
    parser.add_argument(
        "--artifact-name",
        default=default_artifact_name(),
        help="Base name for the archive or executable and its checksum.",
    )
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9._-]+", args.artifact_name):
        parser.error("--artifact-name may contain only letters, numbers, dots, underscores, and hyphens.")
    if not args.version or "\n" in args.version or "\r" in args.version:
        parser.error("--version must be a non-empty single line.")
    return args


def build_executable(version: str) -> Path:
    DIST.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    executable = DIST / ("wf.exe" if platform.system() == "Windows" else "wf")

    with tempfile.TemporaryDirectory(prefix="nimbus-build-") as temporary_directory:
        runtime_hook = Path(temporary_directory) / "version_hook.py"
        runtime_hook.write_text(
            f"import nimbus\nnimbus.__version__ = {json.dumps(version)}\n",
            encoding="utf-8",
        )
        command = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            "--onefile",
            "--name",
            "wf",
            "--paths",
            str(SOURCE),
            "--collect-all",
            "rich",
            "--runtime-hook",
            str(runtime_hook),
            "--distpath",
            str(DIST),
            "--workpath",
            str(BUILD / "work"),
            "--specpath",
            str(BUILD),
            str(SOURCE / "nimbus" / "__main__.py"),
        ]
        result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode:
        raise RuntimeError(f"PyInstaller failed with exit code {result.returncode}.")
    if not executable.is_file():
        raise RuntimeError(f"PyInstaller did not create the expected executable: {executable}")
    return executable


def package_artifact(executable: Path, artifact_name: str) -> Path:
    if platform.system() == "Windows":
        artifact = DIST / f"{artifact_name}.exe"
        shutil.copy2(executable, artifact)
        return artifact

    artifact = DIST / f"{artifact_name}.tar.gz"
    with tarfile.open(artifact, "w:gz") as archive:
        archive.add(executable, arcname="wf")
        archive.add(ROOT / "README.md", arcname="README.txt")
        archive.add(ROOT / "LICENSE", arcname="LICENSE")
    return artifact


def write_checksum(artifact: Path) -> Path:
    digest = hashlib.sha256()
    with artifact.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    checksum = artifact.with_name(f"{artifact.name}.sha256")
    checksum.write_text(f"{digest.hexdigest()}  {artifact.name}\n", encoding="utf-8")
    return checksum


def main() -> int:
    args = parse_args()
    try:
        executable = build_executable(args.version)
        artifact = package_artifact(executable, args.artifact_name)
        checksum = write_checksum(artifact)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 2

    print(f"Built executable: {executable.relative_to(ROOT)}")
    print(f"Release artifact: {artifact.relative_to(ROOT)}")
    print(f"SHA-256 checksum: {checksum.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
