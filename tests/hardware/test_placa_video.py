from unittest.mock import MagicMock, patch

import pytest

from hardware import placa_video
from hardware.placa_video import (
    LeituraPlaca,
    agregar,
    placa_de_motor,
    tipo_de_motor,
)
from hardware.thresholds import RastreadorAlerta, Status


@pytest.fixture(autouse=True)
def contador_limpo():
    """O contador é aberto uma vez e guardado — cada teste começa sem esse estado."""
    with (
        patch.object(placa_video, "_contador", None),
        patch.object(placa_video, "_tentou_abrir", False),
        patch.object(
            placa_video,
            "_rastreador",
            RastreadorAlerta(atraso=0.0, confirmar=Status.ATENCAO),
        ),
    ):
        yield


def _motor(pid: int, tipo: str, placa: str = "0x00000000_0x00010327_phys_0") -> str:
    return f"pid_{pid}_luid_{placa}_eng_0_engtype_{tipo}"


def test_tipo_de_motor_sai_do_nome_da_instancia():
    assert tipo_de_motor(_motor(100, "3D")) == "3D"


def test_instancia_sem_tipo_nao_quebra():
    assert tipo_de_motor("nome_estranho") == "desconhecido"


def test_valor_e_o_maior_tipo_e_nao_a_soma():
    """Somar os 336 motores daria número acima de 100% sem sentido."""
    leituras = [
        (_motor(1, "3D"), 40.0),
        (_motor(2, "Copy"), 30.0),
        (_motor(3, "VideoDecode"), 20.0),
    ]
    assert agregar(leituras) == 40.0


def test_processos_no_mesmo_tipo_somam_entre_si():
    """Dois programas usando o motor 3D ao mesmo tempo usam o mesmo motor."""
    leituras = [(_motor(1, "3D"), 40.0), (_motor(2, "3D"), 25.0)]
    assert agregar(leituras) == 65.0


def test_valor_nunca_passa_de_cem():
    leituras = [(_motor(1, "3D"), 80.0), (_motor(2, "3D"), 80.0)]
    assert agregar(leituras) == 100.0


def test_valores_negativos_sao_ignorados():
    leituras = [(_motor(1, "3D"), -5.0), (_motor(2, "Copy"), 12.0)]
    assert agregar(leituras) == 12.0


def test_vetor_vazio_devolve_none():
    assert agregar([]) is None


def test_vetor_none_devolve_none():
    assert agregar(None) is None


def _contador_falso(leituras, ok=True):
    return MagicMock(ok=ok, ler=MagicMock(return_value=leituras))


def test_uso_agrega_a_leitura_do_contador():
    falso = _contador_falso([(_motor(1, "3D"), 23.0)])
    with patch.object(placa_video.pdh, "ContadorVetor", return_value=falso):
        assert placa_video.uso() == 23.0


def test_contador_que_nao_abre_devolve_none():
    falso = _contador_falso([], ok=False)
    with patch.object(placa_video.pdh, "ContadorVetor", return_value=falso):
        assert placa_video.uso() is None


def test_leitura_que_levanta_erro_devolve_none():
    """Contador que explode vira indisponível, nunca exceção na tela."""
    falso = MagicMock(ok=True, ler=MagicMock(side_effect=OSError("contador sumiu")))
    with patch.object(placa_video.pdh, "ContadorVetor", return_value=falso):
        assert placa_video.uso() is None


def test_contador_e_aberto_uma_vez_so():
    falso = _contador_falso([(_motor(1, "3D"), 5.0)])
    with patch.object(placa_video.pdh, "ContadorVetor", return_value=falso) as abrir:
        placa_video.uso()
        placa_video.uso()
        abrir.assert_called_once()


def test_ler_devolve_none_quando_nao_ha_contador():
    """Sem leitura nenhuma, o cartão inteiro some da tela."""
    falso = _contador_falso([], ok=False)
    with patch.object(placa_video.pdh, "ContadorVetor", return_value=falso):
        assert placa_video.ler() is None


def test_ler_marca_no_limite_acima_de_95():
    falso = _contador_falso([(_motor(1, "3D"), 96.0)])
    with patch.object(placa_video.pdh, "ContadorVetor", return_value=falso):
        assert placa_video.ler().no_limite


def test_ler_nao_marca_no_limite_em_95_redondo():
    falso = _contador_falso([(_motor(1, "3D"), 95.0)])
    with patch.object(placa_video.pdh, "ContadorVetor", return_value=falso):
        assert not placa_video.ler().no_limite


def test_placa_baixa_nao_esta_no_limite():
    """Placa integrada responde com número baixo e real — cartão verde e discreto."""
    falso = _contador_falso([(_motor(1, "3D"), 0.4)])
    with patch.object(placa_video.pdh, "ContadorVetor", return_value=falso):
        assert not placa_video.ler().no_limite


def test_pico_curto_nao_confirma_o_limite():
    """Sem a janela de 5 s o cartão piscaria amarelo a cada pico de um segundo."""
    falso = _contador_falso([(_motor(1, "3D"), 99.0)])
    with (
        patch.object(placa_video.pdh, "ContadorVetor", return_value=falso),
        patch.object(
            placa_video, "_rastreador", RastreadorAlerta(confirmar=Status.ATENCAO)
        ),
    ):
        assert not placa_video.ler().no_limite


def test_leitura_nasce_fora_do_limite():
    assert not LeituraPlaca(uso=50.0).no_limite


def test_placa_de_motor_sai_do_luid_e_do_phys():
    assert placa_de_motor(_motor(1, "3D")) == "0x00000000_0x00010327_phys_0"


def test_instancia_sem_luid_nao_quebra():
    assert placa_de_motor("nome_estranho") == "desconhecida"


def test_placas_diferentes_nao_somam_entre_si():
    """Integrada e dedicada listam as duas — somar o 3D delas inventaria carga."""
    leituras = [
        (_motor(1, "3D", placa="0x0_0x1_phys_0"), 60.0),
        (_motor(2, "3D", placa="0x0_0x2_phys_1"), 55.0),
    ]
    assert agregar(leituras) == 60.0
