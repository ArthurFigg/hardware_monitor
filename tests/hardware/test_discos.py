from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from hardware import discos
from hardware.discos import GB, CacheSaude, LeituraDisco, Unidade, listar_unidades


def _particao(mountpoint="C:\\", fstype="NTFS", opts="rw,fixed"):
    return SimpleNamespace(
        device=mountpoint, mountpoint=mountpoint, fstype=fstype, opts=opts
    )


def _uso(total_gb=500.0, percent=40.0, livre_gb=300.0):
    return SimpleNamespace(
        total=total_gb * GB, percent=percent, free=livre_gb * GB, used=0
    )


@pytest.fixture
def particoes():
    with patch("hardware.discos.psutil.disk_partitions") as mock:
        yield mock


@pytest.fixture
def uso():
    with patch("hardware.discos.psutil.disk_usage") as mock:
        yield mock


def test_unidade_fixa_entra_na_lista(particoes, uso):
    particoes.return_value = [_particao()]
    uso.return_value = _uso()
    assert [u.ponto for u in listar_unidades()] == ["C:"]


def test_unidade_removivel_fica_de_fora(particoes, uso):
    particoes.return_value = [_particao("E:\\", opts="rw,removable")]
    uso.return_value = _uso()
    assert listar_unidades() == ()


def test_unidade_de_rede_fica_de_fora(particoes, uso):
    particoes.return_value = [_particao("Z:\\", opts="rw,remote")]
    uso.return_value = _uso()
    assert listar_unidades() == ()


def test_unidade_de_cd_fica_de_fora(particoes, uso):
    particoes.return_value = [_particao("D:\\", fstype="CDFS", opts="cdrom")]
    uso.return_value = _uso()
    assert listar_unidades() == ()


def test_particao_de_recuperacao_fica_de_fora(particoes, uso):
    """~500 MB e sempre quase cheia — sem o filtro o app abriria em Alerta permanente."""
    particoes.return_value = [_particao("R:\\")]
    uso.return_value = _uso(total_gb=0.5, percent=98.0, livre_gb=0.01)
    assert listar_unidades() == ()


def test_unidade_que_sumiu_nao_quebra_a_coleta(particoes, uso):
    particoes.return_value = [_particao()]
    uso.side_effect = OSError("dispositivo não está pronto")
    assert listar_unidades() == ()


def test_varias_unidades_fixas_entram_todas(particoes, uso):
    particoes.return_value = [_particao("C:\\"), _particao("D:\\")]
    uso.return_value = _uso()
    assert len(listar_unidades()) == 2


def _resposta(saida, codigo=0):
    return MagicMock(returncode=codigo, stdout=saida, stderr="")


def test_saude_reporta_disco_doente():
    saida = '[{"FriendlyName":"CT120BX500SSD1","HealthStatus":"Unhealthy"}]'
    with patch("hardware.discos.subprocess.run", return_value=_resposta(saida)):
        assert discos._consultar_saude() == ("CT120BX500SSD1",)


def test_saude_com_todos_saudaveis_e_tupla_vazia():
    saida = '[{"FriendlyName":"CT120BX500SSD1","HealthStatus":"Healthy"}]'
    with patch("hardware.discos.subprocess.run", return_value=_resposta(saida)):
        assert discos._consultar_saude() == ()


def test_saude_aceita_objeto_unico_de_um_disco_so():
    """Com um disco só, o PowerShell devolve um objeto em vez de uma lista."""
    saida = '{"FriendlyName":"WDC WD10EZEX","HealthStatus":"Warning"}'
    with patch("hardware.discos.subprocess.run", return_value=_resposta(saida)):
        assert discos._consultar_saude() == ("WDC WD10EZEX",)


def test_saude_com_comando_ausente_devolve_none():
    with patch("hardware.discos.subprocess.run", side_effect=FileNotFoundError):
        assert discos._consultar_saude() is None


def test_saude_com_codigo_de_erro_devolve_none():
    with patch("hardware.discos.subprocess.run", return_value=_resposta("", codigo=1)):
        assert discos._consultar_saude() is None


