from __future__ import annotations

import os
import subprocess
from datetime import date
from typing import Callable

import flet as ft

from app.paths import exports_dir
from app.services.export_service import ExportService
from app.services.ponto_service import PontoService
from app.ui.theme import CARD_BG, DANGER, MUTED, PRIMARY, SUCCESS, WARNING


class ListaView:
    def __init__(
        self,
        page: ft.Page,
        service: PontoService,
        export_service: ExportService,
        on_changed: Callable[[], None] | None = None,
    ):
        self.page = page
        self.service = service
        self.export_service = export_service
        self.on_changed = on_changed

        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Data")),
                ft.DataColumn(ft.Text("Horas")),
                ft.DataColumn(ft.Text("Entrada")),
                ft.DataColumn(ft.Text("Saída")),
                ft.DataColumn(ft.Text("Épico")),
                ft.DataColumn(ft.Text("Ações")),
            ],
            rows=[],
            heading_row_color="#111111",
            border=ft.Border(
                top=ft.BorderSide(1, "#333333"),
                right=ft.BorderSide(1, "#333333"),
                bottom=ft.BorderSide(1, "#333333"),
                left=ft.BorderSide(1, "#333333"),
            ),
            column_spacing=18,
        )
        self.status_text = ft.Text("", color=MUTED, size=13)
        self.root = self._build()
        self.refresh()

    def control(self) -> ft.Control:
        return self.root

    def _build(self) -> ft.Control:
        header = ft.Container(
            bgcolor=CARD_BG,
            border_radius=12,
            padding=20,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Registros", size=22, weight=ft.FontWeight.BOLD),
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.OutlinedButton(
                                        content="Exportar CSV",
                                        icon=ft.Icons.TABLE_VIEW,
                                        on_click=self._export_csv,
                                    ),
                                    ft.Button(
                                        content="Exportar Excel",
                                        icon=ft.Icons.GRID_ON,
                                        bgcolor=PRIMARY,
                                        on_click=self._export_excel,
                                    ),
                                    ft.OutlinedButton(
                                        content="Abrir pasta",
                                        icon=ft.Icons.FOLDER_OPEN,
                                        on_click=self._abrir_pasta_exports,
                                    ),
                                    ft.Button(
                                        content="Excluir todos",
                                        icon=ft.Icons.DELETE_SWEEP,
                                        bgcolor=DANGER,
                                        on_click=self._confirmar_exclusao_todos,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.REFRESH,
                                        tooltip="Atualizar",
                                        on_click=lambda e: self.refresh(),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Text(
                        f"Exportações: {exports_dir()}",
                        color=MUTED,
                        size=12,
                        selectable=True,
                    ),
                    self.status_text,
                    ft.Row(
                        scroll=ft.ScrollMode.AUTO,
                        controls=[self.table],
                    ),
                ],
            ),
        )
        return ft.Container(
            expand=True,
            padding=20,
            content=ft.ListView(expand=True, controls=[header]),
        )

    def refresh(self) -> None:
        registros = self.service.listar()
        self.table.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(r.id))),
                    ft.DataCell(ft.Text(r.data_br())),
                    ft.DataCell(ft.Text(f"{r.horas}h")),
                    ft.DataCell(ft.Text(r.entrada)),
                    ft.DataCell(ft.Text(r.saida)),
                    ft.DataCell(ft.Text(r.epico, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)),
                    ft.DataCell(
                        ft.Row(
                            spacing=0,
                            tight=True,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_color=PRIMARY,
                                    tooltip="Editar",
                                    data=r.id,
                                    on_click=self._abrir_edicao,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=DANGER,
                                    tooltip="Excluir",
                                    data=r.id,
                                    on_click=self._confirmar_exclusao,
                                ),
                            ],
                        )
                    ),
                ]
            )
            for r in registros
        ]
        total = sum(r.horas for r in registros)
        self.status_text.value = f"{len(registros)} registro(s) — {total}h no total"
        self.page.update()

    def _abrir_pasta_exports(self, _e=None) -> None:
        pasta = exports_dir()
        try:
            os.startfile(pasta)  # type: ignore[attr-defined]
        except Exception:
            subprocess.Popen(["explorer", str(pasta)])

    def _export_csv(self, _e=None) -> None:
        try:
            path = self.export_service.exportar_csv()
            msg = f"CSV gerado em:\n{path}"
            self.status_text.value = msg
            self.status_text.color = SUCCESS
            self.page.show_dialog(ft.SnackBar(content=ft.Text(msg), bgcolor=SUCCESS))
            self._abrir_pasta_exports()
        except Exception as err:
            self.status_text.value = f"Erro no CSV: {err}"
            self.status_text.color = DANGER
        self.page.update()

    def _export_excel(self, _e=None) -> None:
        try:
            path = self.export_service.exportar_excel()
            msg = f"Excel gerado em:\n{path}"
            self.status_text.value = msg
            self.status_text.color = SUCCESS
            self.page.show_dialog(ft.SnackBar(content=ft.Text(msg), bgcolor=SUCCESS))
            self._abrir_pasta_exports()
        except Exception as err:
            self.status_text.value = f"Erro no Excel: {err}"
            self.status_text.color = DANGER
        self.page.update()

    def _confirmar_exclusao(self, e: ft.ControlEvent) -> None:
        registro_id = e.control.data

        def excluir(_ev=None):
            self.service.excluir(registro_id)
            self.page.pop_dialog()
            self.refresh()
            if self.on_changed:
                self.on_changed()
            self.page.show_dialog(
                ft.SnackBar(content=ft.Text(f"Registro #{registro_id} excluído"), bgcolor=WARNING)
            )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Excluir registro"),
            content=ft.Text(f"Confirma excluir o registro #{registro_id}?"),
            actions=[
                ft.TextButton(content="Cancelar", on_click=lambda ev: self.page.pop_dialog()),
                ft.Button(content="Excluir", bgcolor=DANGER, on_click=excluir),
            ],
        )
        self.page.show_dialog(dialog)

    def _confirmar_exclusao_todos(self, _e=None) -> None:
        total = len(self.service.listar())
        if total == 0:
            self.page.show_dialog(
                ft.SnackBar(content=ft.Text("Não há registros para excluir."), bgcolor=MUTED)
            )
            return

        def excluir_todos(_ev=None):
            apagados = self.service.excluir_todos()
            self.page.pop_dialog()
            self.refresh()
            if self.on_changed:
                self.on_changed()
            msg = (
                f"{apagados} registro(s) apagados do banco. "
                "Arquivos em exports/ foram mantidos."
            )
            self.status_text.value = msg
            self.status_text.color = WARNING
            self.page.show_dialog(ft.SnackBar(content=ft.Text(msg), bgcolor=WARNING))
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Excluir todos os registros"),
            content=ft.Text(
                f"Isso vai apagar os {total} registro(s) da lista e do banco.\n"
                "Os relatórios CSV/Excel já gerados em exports/ NÃO serão apagados.\n\n"
                "Tem certeza?"
            ),
            actions=[
                ft.TextButton(content="Cancelar", on_click=lambda ev: self.page.pop_dialog()),
                ft.Button(
                    content="Excluir todos",
                    bgcolor=DANGER,
                    on_click=excluir_todos,
                ),
            ],
        )
        self.page.show_dialog(dialog)

    def _abrir_edicao(self, e: ft.ControlEvent) -> None:
        registro_id = e.control.data
        atual = next((r for r in self.service.listar() if r.id == registro_id), None)
        if not atual:
            return

        data_field = ft.TextField(label="Data (dd/mm/aaaa)", value=atual.data_br())
        horas_field = ft.TextField(label="Horas", value=str(atual.horas), keyboard_type=ft.KeyboardType.NUMBER)
        epico_field = ft.TextField(label="Épico", value=atual.epico)

        def salvar(_ev=None):
            try:
                partes = (data_field.value or "").strip().split("/")
                if len(partes) != 3:
                    raise ValueError("Data inválida. Use dd/mm/aaaa.")
                d = date(int(partes[2]), int(partes[1]), int(partes[0]))
                horas = int((horas_field.value or "").strip())
                self.service.atualizar_registro(registro_id, d, horas, epico_field.value or "")
                self.page.pop_dialog()
                self.refresh()
                if self.on_changed:
                    self.on_changed()
                self.page.show_dialog(
                    ft.SnackBar(content=ft.Text("Registro atualizado"), bgcolor=SUCCESS)
                )
            except Exception as err:
                self.page.show_dialog(
                    ft.SnackBar(content=ft.Text(str(err)), bgcolor=WARNING)
                )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Editar #{registro_id}"),
            content=ft.Column(
                tight=True,
                spacing=10,
                width=360,
                controls=[data_field, horas_field, epico_field],
            ),
            actions=[
                ft.TextButton(content="Cancelar", on_click=lambda ev: self.page.pop_dialog()),
                ft.Button(content="Salvar", bgcolor=PRIMARY, on_click=salvar),
            ],
        )
        self.page.show_dialog(dialog)
