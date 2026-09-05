import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sistema import inicializacao


@pytest.fixture
def registro():
    """`winreg` inteiro trocado — nenhum teste pode escrever no registro de verdade."""
    falso = MagicMock()
    falso.HKEY_CURRENT_USER = 0
    falso.KEY_SET_VALUE = 2
    falso.REG_SZ = 1
    with patch.object(inicializacao, "winreg", falso):
        yield falso


def test_ativado_quando_a_entrada_existe(registro):
    registro.QueryValueEx.return_value = ("comando", 1)
    assert inicializacao.ativado()


def test_desativado_quando_a_entrada_nao_existe(registro):
    registro.OpenKey.side_effect = FileNotFoundError
    assert not inicializacao.ativado()


def test_leitura_bloqueada_conta_como_desativado(registro):
    """Política corporativa negando leitura não pode virar exceção na abertura da janela."""
    registro.OpenKey.side_effect = PermissionError
    assert not inicializacao.ativado()


def test_ativar_grava_a_entrada(registro):
    assert inicializacao.ativar()
    registro.SetValueEx.assert_called_once()


def test_ativar_grava_com_o_nome_esperado(registro):
    inicializacao.ativar()
    assert registro.SetValueEx.call_args.args[1] == inicializacao.NOME_ENTRADA


def test_ativar_com_escrita_bloqueada_devolve_falha(registro):
    """Antivírus bloqueando: quem chamou precisa saber para desmarcar o interruptor."""
    registro.SetValueEx.side_effect = PermissionError
    assert not inicializacao.ativar()


def test_desativar_remove_a_entrada(registro):
    assert inicializacao.desativar()
    registro.DeleteValue.assert_called_once()


def test_desativar_entrada_inexistente_conta_como_sucesso(registro):
    """A pessoa pode ter removido por fora, pelo Gerenciador de Tarefas."""
    registro.DeleteValue.side_effect = FileNotFoundError
    assert inicializacao.desativar()


def test_desativar_bloqueado_devolve_falha(registro):
    registro.DeleteValue.side_effect = PermissionError
    assert not inicializacao.desativar()


def test_sem_winreg_nao_quebra():
    """O CI roda em Linux, onde `winreg` não existe."""
    with patch.object(inicializacao, "winreg", None):
        assert not inicializacao.ativado()
        assert not inicializacao.ativar()


def test_comando_em_desenvolvimento_usa_pythonw():
    """`python.exe` piscaria uma janela preta de terminal a cada boot."""
    with (
        patch.object(inicializacao.sys, "executable", r"C:\Py\python.exe"),
        patch.object(Path, "exists", return_value=True),
        patch.object(inicializacao, "_empacotado", return_value=False),
    ):
        assert "pythonw.exe" in inicializacao.comando()


def test_comando_em_desenvolvimento_aponta_para_o_main():
    with (
        patch.object(inicializacao.sys, "executable", r"C:\Py\python.exe"),
        patch.object(Path, "exists", return_value=True),
        patch.object(inicializacao, "_empacotado", return_value=False),
    ):
        assert "main.py" in inicializacao.comando()


def test_comando_empacotado_aponta_para_o_executavel():
    """Na versão distribuída não há `main.py` nem interpretador separado."""
    with (
        patch.object(inicializacao.sys, "executable", r"C:\Apps\Monitor.exe"),
        patch.object(inicializacao, "_empacotado", return_value=True),
    ):
        comando = inicializacao.comando()
    assert comando == r'"C:\Apps\Monitor.exe" --minimizado'


def test_comando_sempre_pede_para_abrir_minimizado():
    assert inicializacao.ARGUMENTO_MINIMIZADO in inicializacao.comando()


def test_comando_acompanha_o_interpretador_em_uso():
    """Caminho fixo no código daria o mesmo comando em qualquer máquina.

    Em desenvolvimento o comando contém o caminho desta máquina — é onde o app está
    rodando de fato. O que não pode existir é o caminho escrito no código-fonte.
    """
    with (
        patch.object(inicializacao.sys, "executable", r"D:\Outro\python.exe"),
        patch.object(Path, "exists", return_value=False),
        patch.object(inicializacao, "_empacotado", return_value=False),
    ):
        comando = inicializacao.comando()
    assert comando.startswith(r'"D:\Outro\python.exe"')


def test_codigo_nao_tem_caminho_de_maquina_escrito():
    """A pasta deste projeto não existe na máquina de quem instalar."""
    fonte = Path(inicializacao.__file__).read_text(encoding="utf-8")
    for marca in ("C:\\Users", "OneDrive", ".venv"):
        assert marca not in fonte


def test_comando_resolve_o_interpretador_em_tempo_de_execucao():
    assert str(Path(sys.executable).parent) in inicializacao.comando()


def test_iniciado_minimizado_com_o_argumento():
    assert inicializacao.iniciado_minimizado(["--minimizado"])


def test_iniciado_minimizado_sem_o_argumento():
    assert not inicializacao.iniciado_minimizado([])


def test_valor_gravado_devolve_o_comando(registro):
    registro.QueryValueEx.return_value = (r'"C:\Programas\app.exe" --minimizado', 1)
    assert inicializacao.valor_gravado() == r'"C:\Programas\app.exe" --minimizado'


def test_valor_gravado_sem_entrada_devolve_none(registro):
    registro.OpenKey.side_effect = FileNotFoundError
    assert inicializacao.valor_gravado() is None


@patch.object(inicializacao, "_empacotado", return_value=True)
def test_sincronizar_reescreve_quando_o_caminho_mudou(_, registro):
    """A pessoa arrastou o executável para outra pasta depois de ligar o interruptor."""
    registro.QueryValueEx.return_value = (r'"D:\antiga\app.exe" --minimizado', 1)
    assert inicializacao.sincronizar()
    assert registro.SetValueEx.call_args.args[4] == inicializacao.comando()


@patch.object(inicializacao, "_empacotado", return_value=True)
def test_sincronizar_nao_mexe_quando_o_caminho_confere(_, registro):
    registro.QueryValueEx.return_value = (inicializacao.comando(), 1)
    assert not inicializacao.sincronizar()


@patch.object(inicializacao, "_empacotado", return_value=True)
def test_sincronizar_nao_cria_entrada_que_nao_existia(_, registro):
    """Ausência é a resposta 'não quero abrir com o Windows', não caminho velho."""
    registro.OpenKey.side_effect = FileNotFoundError
    assert not inicializacao.sincronizar()
    registro.SetValueEx.assert_not_called()


@patch.object(inicializacao, "_empacotado", return_value=True)
def test_sincronizar_com_escrita_bloqueada_devolve_falha(_, registro):
    registro.QueryValueEx.return_value = (r'"D:\antiga\app.exe" --minimizado', 1)
    registro.SetValueEx.side_effect = PermissionError
    assert not inicializacao.sincronizar()


def test_sincronizar_rodando_pelo_codigo_nao_mexe_no_registro(registro):
    """Teste em desenvolvimento não pode roubar a entrada do programa empacotado."""
    registro.QueryValueEx.return_value = (r'"C:\Programaspp.exe" --minimizado', 1)
    with patch.object(inicializacao, "_empacotado", return_value=False):
        assert not inicializacao.sincronizar()
    registro.SetValueEx.assert_not_called()
