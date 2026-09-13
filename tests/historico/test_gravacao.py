"""Testes de `historico/gravacao.py`, escritos a partir da spec 08 antes de existir código.

Contrato assumido para `Gravador` (ver ambiguidades no relatório do agente que escreveu
estes testes — não há implementação para conferir, e os nomes abaixo são a interface que
os testes exigem):

    Gravador(banco, relogio=time.time)
    gravador.registrar(recurso, valor, unidade=None, livre_gb=None, agora=None)
        # `recurso` é qualquer objeto com `.nome` (str) e `.grava_historico` (bool) —
        # os recursos reais de `recursos.py` servem. Acumula `valor` no minuto em curso
        # da chave (recurso.nome, unidade); ao virar o minuto grava a média no banco.
    gravador.registrar_status(recurso, status, valor, programa=None, agora=None)
        # abre/atualiza/fecha o episódio de alerta a partir do Status já confirmado.
    gravador.registrar_lacuna(boot_em, agora=None)
        # lê `banco.ultimo_instante()`, grava a lacuna entre o mais recente dos dois
        # (ele ou o boot) e `agora`.
    gravador.fechar()
        # descarta a média parcial do minuto em curso, sem gravar.

O banco é a fronteira de I/O e por isso é mockado aqui — a lógica de acumulação, de
episódio e de lacuna é testada isolada dele. `historico/banco.py` tem suíte própria.
"""

import ast
import pathlib
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from hardware.thresholds import Status
from historico.gravacao import Gravador


def _recurso(nome, grava_historico=True):
    return SimpleNamespace(nome=nome, grava_historico=grava_historico)


# --- amostra por minuto -----------------------------------------------------------


def test_uma_linha_e_gravada_quando_o_minuto_vira():
    banco = MagicMock()
    gravador = Gravador(banco)
    recurso = _recurso("cpu")
    for i in range(60):
        gravador.registrar(recurso, valor=float(i), agora=float(i))
    gravador.registrar(recurso, valor=99.0, agora=60.0)
    assert banco.gravar_amostra.call_count == 1


def test_a_linha_gravada_traz_a_media_dos_valores_do_minuto():
    banco = MagicMock()
    gravador = Gravador(banco)
    recurso = _recurso("cpu")
    for i in range(60):
        gravador.registrar(recurso, valor=float(i), agora=float(i))
    gravador.registrar(recurso, valor=99.0, agora=60.0)
    esperado = sum(range(60)) / 60
    _, kwargs = banco.gravar_amostra.call_args
    assert kwargs["valor"] == pytest.approx(esperado)


def test_duas_unidades_de_disco_produzem_duas_linhas_por_minuto():
    banco = MagicMock()
    gravador = Gravador(banco)
    disco = _recurso("disco")
    for i in range(60):
        gravador.registrar(
            disco, valor=90.0, unidade="C:", livre_gb=10.0, agora=float(i)
        )
        gravador.registrar(
            disco, valor=50.0, unidade="D:", livre_gb=500.0, agora=float(i)
        )
    gravador.registrar(disco, valor=90.0, unidade="C:", livre_gb=10.0, agora=60.0)
    gravador.registrar(disco, valor=50.0, unidade="D:", livre_gb=500.0, agora=60.0)

    unidades = {c.kwargs["unidade"] for c in banco.gravar_amostra.call_args_list}
    assert unidades == {"C:", "D:"}


def test_linha_de_disco_traz_os_gb_livres_alem_do_percentual():
    banco = MagicMock()
    gravador = Gravador(banco)
    disco = _recurso("disco")
    for i in range(60):
        gravador.registrar(
            disco, valor=91.0, unidade="C:", livre_gb=11.0, agora=float(i)
        )
    gravador.registrar(disco, valor=91.0, unidade="C:", livre_gb=11.0, agora=60.0)
    _, kwargs = banco.gravar_amostra.call_args
    assert kwargs["livre_gb"] == 11.0


