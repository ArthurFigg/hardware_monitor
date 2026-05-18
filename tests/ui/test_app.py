from unittest.mock import patch

import pytest

from hardware.collector import DadosHardware
from hardware.thresholds import Status


@pytest.fixture(scope="module")
def monitor(raiz):
    dados_mock = DadosHardware(cpu=10.0, ram=20.0, disco=30.0)
    with patch("ui.app.coletar", return_value=dados_mock):
        from ui.app import AplicativoMonitor
        app = AplicativoMonitor(raiz)
        yield app
        app._rodando = False


def test_monitor_tem_tres_cards(monitor):
    assert set(monitor._cards.keys()) == {"cpu", "ram", "disco"}


def test_monitor_cards_titulos_corretos(monitor):
    assert monitor._cards["cpu"]._label_titulo.cget("text") == "CPU"
    assert monitor._cards["ram"]._label_titulo.cget("text") == "RAM"
    assert monitor._cards["disco"]._label_titulo.cget("text") == "Disco"


def test_monitor_atualizar_cards_todos_normal(monitor):
    dados = DadosHardware(cpu=10.0, ram=20.0, disco=30.0)
    monitor._atualizar_cards(dados)
    assert monitor._cards["cpu"].status_atual == Status.NORMAL
    assert monitor._cards["ram"].status_atual == Status.NORMAL
    assert monitor._cards["disco"].status_atual == Status.NORMAL


def test_monitor_atualizar_cards_cpu_atencao(monitor):
    dados = DadosHardware(cpu=70.0, ram=20.0, disco=30.0)
    monitor._atualizar_cards(dados)
    assert monitor._cards["cpu"].status_atual == Status.ATENCAO
    assert monitor._cards["ram"].status_atual == Status.NORMAL
