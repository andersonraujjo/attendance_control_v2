from __future__ import annotations

import flet as ft

from app.services.ponto_service import PontoService
from app.ui.theme import CARD_BG, MUTED, PRIMARY, SUCCESS, WARNING


class DashboardView:
    def __init__(self, page: ft.Page, service: PontoService):
        self.page = page
        self.service = service

        self.semana_value = ft.Text("0h", size=32, weight=ft.FontWeight.BOLD, color=PRIMARY)
        self.mes_value = ft.Text("0h", size=32, weight=ft.FontWeight.BOLD, color=SUCCESS)
        self.semana_periodo = ft.Text("", color=MUTED, size=12)
        self.mes_periodo = ft.Text("", color=MUTED, size=12)
        self.epicos_column = ft.Column(spacing=8, tight=True)

        self.root = self._build()
        self.refresh()

    def control(self) -> ft.Control:
        return self.root

    def _card(self, titulo: str, valor: ft.Text, sub: ft.Text) -> ft.Container:
        return ft.Container(
            bgcolor=CARD_BG,
            border_radius=12,
            padding=20,
            expand=True,
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text(titulo, color=MUTED, size=13),
                    valor,
                    sub,
                ],
            ),
        )

    def _build(self) -> ft.Control:
        return ft.Container(
            expand=True,
            padding=20,
            content=ft.ListView(
                expand=True,
                controls=[
                    ft.Text("Dashboard", size=22, weight=ft.FontWeight.BOLD),
                    ft.Text("Totais rápidos da semana, do mês e por épico.", color=MUTED, size=13),
                    ft.Container(height=8),
                    ft.Row(
                        spacing=12,
                        controls=[
                            self._card("Horas na semana atual", self.semana_value, self.semana_periodo),
                            self._card("Horas no mês atual", self.mes_value, self.mes_periodo),
                        ],
                    ),
                    ft.Container(height=12),
                    ft.Container(
                        bgcolor=CARD_BG,
                        border_radius=12,
                        padding=20,
                        content=ft.Column(
                            spacing=10,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("Por épico", size=16, weight=ft.FontWeight.W_600),
                                        ft.IconButton(
                                            icon=ft.Icons.REFRESH,
                                            tooltip="Atualizar",
                                            on_click=lambda e: self.refresh(),
                                        ),
                                    ],
                                ),
                                self.epicos_column,
                            ],
                        ),
                    ),
                ],
            ),
        )

    def refresh(self) -> None:
        totais = self.service.totais_dashboard()
        self.semana_value.value = f"{totais['semana']}h"
        self.mes_value.value = f"{totais['mes']}h"
        self.semana_periodo.value = (
            f"{totais['semana_inicio'].strftime('%d/%m')} → "
            f"{totais['semana_fim'].strftime('%d/%m/%Y')}"
        )
        self.mes_periodo.value = (
            f"{totais['mes_inicio'].strftime('%d/%m')} → "
            f"{totais['mes_fim'].strftime('%d/%m/%Y')}"
        )

        if totais["por_epico"]:
            self.epicos_column.controls = [
                ft.Container(
                    bgcolor="#161616",
                    border_radius=8,
                    padding=12,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(epico, expand=True),
                            ft.Text(f"{horas}h", color=WARNING, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                )
                for epico, horas in totais["por_epico"]
            ]
        else:
            self.epicos_column.controls = [
                ft.Text("Nenhum registro ainda.", color=MUTED)
            ]
        self.page.update()
