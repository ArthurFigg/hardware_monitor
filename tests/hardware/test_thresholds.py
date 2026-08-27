from unittest.mock import patch

import pytest

from hardware.discos import LeituraDisco, Unidade
from hardware.placa_video import LeituraPlaca
from hardware.thresholds import (
    ConfirmadorSustentado,
    RastreadorAlerta,
    Status,
    classificar,
    classificar_disco,
    classificar_placa_video,
    classificar_temperatura,
    classificar_unidade,
    estimar_temperatura,
    placa_no_limite,
    reduzindo_por_calor,
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


@pytest.mark.parametrize("celsius", [0.0, 30.0, 64.9])
def test_classificar_temperatura_normal(celsius):
    assert classificar_temperatura(celsius) == Status.NORMAL


@pytest.mark.parametrize("celsius", [65.0, 70.0, 79.9])
def test_classificar_temperatura_atencao(celsius):
    assert classificar_temperatura(celsius) == Status.ATENCAO


@pytest.mark.parametrize("celsius", [80.0, 90.0, 100.0])
def test_classificar_temperatura_alerta(celsius):
    assert classificar_temperatura(celsius) == Status.ALERTA


def test_estimar_temperatura_cpu_zero():
    assert estimar_temperatura(0.0) == pytest.approx(35.0)


def test_estimar_temperatura_cpu_maxima():
    assert estimar_temperatura(100.0) == pytest.approx(85.0)


def test_estimar_temperatura_cpu_media():
    assert estimar_temperatura(50.0) == pytest.approx(60.0)


def test_unidade_com_folga_e_normal():
    assert classificar_unidade(40.0, 300.0) == Status.NORMAL


def test_unidade_em_85_por_cento_e_atencao():
    assert classificar_unidade(85.0, 100.0) == Status.ATENCAO


def test_unidade_em_95_por_cento_e_alerta_mesmo_com_espaco_de_sobra():
    """95% de um disco de 2 TB deixa 100 GB — o percentual manda mesmo assim."""
    assert classificar_unidade(95.0, 100.0) == Status.ALERTA


def test_unidade_com_menos_de_10_gb_livres_e_alerta_mesmo_pouco_ocupada():
    """Disco grande pouco usado não existe assim, mas a regra não pode depender disso."""
    assert classificar_unidade(50.0, 6.0) == Status.ALERTA


def test_unidade_com_menos_de_20_gb_livres_e_atencao():
    assert classificar_unidade(50.0, 15.0) == Status.ATENCAO


def test_disco_assume_o_status_da_pior_unidade():
    leitura = LeituraDisco(
        unidades=(
            Unidade(ponto="C:", percentual=96.0, livre_gb=4.0),
            Unidade(ponto="D:", percentual=20.0, livre_gb=800.0),
        )
    )
    assert classificar_disco(leitura) == Status.ALERTA


def test_disco_sem_nenhuma_unidade_e_normal():
    assert classificar_disco(LeituraDisco()) == Status.NORMAL


def test_desgaste_leva_o_disco_a_alerta():
    leitura = LeituraDisco(
        unidades=(Unidade(ponto="C:", percentual=30.0, livre_gb=400.0),),
        disco_desgastado="CT120BX500SSD1",
    )
    assert classificar_disco(leitura) == Status.ALERTA


def test_temperatura_atencao_acende_junto_com_a_cpu():
    """65°C é exatamente CPU 60% — os dois cartões acendem no mesmo ponto, não antes."""
    assert classificar_temperatura(estimar_temperatura(60.0)) == Status.ATENCAO


def test_temperatura_normal_logo_abaixo_do_limite():
    assert classificar_temperatura(64.9) == Status.NORMAL


def test_alerta_de_temperatura_continua_em_80_graus():
    assert classificar_temperatura(80.0) == Status.ALERTA


def test_carga_alta_com_velocidade_baixa_e_reducao():
    assert reduzindo_por_calor(90.0, 85.0)


def test_carga_alta_com_velocidade_alta_nao_e_reducao():
    """Turbo passa de 100%: velocidade alta sob carga é o processador trabalhando bem."""
    assert not reduzindo_por_calor(90.0, 95.0)


def test_carga_baixa_com_velocidade_baixa_nao_e_reducao():
    """PC ocioso também freia — ali é economia de energia, e acusar seria alarme falso."""
    assert not reduzindo_por_calor(50.0, 70.0)


def test_sem_leitura_de_velocidade_nao_afirma_reducao():
    assert not reduzindo_por_calor(95.0, None)


def test_carga_exatamente_no_limite_conta_como_alta():
    assert reduzindo_por_calor(85.0, 89.9)


def test_velocidade_exatamente_no_limite_nao_conta_como_baixa():
    assert not reduzindo_por_calor(90.0, 90.0)


def test_reducao_so_confirma_depois_do_tempo_minimo():
    confirmador = ConfirmadorSustentado(atraso=5.0)
    assert not confirmador.atualizar(True)


def test_reducao_confirma_quando_o_tempo_passa():
    confirmador = ConfirmadorSustentado(atraso=0.0)
    assert confirmador.atualizar(True)


def test_condicao_que_some_reinicia_a_contagem():
    confirmador = ConfirmadorSustentado(atraso=5.0)
    confirmador.atualizar(True)
    confirmador.atualizar(False)
    with patch("hardware.thresholds.time.monotonic", return_value=1e9):
        assert not confirmador.atualizar(True)


def test_placa_acima_de_95_esta_no_limite():
    assert placa_no_limite(96.0)


def test_placa_em_95_redondo_ainda_tem_folga():
    assert not placa_no_limite(95.0)


def test_placa_no_limite_classifica_em_atencao():
    assert classificar_placa_video(LeituraPlaca(uso=99.0, no_limite=True)) == (
        Status.ATENCAO
    )


def test_placa_fora_do_limite_e_normal():
    assert classificar_placa_video(LeituraPlaca(uso=40.0, no_limite=False)) == (
        Status.NORMAL
    )


def test_placa_nunca_chega_a_alerta():
    """Placa no limite não é emergência e não tem ação urgente — não existe vermelho."""
    em_todos = [
        classificar_placa_video(LeituraPlaca(uso=u, no_limite=True))
        for u in (96.0, 99.0, 100.0)
    ]
    assert Status.ALERTA not in em_todos


def test_rastreador_generalizado_preserva_o_comportamento_do_alerta():
    """O padrão continua sendo vigiar ALERTA e cair para ATENCAO enquanto espera."""
    assert RastreadorAlerta(atraso=5.0).atualizar(Status.ALERTA) == Status.ATENCAO


def test_rastreador_pode_vigiar_a_atencao():
    rastreador = RastreadorAlerta(atraso=5.0, confirmar=Status.ATENCAO)
    assert rastreador.atualizar(Status.ATENCAO) == Status.NORMAL


def test_rastreador_confirma_a_atencao_depois_do_tempo():
    rastreador = RastreadorAlerta(atraso=0.0, confirmar=Status.ATENCAO)
    assert rastreador.atualizar(Status.ATENCAO) == Status.ATENCAO


def test_rastreador_de_atencao_deixa_o_alerta_passar_direto():
    """Quem vigia ATENCAO não segura ALERTA — status que não é o vigiado passa inteiro."""
    rastreador = RastreadorAlerta(atraso=5.0, confirmar=Status.ATENCAO)
    assert rastreador.atualizar(Status.ALERTA) == Status.ALERTA
