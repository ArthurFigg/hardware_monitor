"""O pouco que o app precisa lembrar entre execuções, em `%LOCALAPPDATA%`.

Nunca na pasta do app: a pasta deste projeto está dentro do OneDrive, e gravar aqui
sincronizaria arquivo sem parar. Na máquina de quem instalar, a pasta do app pode nem
ser gravável.

Nesta spec o arquivo nasce sem conteúdo próprio — o interruptor de inicialização lê o
registro, não daqui. Existe porque a spec 5 precisa lembrar se já mostrou a mensagem de
primeira vez, e inventar persistência no meio daquela spec sairia pior.
"""

import json
import os
from pathlib import Path

NOME_PASTA = "MonitorDeHardware"
NOME_ARQUIVO = "estado.json"


def pasta() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("TMP") or "."
    return Path(base) / NOME_PASTA


def caminho() -> Path:
    return pasta() / NOME_ARQUIVO


def carregar() -> dict:
    """Estado gravado, ou vazio. Arquivo corrompido conta como vazio, nunca como erro."""
    try:
        with open(caminho(), encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (OSError, json.JSONDecodeError):
        return {}
    return dados if isinstance(dados, dict) else {}


def salvar(dados: dict) -> bool:
    """Grava o estado. Devolve se conseguiu — nada aqui é essencial ao funcionamento."""
    try:
        pasta().mkdir(parents=True, exist_ok=True)
        with open(caminho(), "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def obter(chave: str, padrao=None):
    return carregar().get(chave, padrao)


def definir(chave: str, valor) -> bool:
    dados = carregar()
    dados[chave] = valor
    return salvar(dados)