def test_recurso_com_grava_historico_falso_nao_gera_linha():
    banco = MagicMock()
    gravador = Gravador(banco)
    recurso = _recurso("fantasma", grava_historico=False)
    for i in range(60):
        gravador.registrar(recurso, valor=50.0, agora=float(i))
    gravador.registrar(recurso, valor=50.0, agora=60.0)
    banco.gravar_amostra.assert_not_called()


def test_o_mesmo_recurso_com_grava_historico_verdadeiro_gera_linha():
    banco = MagicMock()
    gravador = Gravador(banco)
    recurso = _recurso("fantasma", grava_historico=True)
    for i in range(60):
        gravador.registrar(recurso, valor=50.0, agora=float(i))
    gravador.registrar(recurso, valor=50.0, agora=60.0)
    banco.gravar_amostra.assert_called_once()


def test_temperatura_real_nunca_gera_amostra():
    """Usa o recurso de verdade de `recursos.py`: a exclusão vem do campo, não do nome."""
    import recursos

    banco = MagicMock()
    gravador = Gravador(banco)
    for i in range(60):
        gravador.registrar(recursos.TEMPERATURA, valor=70.0, agora=float(i))
    gravador.registrar(recursos.TEMPERATURA, valor=70.0, agora=60.0)
    banco.gravar_amostra.assert_not_called()


def test_gravador_nao_cita_nomes_de_recurso_no_codigo():
    """Quem é gravado vem de `grava_historico`, nunca de comparar nome de recurso.

    Olha os textos literais do módulo, não o arquivo inteiro: varredura por pedaço de
    palavra acusava `programa`, que carrega "ram" dentro de si e não é nome de recurso.
    """
    caminho = (
        pathlib.Path(__file__).resolve().parent.parent.parent
        / "historico"
        / "gravacao.py"
    )
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    literais = {
        no.value.lower()
        for no in ast.walk(arvore)
        if isinstance(no, ast.Constant) and isinstance(no.value, str)
    }
    proibidos = {"temperatura", "cpu", "ram", "disco", "placa_video"}
    assert literais & proibidos == set()


def test_fechar_descarta_a_media_parcial_do_minuto_em_curso():
    banco = MagicMock()
    gravador = Gravador(banco)
    recurso = _recurso("cpu")
    gravador.registrar(recurso, valor=10.0, agora=0.0)
    gravador.registrar(recurso, valor=20.0, agora=30.0)
    gravador.fechar()
    banco.gravar_amostra.assert_not_called()


# --- episódio de alerta -------------------------------------------------------------


def test_confirmar_alerta_abre_o_episodio_sem_instante_de_fim():
    banco = MagicMock()
    gravador = Gravador(banco)
    recurso = _recurso("cpu")
    gravador.registrar_status(
        recurso, Status.ALERTA, valor=90.0, programa="chrome.exe", agora=100.0
    )
    banco.abrir_episodio.assert_called_once_with(
        recurso="cpu", inicio=100.0, pico=90.0, programa="chrome.exe"
    )


def test_sair_do_alerta_preenche_o_fim_na_mesma_linha():
    banco = MagicMock()
    gravador = Gravador(banco)
    recurso = _recurso("cpu")
    gravador.registrar_status(recurso, Status.ALERTA, valor=90.0, agora=100.0)
    gravador.registrar_status(recurso, Status.NORMAL, valor=10.0, agora=160.0)
    banco.fechar_episodio.assert_called_once_with(recurso="cpu", fim=160.0)


def test_sair_do_alerta_nao_cria_um_segundo_episodio():
    banco = MagicMock()
    gravador = Gravador(banco)
    recurso = _recurso("cpu")
    gravador.registrar_status(recurso, Status.ALERTA, valor=90.0, agora=100.0)
    gravador.registrar_status(recurso, Status.NORMAL, valor=10.0, agora=160.0)
    banco.abrir_episodio.assert_called_once()


def test_pico_e_atualizado_quando_superado():
    banco = MagicMock()
    gravador = Gravador(banco)
    recurso = _recurso("cpu")
    gravador.registrar_status(recurso, Status.ALERTA, valor=90.0, agora=100.0)
    gravador.registrar_status(recurso, Status.ALERTA, valor=95.0, agora=101.0)
    banco.atualizar_pico_episodio.assert_called_once_with(recurso="cpu", pico=95.0)


