from __future__ import annotations

from datetime import date, datetime

from app.db.database import get_connection
from app.models.registro import Registro


class RegistroRepository:
    def inserir_muitos(self, registros: list[Registro]) -> list[int]:
        agora = datetime.now().isoformat(timespec="seconds")
        ids: list[int] = []
        conn = get_connection()
        try:
            for reg in registros:
                cur = conn.execute(
                    """
                    INSERT INTO registros
                        (data, horas, epico, entrada, saida, total_horas, criado_em)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        reg.data_iso(),
                        reg.horas,
                        reg.epico,
                        reg.entrada,
                        reg.saida,
                        reg.total_horas,
                        agora,
                    ),
                )
                ids.append(cur.lastrowid)
            conn.commit()
        finally:
            conn.close()
        return ids

    def listar_todos(self) -> list[Registro]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM registros ORDER BY data ASC, id ASC"
            ).fetchall()
            return [self._row_to_registro(r) for r in rows]
        finally:
            conn.close()

    def buscar_por_id(self, registro_id: int) -> Registro | None:
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM registros WHERE id = ?", (registro_id,)
            ).fetchone()
            return self._row_to_registro(row) if row else None
        finally:
            conn.close()

    def atualizar(self, registro: Registro) -> None:
        if registro.id is None:
            raise ValueError("Registro sem id não pode ser atualizado")
        conn = get_connection()
        try:
            conn.execute(
                """
                UPDATE registros
                SET data = ?, horas = ?, epico = ?, entrada = ?, saida = ?, total_horas = ?
                WHERE id = ?
                """,
                (
                    registro.data_iso(),
                    registro.horas,
                    registro.epico,
                    registro.entrada,
                    registro.saida,
                    registro.total_horas,
                    registro.id,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def excluir(self, registro_id: int) -> None:
        conn = get_connection()
        try:
            conn.execute("DELETE FROM registros WHERE id = ?", (registro_id,))
            conn.commit()
        finally:
            conn.close()

    def datas_com_epico(self, epico: str, datas: list[date]) -> list[date]:
        """Retorna datas que já têm registro para o mesmo épico (case-insensitive)."""
        if not datas:
            return []
        placeholders = ",".join("?" for _ in datas)
        params = [epico.strip().lower(), *[d.isoformat() for d in datas]]
        conn = get_connection()
        try:
            rows = conn.execute(
                f"""
                SELECT data FROM registros
                WHERE LOWER(TRIM(epico)) = ? AND data IN ({placeholders})
                ORDER BY data
                """,
                params,
            ).fetchall()
            return [date.fromisoformat(r["data"]) for r in rows]
        finally:
            conn.close()

    def excluir_todos(self) -> int:
        """Apaga todos os registros do banco. Não mexe em arquivos de export."""
        conn = get_connection()
        try:
            cur = conn.execute("SELECT COUNT(*) AS total FROM registros")
            total = int(cur.fetchone()["total"])
            conn.execute("DELETE FROM registros")
            conn.execute("DELETE FROM sqlite_sequence WHERE name = 'registros'")
            conn.commit()
            return total
        finally:
            conn.close()

    def somar_horas_entre(self, inicio: date, fim: date) -> int:
        conn = get_connection()
        try:
            row = conn.execute(
                """
                SELECT COALESCE(SUM(horas), 0) AS total
                FROM registros
                WHERE data BETWEEN ? AND ?
                """,
                (inicio.isoformat(), fim.isoformat()),
            ).fetchone()
            return int(row["total"])
        finally:
            conn.close()

    def somar_por_epico(self) -> list[tuple[str, int]]:
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT epico, SUM(horas) AS total
                FROM registros
                GROUP BY epico
                ORDER BY total DESC, epico ASC
                """
            ).fetchall()
            return [(r["epico"], int(r["total"])) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def _row_to_registro(row) -> Registro:
        return Registro(
            id=row["id"],
            data=date.fromisoformat(row["data"]),
            horas=row["horas"],
            epico=row["epico"],
            entrada=row["entrada"],
            saida=row["saida"],
            total_horas=row["total_horas"],
            criado_em=row["criado_em"],
        )