def test_saude_com_saida_ilegivel_devolve_none():
    with patch("hardware.discos.subprocess.run", return_value=_resposta("não é json")):
        assert discos._consultar_saude() is None


def test_cache_nao_reconsulta_dentro_do_intervalo():
    cache = CacheSaude(intervalo=6 * 60 * 60)
    with patch("hardware.discos._consultar_saude", return_value=()) as consulta:
        cache.obter()
        cache.obter()
        consulta.assert_called_once()


def test_cache_reconsulta_depois_do_intervalo():
    cache = CacheSaude(intervalo=0)
    with patch("hardware.discos._consultar_saude", return_value=()) as consulta:
        cache.obter()
        cache.obter()
        assert consulta.call_count == 2


def test_leitura_junta_unidades_e_desgaste(particoes, uso):
    particoes.return_value = [_particao()]
    uso.return_value = _uso()
    with patch.object(discos._cache_saude, "obter", return_value=("SSD velho",)):
        leitura = discos.ler()
    assert leitura.disco_desgastado == "SSD velho"


def test_leitura_sem_desgaste_nao_nomeia_disco(particoes, uso):
    particoes.return_value = [_particao()]
    uso.return_value = _uso()
    with patch.object(discos._cache_saude, "obter", return_value=()):
        assert discos.ler().disco_desgastado is None


def test_saude_que_falhou_nao_vira_desgaste(particoes, uso):
    """`None` é "não consegui consultar", e não pode acender o alerta de desgaste."""
    particoes.return_value = [_particao()]
    uso.return_value = _uso()
    with patch.object(discos._cache_saude, "obter", return_value=None):
        assert discos.ler().disco_desgastado is None


def test_pior_unidade_e_a_mais_cheia():
    leitura = LeituraDisco(
        unidades=(
            Unidade(ponto="C:", percentual=91.0, livre_gb=15.0),
            Unidade(ponto="D:", percentual=40.0, livre_gb=600.0),
        )
    )
    assert leitura.pior_unidade.ponto == "C:"


def test_pior_unidade_sem_unidades_e_none():
    assert LeituraDisco().pior_unidade is None


def _leitura_com_saude_quebrada(particoes, uso):
    """Windows antigo ou permissão negada, com o espaço ainda legível."""
    particoes.return_value = [_particao()]
    uso.return_value = _uso(percent=96.0, livre_gb=4.0)
    with (
        patch.object(discos, "_cache_saude", CacheSaude()),
        patch("hardware.discos.subprocess.run", side_effect=OSError),
    ):
        return discos.ler()


def test_saude_que_falhou_nao_impede_a_leitura_de_espaco(particoes, uso):
    leitura = _leitura_com_saude_quebrada(particoes, uso)
    assert leitura.pior_unidade.percentual == 96.0


def test_saude_que_falhou_esconde_a_linha_de_desgaste(particoes, uso):
    leitura = _leitura_com_saude_quebrada(particoes, uso)
    assert leitura.disco_desgastado is None


def test_pior_unidade_e_a_de_pior_status_nao_a_de_maior_percentual():
    """SSD de sistema apertado perde no percentual para um HD cheio, mas manda no status.

    Sem esta regra o cartão acende vermelho por causa do C: e exibe o D: no rótulo.
    """
    leitura = LeituraDisco(
        unidades=(
            Unidade(ponto="C:", percentual=93.0, livre_gb=8.4),
            Unidade(ponto="D:", percentual=94.0, livre_gb=120.0),
        )
    )
    assert leitura.pior_unidade.ponto == "C:"


def test_pior_unidade_desempata_pelo_percentual_dentro_do_mesmo_status():
    leitura = LeituraDisco(
        unidades=(
            Unidade(ponto="C:", percentual=96.0, livre_gb=8.0),
            Unidade(ponto="D:", percentual=99.0, livre_gb=2.0),
        )
    )
    assert leitura.pior_unidade.ponto == "D:"
