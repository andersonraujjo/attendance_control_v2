import flet as ft

APP_TITLE = "Ponto Eletrônico v.2"

PRIMARY = ft.Colors.TEAL_400
CARD_BG = "#1E1E1E"
MUTED = ft.Colors.GREY_400
SUCCESS = ft.Colors.GREEN_400
DANGER = ft.Colors.RED_400
WARNING = ft.Colors.AMBER_400


def configure_page(page: ft.Page) -> None:
    page.title = APP_TITLE
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 980
    page.window.height = 720
    page.window.min_width = 820
    page.window.min_height = 600
