from unittest.mock import MagicMock, patch

import recursos
import ui.app
from hardware.collector import DadosHardware
from hardware.thresholds import Status


@patch("ui.app.coletar", return_value=DadosHardware(cpu=10.0, ram=20.0, disco=30.0))
def test_monitor_tem_quatro_cards(_, raiz):
    from ui.app import AplicativoMonitor

    app = AplicativoMonitor(raiz)
    app._rodando = False
    assert set(app._cards.keys()) == {"cpu", "ram", "disco", "temperatura"}


@patch("ui.app.coletar", return_value=DadosHardware(cpu=10.0, ram=20.0, disco=30.0))
def test_monitor_cards_titulos_corretos(_, raiz):
    from ui.app import AplicativoMonitor

    app = AplicativoMonitor(raiz)
    app._rodando = False
    assert app._cards["cpu"]._label_titulo.cget("text") == "CPU"
    assert app._cards["ram"]._label_titulo.cget("text") == "RAM"
    assert app._cards["disco"]._label_titulo.cget("text") == "Disco"
    assert app._cards["temperatura"]._label_titulo.cget("text") == "Temperatura"


@patch("ui.app.coletar", return_value=DadosHardware(cpu=10.0, ram=20.0, disco=30.0))
def test_monitor_atualizar_cards_todos_normal(_, raiz):
    from ui.app import AplicativoMonitor

    app = AplicativoMonitor(raiz)
    app._rodando = False
    app._atualizar_cards(DadosHardware(cpu=10.0, ram=20.0, disco=30.0))
    assert app._cards["cpu"].status_atual == Status.NORMAL
    assert app._cards["ram"].status_atual == Status.NORMAL
    assert app._cards["disco"].status_atual == Status.NORMAL


@patch("ui.app.coletar", return_value=DadosHardware(cpu=10.0, ram=20.0, disco=30.0))
def test_monitor_atualizar_cards_cpu_atencao(_, raiz):
    from ui.app import AplicativoMonitor

    app = AplicativoMonitor(raiz)
    app._rodando = False
    app._atualizar_cards(DadosHardware(cpu=70.0, ram=20.0, disco=30.0))
    assert app._cards["cpu"].status_atual == Status.ATENCAO
    assert app._cards["ram"].status_atual == Status.NORMAL


@patch("ui.app.coletar", return_value=DadosHardware(cpu=10.0, ram=20.0, disco=30.0))
def test_monitor_temperatura_normal_com_cpu_baixa(_, raiz):
    from ui.app import AplicativoMonitor

    app = AplicativoMonitor(raiz)
    app._rodando = False
    # cpu=40 → estimar_temperatura=55°C → NORMAL
    app._atualizar_cards(DadosHardware(cpu=40.0, ram=20.0, disco=30.0))
    assert app._cards["temperatura"].status_atual == Status.NORMAL


@patch("ui.app.coletar", return_value=DadosHardware(cpu=10.0, ram=20.0, disco=30.0))
def test_monitor_temperatura_alerta_com_cpu_alta(_, raiz):
    from ui.app import AplicativoMonitor

    app = AplicativoMonitor(raiz)
    app._rodando = False
    app._rastreadores["temperatura"] = MagicMock(
        atualizar=MagicMock(return_value=Status.ALERTA)
    )
    # cpu=100 → estimar_temperatura=85°C → ALERTA
    app._atualizar_cards(DadosHardware(cpu=100.0, ram=20.0, disco=30.0))
    assert app._cards["temperatura"].status_atual == Status.ALERTA


def _recurso_que_some(valor):
    """Recurso que declara pode_sumir e devolve o valor pedido (None = indisponível)."""
    return recursos.Recurso(
        nome="fantasma",
        rotulo="Fantasma",
        classificar=recursos.CPU.classificar,
        extrair=lambda _: valor,
        formatar_valor=recursos.CPU.formatar_valor,
        descricoes=recursos.CPU.descricoes,
        pode_sumir=True,
        notifica=False,
    )


@patch("ui.app.coletar", return_value=DadosHardware(cpu=10.0, ram=20.0, disco=30.0))
def test_recurso_indisponivel_some_da_tela(_, raiz):
    from ui.app import AplicativoMonitor

    with patch.object(ui.app, "RECURSOS", (_recurso_que_some(None),)):
        app = AplicativoMonitor(raiz)
        app._rodando = False
        app._atualizar_cards(DadosHardware(cpu=10.0, ram=20.0, disco=30.0))
        raiz.update_idletasks()
        assert app.cards_visiveis() == []


@patch("ui.app.coletar", return_value=DadosHardware(cpu=10.0, ram=20.0, disco=30.0))
def test_recurso_disponivel_aparece_na_tela(_, raiz):
    from ui.app import AplicativoMonitor

    with patch.object(ui.app, "RECURSOS", (_recurso_que_some(42.0),)):
        app = AplicativoMonitor(raiz)
        app._rodando = False
        app._atualizar_cards(DadosHardware(cpu=10.0, ram=20.0, disco=30.0))
        raiz.update_idletasks()
        assert app.cards_visiveis() == ["fantasma"]


@patch("ui.app.coletar", return_value=DadosHardware(cpu=10.0, ram=20.0, disco=30.0))
def test_recurso_indisponivel_fica_fora_do_pior_status(_, raiz):
    from ui.app import AplicativoMonitor

    with patch.object(ui.app, "RECURSOS", (_recurso_que_some(None),)):
        app = AplicativoMonitor(raiz)
        app._rodando = False
        app._atualizar_cards(DadosHardware(cpu=95.0, ram=20.0, disco=30.0))
        assert app.pior_status_atual == Status.NORMAL
