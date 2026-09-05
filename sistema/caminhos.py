"""Onde estão os arquivos que o app carrega junto, com executável ou sem ele.

Empacotado em arquivo único, o PyInstaller descompacta tudo numa pasta temporária a cada
abertura e guarda o caminho dela em `sys._MEIPASS`. Caminho relativo à pasta do projeto
só funciona em desenvolvimento: na máquina de quem baixou, essa pasta não existe.
"""

import sys
from pathlib import Path

ICONE = "assets/icone.ico"

_RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent


def raiz() -> Path:
    """Pasta onde os arquivos acompanhantes estão nesta execução."""
    temporaria = getattr(sys, "_MEIPASS", None)
    return Path(temporaria) if temporaria else _RAIZ_DO_PROJETO


def arquivo(relativo: str) -> Path | None:
    """Caminho de um arquivo acompanhante, ou None se ele não veio junto.

    Devolve None em vez de levantar erro porque arquivo esquecido no empacotamento é
    exatamente o defeito que não pode derrubar o app na máquina de outra pessoa.
    """
    caminho = raiz() / relativo
    return caminho if caminho.is_file() else None
