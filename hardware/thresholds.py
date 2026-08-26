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


DESCRICOES = {
    Status.NORMAL: "Desempenho estável. O sistema está operando com folga.",
    Status.ATENCAO: "Carga moderada. Vários processos estão exigindo recursos da máquina.",
    Status.ALERTA: "Sobrecarga de memória/processamento. Feche aplicativos inativos para evitar travamentos.",
}

DESCRICOES_TEMPERATURA = {
    Status.NORMAL: "Temperatura dentro do esperado. O processador está operando com segurança.",
    Status.ATENCAO: "Temperatura elevada. Verifique a ventilação do computador.",
    Status.ALERTA: "Temperatura crítica. Feche aplicativos pesados e verifique o sistema de resfriamento.",
}


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


def descricao(status: Status) -> str:
    return DESCRICOES[status]


def descricao_temperatura(status: Status) -> str:
    return DESCRICOES_TEMPERATURA[status]


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
