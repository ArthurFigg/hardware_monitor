"""Testes de `historico/banco.py`, escritos a partir da spec 08 antes de existir código.

Contrato assumido (não existe implementação ainda, então este é o contrato que os
testes exigem — ver ambiguidades no relatório do agente que os escreveu):

    Banco(caminho=None)          # caminho explícito, ou o padrão em %LOCALAPPDATA%
    banco.disponivel             # False quando abrir/criar falhou, sem levantar erro
    banco.gravar_amostra(recurso, instante, valor, unidade=None, livre_gb=None)
    banco.abrir_episodio(recurso, inicio, pico, programa=None)
    banco.atualizar_pico_episodio(recurso, pico)
    banco.fechar_episodio(recurso, fim)
    banco.gravar_lacuna(inicio, fim)
    banco.ultimo_instante()      # instante da amostra mais recente, ou None
    banco.amostras(desde=None, ate=None)    # lista de dicts, ordenada por instante
    banco.episodios(desde=None, ate=None)   # idem
    banco.lacunas(desde=None, ate=None)     # idem
    banco.fechar()

Todos os testes usam pasta temporária (fixture `pasta_temporaria` ou caminho explícito
em `tmp_path`) — nenhum toca `%LOCALAPPDATA%` real nem a pasta do projeto.
"""

import time
from unittest.mock import patch

import pytest

from historico.banco import Banco

DIA = 24 * 60 * 60


@pytest.fixture
def pasta_temporaria(tmp_path):
    """Nunca a pasta do app: ela está no OneDrive e sincronizaria sem parar."""
    with patch.dict("os.environ", {"LOCALAPPDATA": str(tmp_path)}):
        yield tmp_path


def test_banco_abre_e_fica_disponivel_em_pasta_gravavel(pasta_temporaria):
    banco = Banco()
    assert banco.disponivel


def test_banco_indisponivel_quando_o_caminho_e_impossivel(tmp_path):
    """O 'lugar impossível de escrever' é um arquivo comum no lugar de uma pasta."""
    bloqueio = tmp_path / "bloqueio"
    bloqueio.write_text("isto e um arquivo, nao uma pasta", encoding="utf-8")
    banco = Banco(bloqueio / "historico.db")
    assert not banco.disponivel


def test_banco_indisponivel_nao_levanta_ao_gravar(tmp_path):
    """Escrita que falha esconde a si mesma — a regra de leitura, aplicada à escrita."""
    bloqueio = tmp_path / "bloqueio"
    bloqueio.write_text("isto e um arquivo, nao uma pasta", encoding="utf-8")
    banco = Banco(bloqueio / "historico.db")

    banco.gravar_amostra("cpu", instante=1.0, valor=50.0)
    banco.abrir_episodio("cpu", inicio=1.0, pico=90.0)
    banco.atualizar_pico_episodio("cpu", pico=95.0)
    banco.fechar_episodio("cpu", fim=2.0)
    banco.gravar_lacuna(inicio=1.0, fim=2.0)

    assert not banco.disponivel


def test_amostra_gravada_aparece_na_leitura(tmp_path):
    banco = Banco(tmp_path / "historico.db")
    banco.gravar_amostra("cpu", instante=1000.0, valor=42.0)
    amostras = banco.amostras()
    assert any(a["recurso"] == "cpu" and a["valor"] == 42.0 for a in amostras)


def test_amostra_de_disco_grava_a_unidade(tmp_path):
    banco = Banco(tmp_path / "historico.db")
    banco.gravar_amostra(
        "disco", instante=1000.0, valor=91.0, unidade="C:", livre_gb=11.0
    )
    amostra = banco.amostras()[0]
    assert amostra["unidade"] == "C:"


def test_amostra_de_disco_grava_os_gb_livres(tmp_path):
    banco = Banco(tmp_path / "historico.db")
    banco.gravar_amostra(
        "disco", instante=1000.0, valor=91.0, unidade="C:", livre_gb=11.0
    )
    amostra = banco.amostras()[0]
    assert amostra["livre_gb"] == 11.0


def test_amostra_com_mais_de_90_dias_e_apagada_na_abertura(tmp_path):
    caminho = tmp_path / "historico.db"
    agora = time.time()
    antigo = agora - 91 * DIA

    primeiro = Banco(caminho)
    primeiro.gravar_amostra("cpu", instante=antigo, valor=10.0)
    primeiro.fechar()

    reaberto = Banco(caminho)
    assert reaberto.amostras() == []


