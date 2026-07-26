from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from app.paths import exports_dir
from app.repository.registro_repo import RegistroRepository


class ExportService:
    def __init__(self, repo: RegistroRepository | None = None):
        self.repo = repo or RegistroRepository()

    def _dataframe_v1(self) -> pd.DataFrame:
        registros = self.repo.listar_todos()
        # Ordem cronológica no arquivo (mais antigo primeiro)
        registros = sorted(registros, key=lambda r: (r.data, r.id or 0))
        rows = [
            {
                "id": r.id,
                "data": r.data_br(),
                "entrada": r.entrada,
                "saida": r.saida,
                "total_horas": r.total_horas,
                "comentario": r.epico,
            }
            for r in registros
        ]
        return pd.DataFrame(
            rows,
            columns=["id", "data", "entrada", "saida", "total_horas", "comentario"],
        )

    def exportar_csv(self) -> Path:
        ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        path = exports_dir() / f"relatorio_ponto_{ts}.csv"
        self._dataframe_v1().to_csv(path, index=False, sep=";", encoding="utf-8-sig")
        return path.resolve()

    def exportar_excel(self) -> Path:
        ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        path = exports_dir() / f"relatorio_ponto_{ts}.xlsx"
        self._dataframe_v1().to_excel(path, index=False)
        return path.resolve()
