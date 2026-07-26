from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta


@dataclass
class PreviewDia:
    data: date
    horas: int


@dataclass
class Registro:
    id: int | None
    data: date
    horas: int
    epico: str
    entrada: str
    saida: str
    total_horas: str
    criado_em: str | None = None

    def data_br(self) -> str:
        return self.data.strftime("%d/%m/%Y")

    def data_iso(self) -> str:
        return self.data.isoformat()

    @staticmethod
    def calcular_saida(horas: int, entrada: str = "08:00:00") -> str:
        base = datetime.strptime(entrada, "%H:%M:%S")
        fim = base + timedelta(hours=horas)
        return fim.strftime("%H:%M:%S")

    @staticmethod
    def formatar_total_horas(horas: int) -> str:
        return f"{horas}:00:00"

    @classmethod
    def from_lancamento(
        cls,
        data: date,
        horas: int,
        epico: str,
        entrada: str = "08:00:00",
    ) -> Registro:
        return cls(
            id=None,
            data=data,
            horas=horas,
            epico=epico.strip(),
            entrada=entrada,
            saida=cls.calcular_saida(horas, entrada),
            total_horas=cls.formatar_total_horas(horas),
        )
