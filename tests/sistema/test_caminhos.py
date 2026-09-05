import sys
from pathlib import Path
from unittest.mock import patch

from sistema import caminhos


def test_raiz_em_desenvolvimento_e_a_pasta_do_projeto():
    """Sem `_MEIPASS`, os arquivos estão ao lado do código."""
    assert (caminhos.raiz() / "main.py").is_file()


def test_raiz_empacotado_e_a_pasta_temporaria(tmp_path):
    """Arquivo único: o PyInstaller descompacta tudo e anuncia onde em `_MEIPASS`."""
    with patch.object(sys, "_MEIPASS", str(tmp_path), create=True):
        assert caminhos.raiz() == tmp_path


def test_arquivo_devolve_o_caminho_quando_existe(tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "icone.ico").write_bytes(b"")
    with patch.object(sys, "_MEIPASS", str(tmp_path), create=True):
        assert caminhos.arquivo(caminhos.ICONE) == tmp_path / "assets" / "icone.ico"


def test_arquivo_ausente_devolve_none(tmp_path):
    """Arquivo esquecido no empacotamento não pode derrubar o app de outra pessoa."""
    with patch.object(sys, "_MEIPASS", str(tmp_path), create=True):
        assert caminhos.arquivo(caminhos.ICONE) is None


def test_pasta_com_o_nome_do_arquivo_nao_conta_como_arquivo(tmp_path):
    (tmp_path / "assets" / "icone.ico").mkdir(parents=True)
    with patch.object(sys, "_MEIPASS", str(tmp_path), create=True):
        assert caminhos.arquivo(caminhos.ICONE) is None


def test_o_icone_acompanha_o_projeto():
    """Se o arquivo sumir da pasta, a janela abre sem ícone e ninguém percebe."""
    assert (
        caminhos.arquivo(caminhos.ICONE) == Path(caminhos.raiz()) / "assets/icone.ico"
    )
