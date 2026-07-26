from datetime import date

from app.services.ponto_service import PontoService


def test_divisao_igual_com_resto_nos_ultimos_dias():
    datas = [date(2026, 6, 22 + i) for i in range(7)]
    preview = PontoService.dividir_horas(40, datas)
    horas = [p.horas for p in preview]
    assert sum(horas) == 40
    assert horas == [5, 5, 6, 6, 6, 6, 6]


def test_divisao_cinco_dias_exata():
    datas = [date(2026, 6, 22 + i) for i in range(5)]
    preview = PontoService.dividir_horas(40, datas)
    assert [p.horas for p in preview] == [8, 8, 8, 8, 8]


def test_entrada_saida_geradas():
    from app.models.registro import Registro

    reg = Registro.from_lancamento(date(2026, 6, 22), 8, "Épico teste")
    assert reg.entrada == "08:00:00"
    assert reg.saida == "16:00:00"
    assert reg.total_horas == "8:00:00"
