from plyer import notification

from hardware.thresholds import Status
from recursos import Recurso


class GerenciadorNotificacoes:
    """Dispara a notificação de um recurso uma vez por episódio de alerta.

    O texto vem do `Recurso` — nenhuma frase é escrita aqui. Antes existia uma mensagem
    fixa que servia os quatro recursos, e a temperatura crítica anunciava "sobrecarga de
    memória/processamento".
    """

    def __init__(self, recurso: Recurso):
        self._recurso = recurso
        self._notificado = False

    def processar(
        self,
        status: Status,
        causa: str | None = None,
        programa: str | None = None,
        valor: float | None = None,
    ) -> None:
        if status != Status.ALERTA:
            self._notificado = False
            return

        if self._notificado:
            return

        texto = self._recurso.texto_notificacao(status, causa, programa, valor)
        if texto is None:
            return

        titulo, corpo = texto
        notification.notify(title=titulo, message=corpo, timeout=5)
        self._notificado = True
