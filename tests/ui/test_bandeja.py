from unittest.mock import MagicMock, patch

import pytest

from hardware.thresholds import Status
from ui import bandeja
from ui.components.semaphore import CORES


@pytest.fixture
def pystray_falso():
    falso = MagicMock()
    falso.Icon.return_value = MagicMock(icon=None, title=None)
    with patch.object(bandeja, "pystray", falso):
        yield falso


def _bandeja(pystray_falso=None, abrir=None, sair=None):
    return bandeja.Bandeja(
        ao_abrir=abrir or (lambda: None), ao_sair=sair or (lambda: None)
    )


def test_cor_do_icone_normal_e_a_do_semaforo():
    """A paleta é lida do semáforo, não redefinida aqui."""
    imagem = bandeja.desenhar(Status.NORMAL, tamanho=16)
    assert CORES[Status.NORMAL].lstrip("#").lower() in _cores_usadas(imagem)


def test_cor_do_icone_atencao_e_a_do_semaforo():
    imagem = bandeja.desenhar(Status.ATENCAO, tamanho=16)
    assert CORES[Status.ATENCAO].lstrip("#").lower() in _cores_usadas(imagem)


def test_cor_do_icone_alerta_e_a_do_semaforo():
    imagem = bandeja.desenhar(Status.ALERTA, tamanho=16)
    assert CORES[Status.ALERTA].lstrip("#").lower() in _cores_usadas(imagem)


def _cores_usadas(imagem) -> set[str]:
    return {
        f"{r:02x}{g:02x}{b:02x}"
        for _, (r, g, b, a) in imagem.getcolors(maxcolors=100000) or []
        if a > 0
    }


def test_tres_status_dao_tres_cores_distintas():
    cores = {CORES[s] for s in (Status.NORMAL, Status.ATENCAO, Status.ALERTA)}
    assert len(cores) == 3


def test_descricao_muda_com_o_status():
    assert bandeja.descricao(Status.NORMAL) != bandeja.descricao(Status.ALERTA)


def test_descricao_nomeia_o_app():
    assert bandeja.descricao(Status.NORMAL).startswith("Monitor de Hardware")


def test_iniciar_sobe_o_icone(pystray_falso):
    icone = _bandeja()
    assert icone.iniciar(Status.NORMAL)


def test_iniciar_roda_em_thread_propria(pystray_falso):
    """`run_detached` — a janela não pode ficar presa esperando a bandeja."""
    icone = _bandeja()
    icone.iniciar(Status.NORMAL)
    pystray_falso.Icon.return_value.run_detached.assert_called_once()


def test_sem_pystray_a_bandeja_fica_indisponivel():
    with patch.object(bandeja, "pystray", None):
        assert not _bandeja().disponivel


def test_sem_pystray_iniciar_devolve_falso():
    with patch.object(bandeja, "pystray", None):
        assert not _bandeja().iniciar(Status.NORMAL)


def test_ambiente_sem_area_de_notificacao_nao_levanta_erro(pystray_falso):
    """Nunca exibe erro, nunca impede o app de abrir."""
    pystray_falso.Icon.side_effect = OSError("sem área de notificação")
    icone = _bandeja()
    assert not icone.iniciar(Status.NORMAL)


def test_falha_ao_subir_marca_como_indisponivel(pystray_falso):
    pystray_falso.Icon.side_effect = OSError("sem área de notificação")
    icone = _bandeja()
    icone.iniciar(Status.NORMAL)
    assert not icone.disponivel


def test_atualizar_troca_a_cor_quando_o_status_muda(pystray_falso):
    icone = _bandeja()
    icone.iniciar(Status.NORMAL)
    antes = pystray_falso.Icon.return_value.icon
    icone.atualizar(Status.ALERTA)
    assert pystray_falso.Icon.return_value.icon is not antes


def test_atualizar_nao_redesenha_com_o_mesmo_status(pystray_falso):
    """Redesenhar a cada ciclo custaria uma imagem por segundo para nada."""
    icone = _bandeja()
    icone.iniciar(Status.NORMAL)
    antes = pystray_falso.Icon.return_value.icon
    icone.atualizar(Status.NORMAL)
    assert pystray_falso.Icon.return_value.icon is antes


def test_atualizar_sem_icone_nao_quebra():
    with patch.object(bandeja, "pystray", None):
        _bandeja().atualizar(Status.ALERTA)


def test_menu_tem_abrir_e_sair(pystray_falso):
    icone = _bandeja()
    icone.iniciar(Status.NORMAL)
    rotulos = [chamada.args[0] for chamada in pystray_falso.MenuItem.call_args_list]
    assert rotulos == ["Abrir", "Sair"]


def test_abrir_chama_a_acao_recebida(pystray_falso):
    chamadas = []
    icone = _bandeja(abrir=lambda: chamadas.append("abriu"))
    icone.iniciar(Status.NORMAL)
    acao_abrir = pystray_falso.MenuItem.call_args_list[0].args[1]
    acao_abrir()
    assert chamadas == ["abriu"]


def test_sair_chama_a_acao_recebida(pystray_falso):
    chamadas = []
    icone = _bandeja(sair=lambda: chamadas.append("saiu"))
    icone.iniciar(Status.NORMAL)
    acao_sair = pystray_falso.MenuItem.call_args_list[1].args[1]
    acao_sair()
    assert chamadas == ["saiu"]


def test_parar_remove_o_icone(pystray_falso):
    icone = _bandeja()
    icone.iniciar(Status.NORMAL)
    icone.parar()
    pystray_falso.Icon.return_value.stop.assert_called_once()


def test_parar_sem_icone_nao_quebra():
    with patch.object(bandeja, "pystray", None):
        _bandeja().parar()
