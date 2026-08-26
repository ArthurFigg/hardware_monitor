from unittest.mock import MagicMock, patch

import pytest

from hardware.collector import DadosHardware, coletar
from hardware.discos import LeituraDisco, Unidade

_LEITURA = LeituraDisco(
    unidades=(Unidade(ponto="C:", percentual=30.0, livre_gb=300.0),)
)


@pytest.fixture(autouse=True)
def hardware_simulado():
    with (
        patch("hardware.collector.psutil.cpu_percent", return_value=45.0),
        patch("hardware.collector.psutil.virtual_memory") as ram,
        patch("hardware.collector.discos.ler", return_value=_LEITURA) as disco,
    ):
        ram.return_value = MagicMock(percent=60.0)
        yield ram, disco


def test_coletar_retorna_dados_hardware():
    assert isinstance(coletar(), DadosHardware)


def test_coletar_cpu_correto():
    assert coletar().cpu == 45.0


def test_coletar_ram_correta(hardware_simulado):
    ram, _ = hardware_simulado
    ram.return_value = MagicMock(percent=72.0)
    assert coletar().ram == 72.0


def test_coletar_disco_traz_a_leitura_completa():
    assert coletar().disco is _LEITURA
