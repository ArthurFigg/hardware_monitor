"""Gera `assets/icone.ico` a partir do mesmo desenho que o app usa na bandeja.

Roda à mão, quando o ícone precisar mudar: `uv run python assets/gerar_icone.py`.
O `.ico` fica versionado — o build não depende deste script.

O ícone do executável é fixo em verde. O da bandeja muda de cor com o estado, mas o do
arquivo é a identidade do app, não um indicador: um `.exe` que troca de ícone conforme a
máquina seria confuso na barra de tarefas e impossível no Explorer.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

# `assets/` guarda dados, não é pacote — rodando o script daqui a raiz do projeto não
# entra no caminho de importação sozinha. A cor vem do semáforo de propósito: o ícone do
# app e a luz da tela não podem divergir.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hardware.thresholds import Status
from ui.components.semaphore import CORES

# O Windows escolhe o tamanho conforme o contexto — 16 na barra de tarefas, 256 na
# visualização grande do Explorer. Sem os tamanhos pequenos ele reduz o maior e borra.
TAMANHOS = [16, 24, 32, 48, 64, 128, 256]

_FUNDO = "#1F1F1F"
_DESTINO = Path(__file__).resolve().parent / "icone.ico"


def desenhar(tamanho: int) -> Image.Image:
    imagem = Image.new("RGBA", (tamanho, tamanho), (0, 0, 0, 0))
    desenho = ImageDraw.Draw(imagem)

    # Disco escuro atrás do círculo colorido: sem ele o verde some sobre papel de parede
    # claro, e o ícone vira uma mancha.
    desenho.ellipse((0, 0, tamanho - 1, tamanho - 1), fill=_FUNDO)

    margem = max(2, round(tamanho * 0.22))
    desenho.ellipse(
        (margem, margem, tamanho - 1 - margem, tamanho - 1 - margem),
        fill=CORES[Status.NORMAL],
    )
    return imagem


def main() -> None:
    imagens = [desenhar(t) for t in TAMANHOS]
    imagens[-1].save(_DESTINO, format="ICO", sizes=[(t, t) for t in TAMANHOS])
    print(f"gerado: {_DESTINO} ({_DESTINO.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
