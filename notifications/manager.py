from plyer import notification

from hardware.thresholds import Status

_MENSAGEM_ALERTA = (
    "Sobrecarga de memória/processamento. "
    "Feche aplicativos inativos para evitar travamentos."
)


class GerenciadorNotificacoes:
    def __init__(self):
        self._notificado = False

    def processar(self, status: Status) -> None:
        if status == Status.ALERTA:
            if not self._notificado:
                self._disparar()
                self._notificado = True
        else:
            self._notificado = False

    def _disparar(self) -> None:
        notification.notify(
            title="Monitor de Hardware",
            message=_MENSAGEM_ALERTA,
            timeout=5,
        )
