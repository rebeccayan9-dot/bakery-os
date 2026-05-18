"""Load and persist JSON state files."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("BAKERY_DATA", ROOT / "web" / "data"))


def _path(name: str) -> Path:
    return DATA_DIR / f"{name}.json"


def load(name: str) -> Any:
    with _path(name).open() as f:
        return json.load(f)


def save(name: str, value: Any) -> None:
    path = _path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(value, f, indent=2)
        f.write("\n")


def recipes() -> dict:
    return load("recipes")


def inventory() -> dict:
    return load("inventory")


def config() -> dict:
    return load("config")


def substitutions() -> dict:
    return load("substitutions")
