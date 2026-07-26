from __future__ import annotations

from datetime import date, timedelta

from app.models.registro import PreviewDia, Registro
from app.repository.registro_repo import RegistroRepository


class PontoService:
    def __init__(self, repo: RegistroRepository | None = None):
        self.repo = repo or RegistroRepository()

    @staticmethod
    def dividir_horas(total_horas: int, datas: list[date]) -> list[PreviewDia]:
        if total_horas <= 0:
            raise ValueError("Informe uma quantidade de horas maior que zero.")
        if not datas:
            raise ValueError("Selecione ao menos uma data.")

        datas_ordenadas = sorted(set(datas))
        n = len(datas_ordenadas)
        base, resto = divmod(total_horas, n)

        preview: list[PreviewDia] = []
        for i, d in enumerate(datas_ordenadas):
            # Resto vai para os últimos dias
            horas = base + (1 if i >= n - resto else 0)
            preview.append(PreviewDia(data=d, horas=horas))
        return preview

    @staticmethod
    def datas_semana_uteis(referencia: date | None = None) -> list[date]:
        """Segunda a sexta da semana da data de referência."""
        ref = referencia or date.today()
        segunda = ref - timedelta(days=ref.weekday())
        return [segunda + timedelta(days=i) for i in range(5)]

    @staticmethod
    def datas_semana_completa(referencia: date | None = None) -> list[date]:
        """Segunda a domingo da semana da data de referência."""
        ref = referencia or date.today()
        segunda = ref - timedelta(days=ref.weekday())
        return [segunda + timedelta(days=i) for i in range(7)]

    def gerar_preview(
        self, total_horas: int, epico: str, datas: list[date]
    ) -> list[PreviewDia]:
        if not epico.strip():
            raise ValueError("Informe o épico.")
        return self.dividir_horas(total_horas, datas)

    def confirmar_lancamento(
        self, total_horas: int, epico: str, datas: list[date]
    ) -> list[Registro]:
        preview = self.gerar_preview(total_horas, epico, datas)
        conflitos = self.repo.datas_com_epico(epico, [p.data for p in preview])
        if conflitos:
            datas_br = ", ".join(d.strftime("%d/%m/%Y") for d in conflitos)
            raise ValueError(
                "Já existem registros com este épico nestas datas: "
                f"{datas_br}. Altere o épico/datas ou exclua os registros anteriores."
            )
        registros = [
            Registro.from_lancamento(p.data, p.horas, epico) for p in preview
        ]
        ids = self.repo.inserir_muitos(registros)
        for reg, reg_id in zip(registros, ids):
            reg.id = reg_id
        return registros

    def listar(self) -> list[Registro]:
        return self.repo.listar_todos()

    def atualizar_registro(
        self,
        registro_id: int,
        data: date,
        horas: int,
        epico: str,
    ) -> Registro:
        if horas <= 0:
            raise ValueError("Horas devem ser maiores que zero.")
        if not epico.strip():
            raise ValueError("Informe o épico.")

        atualizado = Registro.from_lancamento(data, horas, epico)
        atualizado.id = registro_id
        self.repo.atualizar(atualizado)
        return atualizado

    def excluir(self, registro_id: int) -> None:
        self.repo.excluir(registro_id)

    def excluir_todos(self) -> int:
        """Limpa a tabela de registros. Relatórios já gerados em exports/ permanecem."""
        return self.repo.excluir_todos()

    def totais_dashboard(self, referencia: date | None = None) -> dict:
        ref = referencia or date.today()
        segunda = ref - timedelta(days=ref.weekday())
        domingo = segunda + timedelta(days=6)
        inicio_mes = ref.replace(day=1)
        if ref.month == 12:
            fim_mes = ref.replace(year=ref.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            fim_mes = ref.replace(month=ref.month + 1, day=1) - timedelta(days=1)

        return {
            "semana": self.repo.somar_horas_entre(segunda, domingo),
            "mes": self.repo.somar_horas_entre(inicio_mes, fim_mes),
            "por_epico": self.repo.somar_por_epico(),
            "semana_inicio": segunda,
            "semana_fim": domingo,
            "mes_inicio": inicio_mes,
            "mes_fim": fim_mes,
        }
