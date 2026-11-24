"""Small JSON response cache stored in the user's cache directory."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


def cache_dir() -> Path:
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Caches"
    else:
        root = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return root / "nimbus-weather"


class ResponseCache:
    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory or cache_dir()

    def _path(self, url: str, params: dict[str, Any]) -> Path:
        identity = json.dumps([url, params], sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(identity.encode()).hexdigest()
        return self.directory / f"{digest}.json"

    def read(self, url: str, params: dict[str, Any]) -> tuple[dict[str, Any], float] | None:
        path = self._path(url, params)
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            payload = record["payload"]
            timestamp = float(record["timestamp"])
            if isinstance(payload, dict):
                return payload, max(0.0, time.time() - timestamp)
        except (OSError, ValueError, KeyError, TypeError):
            return None
        return None

    def write(self, url: str, params: dict[str, Any], payload: dict[str, Any]) -> None:
        path = self._path(url, params)
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps({"timestamp": time.time(), "payload": payload}),
                encoding="utf-8",
            )
        except OSError:
            return
