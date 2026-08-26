from unittest.mock import MagicMock, patch

import psutil

from hardware import processos


def _processo(nome: str, cpu: float = 0.0, ram: float = 0.0):
    p = MagicMock()
    p.info = {"name": nome}
    p.cpu_percent.return_value = cpu
    p.memory_percent.return_value = ram
    return p


def test_soma_processos_de_mesmo_nome():
    abas = [_processo("chrome.exe", ram=4.0) for _ in range(20)]
    with patch.object(psutil, "process_iter", return_value=abas):
        nome, valor = processos.programa_dominante_ram()
    assert nome == "chrome.exe"
    assert valor == 80.0


def test_processo_ocioso_do_sistema_nunca_e_escolhido():
    lista = [
        _processo("System Idle Process", ram=99.0),
        _processo("chrome.exe", ram=5.0),
    ]
    with patch.object(psutil, "process_iter", return_value=lista):
        nome, _ = processos.programa_dominante_ram()
    assert nome == "chrome.exe"


def test_valor_de_cpu_e_normalizado_por_nucleo():
    # 400% somados em 4 núcleos = 100% da máquina
    lista = [_processo("jogo.exe", cpu=400.0)]
    with (
        patch.object(psutil, "process_iter", return_value=lista),
        patch.object(psutil, "cpu_count", return_value=4),
        patch.object(processos.time, "sleep"),
    ):
        nome, valor = processos.programa_dominante_cpu()
    assert nome == "jogo.exe"
    assert valor == 100.0


def test_valor_nunca_passa_de_cem():
    lista = [_processo("jogo.exe", cpu=800.0)]
    with (
        patch.object(psutil, "process_iter", return_value=lista),
        patch.object(psutil, "cpu_count", return_value=4),
        patch.object(processos.time, "sleep"),
    ):
        _, valor = processos.programa_dominante_cpu()
    assert valor == 100.0


def test_consumo_espalhado_nao_nomeia_ninguem():
    lista = [_processo(f"p{i}.exe", ram=0.2) for i in range(10)]
    with patch.object(psutil, "process_iter", return_value=lista):
        assert processos.programa_dominante_ram() is None


def test_sem_processo_nenhum_devolve_nada():
    with patch.object(psutil, "process_iter", return_value=[]):
        assert processos.programa_dominante_ram() is None


def test_processo_inacessivel_e_ignorado_sem_quebrar():
    inacessivel = _processo("protegido.exe")
    inacessivel.memory_percent.side_effect = psutil.AccessDenied()
    lista = [inacessivel, _processo("chrome.exe", ram=7.0)]
    with patch.object(psutil, "process_iter", return_value=lista):
        nome, _ = processos.programa_dominante_ram()
    assert nome == "chrome.exe"


def test_disco_e_temperatura_nao_varrem_processos():
    with patch.object(psutil, "process_iter") as varredura:
        assert processos.programa_dominante("disco") is None
        assert processos.programa_dominante("temperatura") is None
        varredura.assert_not_called()
