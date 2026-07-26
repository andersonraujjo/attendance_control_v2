from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Garante import `app.*` quando executado como script
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import flet as ft

from app.db.database import init_db
from app.ui.app import build_app


def main(page: ft.Page) -> None:
    init_db()
    build_app(page)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    ft.run(main)
