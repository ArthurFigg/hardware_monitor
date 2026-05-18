from unittest.mock import MagicMock, patch

from hardware.collector import DadosHardware, coletar


@patch("hardware.collector.psutil.cpu_percent", return_value=45.0)
@patch("hardware.collector.psutil.virtual_memory")
@patch("hardware.collector.psutil.disk_usage")
def test_coletar_retorna_dados_hardware(mock_disco, mock_ram, _mock_cpu):
    mock_ram.return_value = MagicMock(percent=60.0)
    mock_disco.return_value = MagicMock(percent=30.0)

    assert isinstance(coletar(), DadosHardware)


@patch("hardware.collector.psutil.cpu_percent", return_value=45.0)
@patch("hardware.collector.psutil.virtual_memory")
@patch("hardware.collector.psutil.disk_usage")
def test_coletar_cpu_correto(mock_disco, mock_ram, _mock_cpu):
    mock_ram.return_value = MagicMock(percent=60.0)
    mock_disco.return_value = MagicMock(percent=30.0)

    assert coletar().cpu == 45.0


@patch("hardware.collector.psutil.cpu_percent", return_value=45.0)
@patch("hardware.collector.psutil.virtual_memory")
@patch("hardware.collector.psutil.disk_usage")
def test_coletar_ram_correta(mock_disco, mock_ram, _mock_cpu):
    mock_ram.return_value = MagicMock(percent=72.0)
    mock_disco.return_value = MagicMock(percent=30.0)

    assert coletar().ram == 72.0


@patch("hardware.collector.psutil.cpu_percent", return_value=45.0)
@patch("hardware.collector.psutil.virtual_memory")
@patch("hardware.collector.psutil.disk_usage")
def test_coletar_disco_correto(mock_disco, mock_ram, _mock_cpu):
    mock_ram.return_value = MagicMock(percent=60.0)
    mock_disco.return_value = MagicMock(percent=55.0)

    assert coletar().disco == 55.0