def test_pico_nao_muda_quando_nao_e_superado():
    banco = MagicMock()
    gravador = Gravador(banco)
    recurso = _recurso("cpu")
    gravador.registrar_status(recurso, Status.ALERTA, valor=90.0, agora=100.0)
    gravador.registrar_status(recurso, Status.ALERTA, valor=80.0, agora=101.0)
    banco.atualizar_pico_episodio.assert_not_called()


def test_episodio_nunca_fechado_nao_impede_a_gravacao_dos_seguintes():
    banco = MagicMock()
    gravador = Gravador(banco)
    cpu = _recurso("cpu")
    ram = _recurso("ram")

    gravador.registrar_status(cpu, Status.ALERTA, valor=90.0, agora=100.0)
    # cpu nunca sai do alerta — o episódio dela fica aberto para sempre.
    gravador.registrar_status(ram, Status.ALERTA, valor=88.0, agora=150.0)
    gravador.registrar_status(ram, Status.NORMAL, valor=10.0, agora=200.0)

    banco.fechar_episodio.assert_called_once_with(recurso="ram", fim=200.0)


# --- lacuna: PC ligado sem o app -----------------------------------------------------


def test_lacuna_comeca_no_ultimo_minuto_quando_ele_e_mais_recente_que_o_boot():
    banco = MagicMock()
    agora = 100_000.0
    banco.ultimo_instante.return_value = agora - 3 * 3600
    gravador = Gravador(banco)
    gravador.registrar_lacuna(boot_em=agora - 5 * 3600, agora=agora)
    banco.gravar_lacuna.assert_called_once_with(inicio=agora - 3 * 3600, fim=agora)


def test_lacuna_comeca_no_boot_quando_ele_e_mais_recente_que_o_ultimo_minuto():
    """Boot mais recente que o último minuto gravado: o PC foi desligado no meio."""
    banco = MagicMock()
    agora = 100_000.0
    banco.ultimo_instante.return_value = agora - 3 * 3600
    gravador = Gravador(banco)
    gravador.registrar_lacuna(boot_em=agora - 1 * 3600, agora=agora)
    banco.gravar_lacuna.assert_called_once_with(inicio=agora - 1 * 3600, fim=agora)


def test_reabertura_segundos_depois_de_fechar_nao_grava_lacuna():
    banco = MagicMock()
    agora = 100_000.0
    banco.ultimo_instante.return_value = agora - 5
    gravador = Gravador(banco)
    gravador.registrar_lacuna(boot_em=agora - 3600, agora=agora)
    banco.gravar_lacuna.assert_not_called()


def test_lacuna_registrada_nao_grava_valor_de_recurso_nenhum():
    banco = MagicMock()
    agora = 100_000.0
    banco.ultimo_instante.return_value = agora - 3 * 3600
    gravador = Gravador(banco)
    gravador.registrar_lacuna(boot_em=agora - 5 * 3600, agora=agora)
    banco.gravar_amostra.assert_not_called()


# --- banco indisponível --------------------------------------------------------------


def test_banco_indisponivel_nao_impede_o_gravador_de_seguir_aceitando_chamadas(
    tmp_path,
):
    from historico.banco import Banco

    bloqueio = tmp_path / "bloqueio"
    bloqueio.write_text("isto e um arquivo, nao uma pasta", encoding="utf-8")
    banco = Banco(bloqueio / "historico.db")
    gravador = Gravador(banco)
    recurso = _recurso("cpu")

    for i in range(60):
        gravador.registrar(recurso, valor=float(i), agora=float(i))
    gravador.registrar(recurso, valor=99.0, agora=60.0)
    gravador.registrar_status(recurso, Status.ALERTA, valor=90.0, agora=61.0)
    gravador.registrar_lacuna(boot_em=0.0, agora=61.0)

    assert not banco.disponivel
