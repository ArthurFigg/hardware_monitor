"""Entrada do app na chave `Run` do usuário — abrir junto com o Windows.

Fica em `sistema/` e não em `hardware/` porque mexer no registro é integração com o
sistema operacional, não coleta de hardware.

A entrada no registro **é** o estado do interruptor. Não há arquivo de configuração
espelhando isso, e é de propósito: assim o interruptor não tem como discordar da
realidade, nem quando a pessoa remove a entrada por fora, pelo Gerenciador de Tarefas.
"""

import sys
from pathlib import Path

try:
    import winreg
except ImportError:  # Linux, onde o CI roda
    winreg = None

NOME_ENTRADA = "MonitorDeHardware"
CHAVE_RUN = r"Software\Microsoft\Windows\CurrentVersion\Run"

# Todas as 10 entradas já presentes nesta máquina usam alguma variação de silencioso.
# O `.exe` da spec 7 precisa aceitar exatamente este argumento.
ARGUMENTO_MINIMIZADO = "--minimizado"


def _empacotado() -> bool:
    """True quando rodando a partir do `.exe` da spec 7, em vez do interpretador."""
    return getattr(sys, "frozen", False)


def comando() -> str:
    """Linha de comando a gravar no registro, resolvida em tempo de execução.

    Nunca um caminho fixo: na máquina de quem instalou, a pasta deste projeto não existe.
    Em desenvolvimento aponta para o `pythonw.exe` do ambiente — `pythonw` e não
    `python`, senão uma janela preta de terminal pisca a cada boot.
    """
    if _empacotado():
        return f'"{sys.executable}" {ARGUMENTO_MINIMIZADO}'

    interpretador = Path(sys.executable)
    sem_console = interpretador.with_name("pythonw.exe")
    if sem_console.exists():
        interpretador = sem_console

    script = Path(__file__).resolve().parent.parent / "main.py"
    return f'"{interpretador}" "{script}" {ARGUMENTO_MINIMIZADO}'


def ativado() -> bool:
    """Se a entrada existe agora. Leitura que falha responde 'não', nunca levanta erro."""
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CHAVE_RUN) as chave:
            winreg.QueryValueEx(chave, NOME_ENTRADA)
        return True
    except OSError:
        return False


def ativar() -> bool:
    """Grava a entrada. Devolve se conseguiu — quem chamou precisa saber.

    Diferente da regra geral de "leitura que falha esconde a si mesma": aqui é ação que a
    pessoa pediu, e falhar calado deixaria a caixa marcada com o app não abrindo no boot.
    """
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, CHAVE_RUN, 0, winreg.KEY_SET_VALUE
        ) as chave:
            winreg.SetValueEx(chave, NOME_ENTRADA, 0, winreg.REG_SZ, comando())
        return True
    except OSError:
        return False


def desativar() -> bool:
    """Remove a entrada. Entrada que já não existia conta como sucesso."""
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, CHAVE_RUN, 0, winreg.KEY_SET_VALUE
        ) as chave:
            winreg.DeleteValue(chave, NOME_ENTRADA)
        return True
    except FileNotFoundError:
        return True
    except OSError:
        return False


def iniciado_minimizado(argumentos=None) -> bool:
    """Se o app subiu pela entrada do registro, e portanto não deve roubar a tela."""
    argv = sys.argv[1:] if argumentos is None else argumentos
    return ARGUMENTO_MINIMIZADO in argv
