"""Entrypoint para desenvolvimento e empacote (.exe)."""
from __future__ import annotations

import asyncio
import sys

import flet as ft

from app.main import main

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    ft.run(main)
