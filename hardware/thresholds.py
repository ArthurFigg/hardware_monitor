import time
from enum import Enum


LIMITE_ATENCAO = 60.0
LIMITE_ALERTA = 85.0


class Status(Enum):
    NORMAL = "normal"
    ATENCAO = "atencao"
    ALERTA = "alerta"


DESCRICOES = {
    Status.NORMAL: "Desempenho estável. O sistema está operando com folga.",
    Status.ATENCAO: "Carga moderada. Vários processos estão exigindo recursos da máquina.",
    Status.ALERTA: "Sobrecarga de memória/processamento. Feche aplicativos inativos para evitar travamentos.",
}


def classificar(percentual: float) -> Status:
    if percentual >= LIMITE_ALERTA:
        return Status.ALERTA
    if percentual >= LIMITE_ATENCAO:
        return Status.ATENCAO
    return Status.NORMAL


def descricao(status: Status) -> str:
    return DESCRICOES[status]


class RastreadorAlerta:
    """Garante que ALERTA só seja confirmado após sustentado pelo tempo mínimo."""

    def __init__(self, atraso: float = 5.0):
        self._atraso = atraso
        self._inicio: float | None = None

    def atualizar(self, status: Status) -> Status:
        agora = time.monotonic()
        if status == Status.ALERTA:
            if self._inicio is None:
                self._inicio = agora
            if (agora - self._inicio) < self._atraso:
                return Status.ATENCAO
            return Status.ALERTA
        self._inicio = None
        return status
