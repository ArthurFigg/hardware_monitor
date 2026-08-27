from unittest.mock import MagicMock, patch

import pytest

from hardware.collector import DadosHardware, coletar, segundos_ligado
from hardware.discos import LeituraDisco, Unidade
from hardware.placa_video import LeituraPlaca

_PLACA = LeituraPlaca(uso=12.0)
_LEITURA = LeituraDisco(
    unidades=(Unidade(ponto="C:", percentual=30.0, livre_gb=300.0),)
)


@pytest.fixture(autouse=True)
def hardware_simulado():
    with (
        patch("hardware.collector.psutil.cpu_percent", return_value=45.0),
        patch("hardware.collector.psutil.virtual_memory") as ram,
        patch("hardware.collector.discos.ler", return_value=_LEITURA) as disco,
        patch(
            "hardware.collector.desempenho.velocidade_processador", return_value=118.0
        ),
        patch("hardware.collector.placa_video.ler", return_value=_PLACA),
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


def test_coletar_traz_a_velocidade_do_processador():
    assert coletar().velocidade == 118.0


def test_coletar_avanca_a_janela_do_aviso_de_calor():
    """O relógio de 5 s anda na coleta — um tique por ciclo, não por consumidor."""
    with patch(
        "hardware.collector.desempenho.confirmar_reducao", return_value=True
    ) as confirmar:
        assert coletar().reduzindo
        confirmar.assert_called_once()


def test_segundos_ligado_conta_desde_o_boot():
    with (
        patch("hardware.collector.psutil.boot_time", return_value=1000.0),
        patch("hardware.collector.time.time", return_value=1000.0 + 3600),
    ):
        assert segundos_ligado() == 3600


def test_segundos_ligado_indisponivel_devolve_none():
    """Leitura que falha esconde a linha do rodapé, nunca quebra a janela."""
    with patch("hardware.collector.psutil.boot_time", side_effect=OSError):
        assert segundos_ligado() is None


def test_coletar_traz_a_leitura_da_placa():
    assert coletar().placa is _PLACA
