from __future__ import annotations

import calendar
from datetime import date
from typing import Callable

import flet as ft

from app.models.registro import Registro
from app.services.ponto_service import PontoService
from app.ui.theme import CARD_BG, MUTED, PRIMARY, SUCCESS, WARNING


class LancamentoView:
    def __init__(
        self,
        page: ft.Page,
        service: PontoService,
        on_saved: Callable[[], None] | None = None,
    ):
        self.page = page
        self.service = service
        self.on_saved = on_saved

        self.selected_dates: set[date] = set()
        self.calendar_month = date.today().replace(day=1)
        self._last_submit_key: tuple | None = None
        self._saving = False

        self.horas_field = ft.TextField(
            label="Horas totais",
            hint_text="Ex: 40",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=180,
            value="40",
        )
        self.epico_field = ft.TextField(
            label="Épico",
            hint_text="Ex: Épico integração UY3",
            expand=True,
        )
        self.status_text = ft.Text("", color=WARNING, size=13)
        self.selected_label = ft.Text("Nenhuma data selecionada", color=MUTED, size=13)
        self.preview_column = ft.Column(spacing=4, tight=True)
        self.calendar_grid = ft.Column(spacing=6)
        self.month_title = ft.Text("", size=16, weight=ft.FontWeight.W_600)
        self.btn_confirmar = ft.Button(
            content="Confirmar lançamento",
            icon=ft.Icons.CHECK_CIRCLE,
            bgcolor=SUCCESS,
            color=ft.Colors.BLACK,
            on_click=self._confirmar,
        )

        self.root = self._build()
        self._rebuild_calendar()

    def control(self) -> ft.Control:
        return self.root

    def _build(self) -> ft.Control:
        form = ft.Container(
            bgcolor=CARD_BG,
            border_radius=12,
            padding=20,
            content=ft.Column(
                spacing=14,
                controls=[
                    ft.Text("Novo lançamento", size=22, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Informe as horas, o épico e selecione as datas. "
                        "A divisão será igualitária (resto nos últimos dias).",
                        color=MUTED,
                        size=13,
                    ),
                    ft.Row(
                        controls=[self.horas_field, self.epico_field],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    ft.Row(
                        spacing=8,
                        wrap=True,
                        controls=[
                            ft.OutlinedButton(
                                content="Esta semana (úteis)",
                                icon=ft.Icons.DATE_RANGE,
                                on_click=self._select_uteis,
                            ),
                            ft.OutlinedButton(
                                content="Semana completa",
                                icon=ft.Icons.CALENDAR_VIEW_WEEK,
                                on_click=self._select_completa,
                            ),
                            ft.OutlinedButton(
                                content="Limpar datas",
                                icon=ft.Icons.CLEAR_ALL,
                                on_click=self._clear_dates,
                            ),
                            ft.OutlinedButton(
                                content="Limpar tudo",
                                icon=ft.Icons.RESTART_ALT,
                                on_click=self._limpar_tudo,
                            ),
                        ],
                    ),
                    self.selected_label,
                    self._calendar_card(),
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Button(
                                content="Gerar preview",
                                icon=ft.Icons.PREVIEW,
                                bgcolor=PRIMARY,
                                on_click=self._gerar_preview,
                            ),
                            self.btn_confirmar,
                        ],
                    ),
                    self.status_text,
                    ft.Text("Preview", size=16, weight=ft.FontWeight.W_600),
                    self.preview_column,
                ],
            ),
        )
        return ft.Container(
            expand=True,
            padding=20,
            content=ft.ListView(expand=True, controls=[form]),
        )

    def _calendar_card(self) -> ft.Container:
        return ft.Container(
            bgcolor="#161616",
            border_radius=10,
            padding=12,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_LEFT,
                                on_click=self._prev_month,
                            ),
                            self.month_title,
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_RIGHT,
                                on_click=self._next_month,
                            ),
                        ],
                    ),
                    self.calendar_grid,
                ],
            ),
        )

    def _month_title_text(self) -> str:
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
        ]
        return f"{meses[self.calendar_month.month - 1]} {self.calendar_month.year}"

    def _rebuild_calendar(self) -> None:
        year = self.calendar_month.year
        month = self.calendar_month.month
        cal = calendar.Calendar(firstweekday=0)
        self.month_title.value = self._month_title_text()

        header = ft.Row(
            spacing=4,
            controls=[
                ft.Container(
                    width=42,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(d, size=11, color=MUTED),
                )
                for d in ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
            ],
        )

        weeks: list[ft.Control] = [header]
        for week in cal.monthdatescalendar(year, month):
            cells = []
            for d in week:
                in_month = d.month == month
                selected = d in self.selected_dates

                def make_handler(day: date):
                    return lambda e: self._toggle_date(day)

                cells.append(
                    ft.Container(
                        width=42,
                        height=36,
                        border_radius=8,
                        alignment=ft.Alignment.CENTER,
                        bgcolor=PRIMARY if selected else None,
                        opacity=1.0 if in_month else 0.35,
                        content=ft.Text(
                            str(d.day),
                            size=13,
                            weight=ft.FontWeight.BOLD if selected else None,
                            color=ft.Colors.BLACK if selected else ft.Colors.WHITE,
                        ),
                        on_click=make_handler(d),
                        ink=True,
                    )
                )
            weeks.append(ft.Row(spacing=4, controls=cells))

        self.calendar_grid.controls = weeks
        self._refresh_selected_label()

    def _toggle_date(self, day: date) -> None:
        if day in self.selected_dates:
            self.selected_dates.remove(day)
        else:
            self.selected_dates.add(day)
        self._rebuild_calendar()
        self.page.update()

    def _prev_month(self, _e=None) -> None:
        y, m = self.calendar_month.year, self.calendar_month.month
        self.calendar_month = date(y - 1, 12, 1) if m == 1 else date(y, m - 1, 1)
        self._rebuild_calendar()
        self.page.update()

    def _next_month(self, _e=None) -> None:
        y, m = self.calendar_month.year, self.calendar_month.month
        self.calendar_month = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
        self._rebuild_calendar()
        self.page.update()

    def _select_uteis(self, _e=None) -> None:
        self.selected_dates = set(self.service.datas_semana_uteis())
        self.calendar_month = min(self.selected_dates).replace(day=1)
        self._rebuild_calendar()
        self.page.update()

    def _select_completa(self, _e=None) -> None:
        self.selected_dates = set(self.service.datas_semana_completa())
        self.calendar_month = min(self.selected_dates).replace(day=1)
        self._rebuild_calendar()
        self.page.update()

    def _clear_dates(self, _e=None) -> None:
        self.selected_dates.clear()
        self.preview_column.controls.clear()
        self._rebuild_calendar()
        self.page.update()

    def _limpar_tudo(self, _e=None) -> None:
        self._last_submit_key = None
        self._reset_formulario()
        self.page.update()

    def _refresh_selected_label(self) -> None:
        if not self.selected_dates:
            self.selected_label.value = "Nenhuma data selecionada"
            return
        ordenadas = sorted(self.selected_dates)
        textos = [d.strftime("%d/%m") for d in ordenadas]
        self.selected_label.value = f"{len(ordenadas)} data(s): " + ", ".join(textos)

    def _parse_horas(self) -> int:
        raw = (self.horas_field.value or "").strip()
        if not raw.isdigit():
            raise ValueError("Horas totais deve ser um número inteiro.")
        return int(raw)

    def _submit_key(self, total: int, epico: str, datas: set[date]) -> tuple:
        return (total, epico.strip().lower(), tuple(sorted(datas)))

    def _reset_formulario(self, mensagem_sucesso: str | None = None) -> None:
        """Volta a tela ao estado inicial limpo."""
        self.horas_field.value = "40"
        self.epico_field.value = ""
        self.selected_dates.clear()
        self.preview_column.controls.clear()
        self.calendar_month = date.today().replace(day=1)
        self._rebuild_calendar()
        if mensagem_sucesso:
            self.status_text.value = mensagem_sucesso
            self.status_text.color = SUCCESS
        else:
            self.status_text.value = ""

    def _gerar_preview(self, _e=None) -> None:
        try:
            total = self._parse_horas()
            epico = (self.epico_field.value or "").strip()
            preview = self.service.gerar_preview(total, epico, list(self.selected_dates))
            self.preview_column.controls = [
                ft.Text(
                    f"{p.data.strftime('%d/%m/%Y')}  →  {p.horas}h  "
                    f"(08:00 → {Registro.calcular_saida(p.horas)[:5]})",
                    size=13,
                )
                for p in preview
            ]
            self.status_text.value = f"Preview ok — soma {sum(p.horas for p in preview)}h"
            self.status_text.color = SUCCESS
        except ValueError as err:
            self.status_text.value = str(err)
            self.status_text.color = WARNING
            self.preview_column.controls.clear()
        self.page.update()

    def _confirmar(self, _e=None) -> None:
        if self._saving:
            return

        try:
            total = self._parse_horas()
            epico = (self.epico_field.value or "").strip()
            datas = set(self.selected_dates)
            chave = self._submit_key(total, epico, datas)

            if self._last_submit_key == chave:
                raise ValueError(
                    "Este lançamento já foi confirmado agora há pouco "
                    "(mesmo total, épico e datas). Altere algo para enviar de novo."
                )

            self._saving = True
            self.btn_confirmar.disabled = True
            self.page.update()

            regs = self.service.confirmar_lancamento(total, epico, list(datas))
            self._last_submit_key = chave
            msg = f"{len(regs)} registro(s) salvos com sucesso."
            self.status_text.value = msg
            self.status_text.color = SUCCESS
            self.page.show_dialog(ft.SnackBar(content=ft.Text(msg), bgcolor=SUCCESS))
            if self.on_saved:
                self.on_saved()
        except ValueError as err:
            self.status_text.value = str(err)
            self.status_text.color = WARNING
            self.page.show_dialog(ft.SnackBar(content=ft.Text(str(err)), bgcolor=WARNING))
        except Exception as err:
            self.status_text.value = f"Erro ao salvar: {err}"
            self.status_text.color = ft.Colors.RED_400
        finally:
            self._saving = False
            self.btn_confirmar.disabled = False
            self.page.update()