def test_amostra_de_89_dias_permanece(tmp_path):
    caminho = tmp_path / "historico.db"
    agora = time.time()
    recente = agora - 89 * DIA

    primeiro = Banco(caminho)
    primeiro.gravar_amostra("cpu", instante=recente, valor=10.0)
    primeiro.fechar()

    reaberto = Banco(caminho)
    assert len(reaberto.amostras()) == 1


def test_episodio_com_mais_de_90_dias_e_apagado_na_abertura(tmp_path):
    """A retenção da abertura vale para os três tipos, não só para a amostra."""
    caminho = tmp_path / "historico.db"
    agora = time.time()
    antigo = agora - 91 * DIA

    primeiro = Banco(caminho)
    primeiro.abrir_episodio("cpu", inicio=antigo, pico=90.0)
    primeiro.fechar_episodio("cpu", fim=antigo + 10)
    primeiro.fechar()

    reaberto = Banco(caminho)
    assert reaberto.episodios() == []


def test_lacuna_com_mais_de_90_dias_e_apagada_na_abertura(tmp_path):
    caminho = tmp_path / "historico.db"
    agora = time.time()
    antigo = agora - 91 * DIA

    primeiro = Banco(caminho)
    primeiro.gravar_lacuna(inicio=antigo, fim=antigo + 10)
    primeiro.fechar()

    reaberto = Banco(caminho)
    assert reaberto.lacunas() == []


def test_episodio_aberto_nao_tem_instante_de_fim(tmp_path):
    banco = Banco(tmp_path / "historico.db")
    banco.abrir_episodio("cpu", inicio=100.0, pico=90.0, programa="chrome.exe")
    episodio = banco.episodios()[0]
    assert episodio["fim"] is None


def test_fechar_episodio_preenche_o_fim_sem_criar_uma_segunda_linha(tmp_path):
    banco = Banco(tmp_path / "historico.db")
    banco.abrir_episodio("cpu", inicio=100.0, pico=90.0)
    banco.fechar_episodio("cpu", fim=160.0)
    episodios = banco.episodios()
    assert len(episodios) == 1 and episodios[0]["fim"] == 160.0


def test_atualizar_pico_do_episodio_muda_o_valor_gravado(tmp_path):
    banco = Banco(tmp_path / "historico.db")
    banco.abrir_episodio("cpu", inicio=100.0, pico=90.0)
    banco.atualizar_pico_episodio("cpu", pico=95.0)
    assert banco.episodios()[0]["pico"] == 95.0


def test_episodio_sem_programa_fica_sem_programa(tmp_path):
    banco = Banco(tmp_path / "historico.db")
    banco.abrir_episodio("cpu", inicio=100.0, pico=90.0)
    assert banco.episodios()[0]["programa"] is None


def test_lacuna_gravada_nao_tem_campo_de_valor(tmp_path):
    """Lacuna diz quanto tempo passou, nunca quanto a máquina consumiu."""
    banco = Banco(tmp_path / "historico.db")
    banco.gravar_lacuna(inicio=100.0, fim=200.0)
    lacuna = banco.lacunas()[0]
    assert "valor" not in lacuna


def test_ultimo_instante_e_o_mais_recente_entre_os_recursos(tmp_path):
    banco = Banco(tmp_path / "historico.db")
    banco.gravar_amostra("cpu", instante=100.0, valor=10.0)
    banco.gravar_amostra("ram", instante=300.0, valor=20.0)
    banco.gravar_amostra("disco", instante=200.0, valor=30.0)
    assert banco.ultimo_instante() == 300.0


def test_ultimo_instante_sem_nenhuma_amostra_e_none(tmp_path):
    banco = Banco(tmp_path / "historico.db")
    assert banco.ultimo_instante() is None


def test_amostra_com_instante_repetido_nao_substitui_a_anterior(tmp_path):
    """Relógio do sistema andando para trás não pode apagar uma linha já gravada."""
    banco = Banco(tmp_path / "historico.db")
    banco.gravar_amostra("cpu", instante=100.0, valor=10.0)
    banco.gravar_amostra("cpu", instante=100.0, valor=20.0)
    assert len(banco.amostras()) == 2


def test_amostras_sao_devolvidas_em_ordem_cronologica(tmp_path):
    banco = Banco(tmp_path / "historico.db")
    banco.gravar_amostra("cpu", instante=300.0, valor=1.0)
    banco.gravar_amostra("cpu", instante=100.0, valor=2.0)
    banco.gravar_amostra("cpu", instante=200.0, valor=3.0)
    instantes = [a["instante"] for a in banco.amostras()]
    assert instantes == sorted(instantes)
