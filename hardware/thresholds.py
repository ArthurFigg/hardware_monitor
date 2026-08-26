import time
from enum import Enum

LIMITE_ATENCAO = 60.0
LIMITE_ALERTA = 85.0

LIMITE_TEMP_ATENCAO = 60.0
LIMITE_TEMP_ALERTA = 80.0

_TEMP_IDLE = 35.0
_TEMP_CARGA_MAXIMA = 85.0


class Status(Enum):
    NORMAL = "normal"
    ATENCAO = "atencao"
    ALERTA = "alerta"


def classificar(percentual: float) -> Status:
    if percentual >= LIMITE_ALERTA:
        return Status.ALERTA
    if percentual >= LIMITE_ATENCAO:
        return Status.ATENCAO
    return Status.NORMAL


def classificar_temperatura(celsius: float) -> Status:
    if celsius >= LIMITE_TEMP_ALERTA:
        return Status.ALERTA
    if celsius >= LIMITE_TEMP_ATENCAO:
        return Status.ATENCAO
    return Status.NORMAL


def estimar_temperatura(cpu: float) -> float:
    return _TEMP_IDLE + (cpu / 100) * (_TEMP_CARGA_MAXIMA - _TEMP_IDLE)


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
