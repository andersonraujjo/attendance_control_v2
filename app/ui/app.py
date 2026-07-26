from __future__ import annotations

import flet as ft

from app.services.export_service import ExportService
from app.services.ponto_service import PontoService
from app.ui.dashboard import DashboardView
from app.ui.lancamento import LancamentoView
from app.ui.lista import ListaView
from app.ui.theme import APP_TITLE, PRIMARY, configure_page


def build_app(page: ft.Page) -> None:
    configure_page(page)

    service = PontoService()
    export_service = ExportService()

    body = ft.Container(expand=True)

    def on_data_changed() -> None:
        lista.refresh()
        dashboard.refresh()

    lancamento = LancamentoView(page, service, on_saved=on_data_changed)
    lista = ListaView(page, service, export_service, on_changed=on_data_changed)
    dashboard = DashboardView(page, service)

    views = [lancamento.control(), lista.control(), dashboard.control()]

    def switch_tab(index: int) -> None:
        body.content = views[index]
        if index == 1:
            lista.refresh()
        elif index == 2:
            dashboard.refresh()
        page.update()

    def on_nav_change(e: ft.ControlEvent) -> None:
        switch_tab(e.control.selected_index)

    page.appbar = ft.AppBar(
        title=ft.Text(APP_TITLE, weight=ft.FontWeight.BOLD),
        bgcolor="#121212",
        center_title=False,
    )
    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                selected_icon=ft.Icons.ADD_CIRCLE,
                label="Lançar",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.LIST_ALT_OUTLINED,
                selected_icon=ft.Icons.LIST_ALT,
                label="Registros",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.INSIGHTS_OUTLINED,
                selected_icon=ft.Icons.INSIGHTS,
                label="Dashboard",
            ),
        ],
        bgcolor="#121212",
        indicator_color=PRIMARY,
    )

    body.content = views[0]
    page.add(body)
