"""Ícone ao lado do relógio, colorido pelo pior status do momento.

Duas regras de thread valem aqui, em direções opostas:

- Atualizar a cor do ícone **a partir da thread do Tkinter** é seguro, e é assim que se faz.
- A thread do `pystray` **nunca** pode mexer em widget do Tkinter. Por isso as ações do menu
  recebem funções prontas de quem chamou, e quem chamou é responsável por passá-las por
  `widget.after(0, ...)`. Este módulo não conhece widget nenhum.

Sem `pystray` instalado ou sem bandeja no ambiente, `disponivel` fica falso e o app volta ao
comportamento de antes: sem ícone, e fechar a janela encerra.
"""

from collections.abc import Callable

from hardware.thresholds import Status
from ui.components.semaphore import CORES

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover - depende do ambiente, não da lógica
    pystray = None
    Image = None
    ImageDraw = None

TITULO = "Monitor de Hardware"

# Sem jargão e sem tom de assistente, como o resto da interface.
RESUMOS = {
    Status.NORMAL: "tudo em ordem",
    Status.ATENCAO: "algo exigindo atenção",
    Status.ALERTA: "algo precisando de ação",
}

_TAMANHO = 64
_MARGEM = 6


def descricao(status: Status) -> str:
    """Texto que aparece ao passar o mouse sobre o ícone."""
    return f"{TITULO} — {RESUMOS[status]}"


def desenhar(status: Status, tamanho: int = _TAMANHO):
    """Círculo cheio na cor do status. Mesma paleta do semáforo, sem inventar outra."""
    imagem = Image.new("RGBA", (tamanho, tamanho), (0, 0, 0, 0))
    ImageDraw.Draw(imagem).ellipse(
        (_MARGEM, _MARGEM, tamanho - _MARGEM, tamanho - _MARGEM),
        fill=CORES[status],
    )
    return imagem


class Bandeja:
    """O ícone e o menu. Construir não levanta erro quando a bandeja não existe."""

    def __init__(self, ao_abrir: Callable[[], None], ao_sair: Callable[[], None]):
        self._ao_abrir = ao_abrir
        self._ao_sair = ao_sair
        self._icone = None
        self._status = None
        self.disponivel = pystray is not None

    @property
    def ativo(self) -> bool:
        """Se o ícone está no ar agora.

        Diferente de `disponivel`, que só diz que a biblioteca existe. Esconder a janela
        depende deste: sem ícone no ar, esconder deixaria o app sem como ser reaberto.
        """
        return self._icone is not None

    def iniciar(self, status: Status = Status.NORMAL) -> bool:
        """Sobe o ícone numa thread própria. Devolve se conseguiu."""
        if not self.disponivel:
            return False
        try:
            self._icone = pystray.Icon(
                "monitor_de_hardware",
                icon=desenhar(status),
                title=descricao(status),
                menu=self._menu(),
            )
            self._icone.run_detached()
        except (OSError, ImportError, NotImplementedError, RuntimeError):
            # A bandeja é enfeite: ambiente sem área de notificação não pode impedir o
            # app de abrir. Cada backend do `pystray` falha de um jeito — `OSError` no
            # Windows sem área de notificação, `ImportError` quando não há backend,
            # `NotImplementedError` onde `run_detached` não existe.
            self._icone = None
            self.disponivel = False
            return False

        self._status = status
        return True

    def _menu(self):
        return pystray.Menu(
            pystray.MenuItem("Abrir", lambda *_: self._ao_abrir(), default=True),
            pystray.MenuItem("Sair", lambda *_: self._ao_sair()),
        )

    def atualizar(self, status: Status) -> None:
        """Troca a cor, e só quando o status muda de fato.

        Redesenhar a cada ciclo custaria uma imagem por segundo para nada.
        """
        if self._icone is None or status == self._status:
            return
        self._status = status
        self._icone.icon = desenhar(status)
        self._icone.title = descricao(status)

    def parar(self) -> None:
        if self._icone is None:
            return
        self._icone.stop()
        self._icone = None
