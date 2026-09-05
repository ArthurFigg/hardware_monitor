from unittest.mock import MagicMock, patch

import pytest

from sistema import instancia_unica


@pytest.fixture
def kernel():
    """API do Windows trocada — nenhum teste cria mutex de verdade."""
    falso = MagicMock()
    falso.GetLastError.return_value = 0
    falso.CreateMutexW.return_value = 1
    falso.CreateEventW.return_value = 2
    falso.SetEvent.return_value = 1
    with patch.object(instancia_unica, "_kernel32", falso):
        yield falso


def test_primeira_instancia_reserva(kernel):
    assert instancia_unica.reservar()


def test_segunda_instancia_nao_reserva(kernel):
    kernel.GetLastError.return_value = instancia_unica._JA_EXISTE
    assert not instancia_unica.reservar()


def test_reservar_usa_o_nome_combinado(kernel):
    """Nome diferente entre as duas instâncias faria cada uma se achar a primeira."""
    instancia_unica.reservar()
    assert kernel.CreateMutexW.call_args.args[2] == instancia_unica.NOME_MUTEX


def test_o_identificador_do_mutex_fica_guardado(kernel):
    """Solto, o coletor de lixo o recolhe e o Windows libera o mutex."""
    instancia_unica.reservar()
    assert instancia_unica._mutex == 1


def test_pedir_para_abrir_sinaliza_o_evento(kernel):
    assert instancia_unica.pedir_para_abrir()
    kernel.SetEvent.assert_called_once_with(2)


def test_pedir_para_abrir_fecha_o_que_abriu(kernel):
    instancia_unica.pedir_para_abrir()
    kernel.CloseHandle.assert_called_once_with(2)


def test_pedir_para_abrir_sem_evento_devolve_falha(kernel):
    kernel.CreateEventW.return_value = 0
    assert not instancia_unica.pedir_para_abrir()


def test_vigiar_chama_a_acao_a_cada_pedido(kernel):
    """Um sinal, uma chamada; a espera seguinte falha e encerra a vigilância."""
    kernel.WaitForSingleObject.side_effect = [
        instancia_unica._SINALIZADO,
        instancia_unica._ESPERA_FALHOU,
    ]
    avisado = MagicMock()
    thread = instancia_unica.vigiar_pedidos(avisado)
    thread.join(timeout=2)
    avisado.assert_called_once_with()


def test_vigiar_sem_evento_nao_sobe_thread(kernel):
    kernel.CreateEventW.return_value = 0
    assert instancia_unica.vigiar_pedidos(MagicMock()) is None


def test_sem_windows_reservar_deixa_passar():
    """O CI roda em Linux, onde `ctypes.windll` não existe."""
    with patch.object(instancia_unica, "_kernel32", None):
        assert instancia_unica.reservar()


def test_sem_windows_nao_sobe_vigilancia():
    with patch.object(instancia_unica, "_kernel32", None):
        assert instancia_unica.vigiar_pedidos(MagicMock()) is None


def test_sem_windows_pedir_para_abrir_devolve_falha():
    with patch.object(instancia_unica, "_kernel32", None):
        assert not instancia_unica.pedir_para_abrir()


def test_vigiar_para_quando_a_espera_falha(kernel):
    """Identificador inválido: insistir queimaria um núcleo em laço apertado."""
    kernel.WaitForSingleObject.return_value = instancia_unica._ESPERA_FALHOU
    thread = instancia_unica.vigiar_pedidos(MagicMock())
    thread.join(timeout=2)
    assert not thread.is_alive()
