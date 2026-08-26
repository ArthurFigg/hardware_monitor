from unittest.mock import patch

import pytest

from sistema import estado


@pytest.fixture
def pasta_temporaria(tmp_path):
    """Nunca a pasta do app: ela está no OneDrive e sincronizaria sem parar."""
    with patch.dict("os.environ", {"LOCALAPPDATA": str(tmp_path)}):
        yield tmp_path


def test_estado_vazio_quando_nao_ha_arquivo(pasta_temporaria):
    assert estado.carregar() == {}


def test_salvar_e_carregar_de_volta(pasta_temporaria):
    estado.salvar({"ja_avisou": True})
    assert estado.carregar() == {"ja_avisou": True}


def test_definir_preserva_o_que_ja_estava(pasta_temporaria):
    estado.definir("primeiro", 1)
    estado.definir("segundo", 2)
    assert estado.carregar() == {"primeiro": 1, "segundo": 2}


def test_obter_devolve_o_padrao_quando_a_chave_falta(pasta_temporaria):
    assert estado.obter("inexistente", "padrao") == "padrao"


def test_arquivo_corrompido_conta_como_vazio(pasta_temporaria):
    """Arquivo cortado no meio de uma gravação não pode impedir o app de abrir."""
    estado.pasta().mkdir(parents=True, exist_ok=True)
    estado.caminho().write_text("{isso não é json", encoding="utf-8")
    assert estado.carregar() == {}


def test_conteudo_que_nao_e_dicionario_conta_como_vazio(pasta_temporaria):
    estado.pasta().mkdir(parents=True, exist_ok=True)
    estado.caminho().write_text("[1, 2, 3]", encoding="utf-8")
    assert estado.carregar() == {}


def test_pasta_fica_em_localappdata(pasta_temporaria):
    assert estado.pasta().parent == pasta_temporaria


def test_gravacao_que_falha_devolve_falso(pasta_temporaria):
    with patch.object(estado.Path, "mkdir", side_effect=PermissionError):
        assert not estado.salvar({"a": 1})
