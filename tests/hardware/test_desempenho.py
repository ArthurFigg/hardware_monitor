from unittest.mock import MagicMock, patch

import pytest

from hardware import desempenho
from hardware.thresholds import ConfirmadorSustentado


@pytest.fixture(autouse=True)
def contador_limpo():
    """O contador é aberto uma vez e guardado — cada teste começa sem esse estado."""
    with (
        patch.object(desempenho, "_contador", None),
        patch.object(desempenho, "_tentou_abrir", False),
        patch.object(desempenho, "_confirmador", ConfirmadorSustentado(atraso=0.0)),
    ):
        yield


def _contador(valor, ok=True):
    return MagicMock(ok=ok, ler=MagicMock(return_value=valor))


def test_velocidade_devolve_o_valor_lido():
    with patch.object(desempenho.pdh, "Contador", return_value=_contador(87.5)):
        assert desempenho.velocidade_processador() == 87.5


def test_velocidade_acima_de_cem_e_normal():
    """Turbo. Medido nesta máquina: 120% em repouso."""
    with patch.object(desempenho.pdh, "Contador", return_value=_contador(121.0)):
        assert desempenho.velocidade_processador() == 121.0


def test_contador_que_nao_abre_devolve_none():
    with patch.object(desempenho.pdh, "Contador", return_value=_contador(0, ok=False)):
        assert desempenho.velocidade_processador() is None


def test_leitura_indisponivel_devolve_none():
    with patch.object(desempenho.pdh, "Contador", return_value=_contador(None)):
        assert desempenho.velocidade_processador() is None


def test_valor_negativo_e_tratado_como_indisponivel():
    with patch.object(desempenho.pdh, "Contador", return_value=_contador(-3.0)):
        assert desempenho.velocidade_processador() is None


def test_valor_absurdo_e_tratado_como_indisponivel():
    with patch.object(desempenho.pdh, "Contador", return_value=_contador(99999.0)):
        assert desempenho.velocidade_processador() is None


def test_consulta_e_aberta_uma_vez_so():
    """Abrir consulta por leitura custaria caro no ciclo de um segundo."""
    with patch.object(
        desempenho.pdh, "Contador", return_value=_contador(90.0)
    ) as abrir:
        desempenho.velocidade_processador()
        desempenho.velocidade_processador()
        desempenho.velocidade_processador()
        abrir.assert_called_once()


def test_contador_que_falhou_nao_e_reaberto_a_cada_leitura():
    with patch.object(
        desempenho.pdh, "Contador", return_value=_contador(0, ok=False)
    ) as abrir:
        desempenho.velocidade_processador()
        desempenho.velocidade_processador()
        abrir.assert_called_once()


def test_confirmar_reducao_com_carga_alta_e_velocidade_baixa():
    assert desempenho.confirmar_reducao(90.0, 85.0)


def test_confirmar_reducao_sem_velocidade_e_falso():
    assert not desempenho.confirmar_reducao(90.0, None)


def test_leitura_de_temperatura_nasce_sem_aviso():
    assert not desempenho.LeituraTemperatura(celsius=55.0).reduzindo
