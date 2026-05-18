from unittest.mock import patch

import pytest

from hardware.thresholds import (
    RastreadorAlerta,
    Status,
    classificar,
    classificar_temperatura,
    descricao,
    descricao_temperatura,
    estimar_temperatura,
)


@pytest.mark.parametrize("percentual", [0.0, 30.0, 59.9])
def test_classificar_normal(percentual):
    assert classificar(percentual) == Status.NORMAL


@pytest.mark.parametrize("percentual", [60.0, 72.0, 84.9])
def test_classificar_atencao(percentual):
    assert classificar(percentual) == Status.ATENCAO


@pytest.mark.parametrize("percentual", [85.0, 92.0, 100.0])
def test_classificar_alerta(percentual):
    assert classificar(percentual) == Status.ALERTA


def test_descricao_normal_contem_texto_correto():
    assert descricao(Status.NORMAL) == "Desempenho estável. O sistema está operando com folga."


def test_descricao_atencao_contem_texto_correto():
    assert descricao(Status.ATENCAO) == "Carga moderada. Vários processos estão exigindo recursos da máquina."


def test_descricao_alerta_contem_texto_correto():
    assert descricao(Status.ALERTA) == "Sobrecarga de memória/processamento. Feche aplicativos inativos para evitar travamentos."


def test_rastreador_retorna_atencao_antes_do_atraso():
    rastreador = RastreadorAlerta(atraso=5.0)
    with patch("hardware.thresholds.time.monotonic", side_effect=[0.0, 3.0]):
        rastreador.atualizar(Status.ALERTA)
        resultado = rastreador.atualizar(Status.ALERTA)
    assert resultado == Status.ATENCAO


def test_rastreador_retorna_alerta_apos_atraso():
    rastreador = RastreadorAlerta(atraso=5.0)
    with patch("hardware.thresholds.time.monotonic", side_effect=[0.0, 5.0]):
        rastreador.atualizar(Status.ALERTA)
        resultado = rastreador.atualizar(Status.ALERTA)
    assert resultado == Status.ALERTA


def test_rastreador_reseta_ao_sair_do_alerta():
    rastreador = RastreadorAlerta(atraso=5.0)
    with patch("hardware.thresholds.time.monotonic", side_effect=[0.0, 1.0]):
        rastreador.atualizar(Status.ALERTA)
        rastreador.atualizar(Status.NORMAL)
    assert rastreador._inicio is None


def test_rastreador_nao_altera_status_normal():
    assert RastreadorAlerta().atualizar(Status.NORMAL) == Status.NORMAL


def test_rastreador_nao_altera_status_atencao():
    assert RastreadorAlerta().atualizar(Status.ATENCAO) == Status.ATENCAO


@pytest.mark.parametrize("celsius", [0.0, 30.0, 59.9])
def test_classificar_temperatura_normal(celsius):
    assert classificar_temperatura(celsius) == Status.NORMAL


@pytest.mark.parametrize("celsius", [60.0, 70.0, 79.9])
def test_classificar_temperatura_atencao(celsius):
    assert classificar_temperatura(celsius) == Status.ATENCAO


@pytest.mark.parametrize("celsius", [80.0, 90.0, 100.0])
def test_classificar_temperatura_alerta(celsius):
    assert classificar_temperatura(celsius) == Status.ALERTA


def test_descricao_temperatura_normal():
    assert "segurança" in descricao_temperatura(Status.NORMAL)


def test_descricao_temperatura_atencao():
    assert "ventilação" in descricao_temperatura(Status.ATENCAO)


def test_descricao_temperatura_alerta():
    assert "crítica" in descricao_temperatura(Status.ALERTA)


def test_estimar_temperatura_cpu_zero():
    assert estimar_temperatura(0.0) == pytest.approx(35.0)


def test_estimar_temperatura_cpu_maxima():
    assert estimar_temperatura(100.0) == pytest.approx(85.0)


def test_estimar_temperatura_cpu_media():
    assert estimar_temperatura(50.0) == pytest.approx(60.0)
