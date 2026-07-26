from __future__ import annotations

import sqlite3
from pathlib import Path

from app.paths import data_dir

DB_NAME = "ponto_v2.db"


def db_path() -> Path:
    return data_dir() / DB_NAME


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                horas INTEGER NOT NULL,
                epico TEXT NOT NULL,
                entrada TEXT NOT NULL,
                saida TEXT NOT NULL,
                total_horas TEXT NOT NULL,
                criado_em TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_registros_data ON registros(data)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_registros_epico ON registros(epico)")
        conn.commit()
    finally:
        conn.close()
