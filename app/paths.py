from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    """Pasta base do app (projeto em dev; pasta do .exe quando empacotado)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def data_dir() -> Path:
    path = app_root() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def exports_dir() -> Path:
    path = app_root() / "exports"
    path.mkdir(parents=True, exist_ok=True)
    return path
