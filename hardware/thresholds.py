import time
from enum import Enum

LIMITE_ATENCAO = 60.0
LIMITE_ALERTA = 85.0

LIMITE_TEMP_ATENCAO = 60.0
LIMITE_TEMP_ALERTA = 80.0

# O disco tem limites próprios, e dois de cada tipo. Percentual sozinho avisa tarde no
# disco pequeno (95% de 120 GB deixa 6 GB, e o Windows já não atualiza com isso) e cedo
# no grande (95% de 1 TB deixa 50 GB, que é folga). Vale o que acontecer primeiro.
LIMITE_DISCO_ATENCAO = 85.0
LIMITE_DISCO_ALERTA = 95.0
LIMITE_LIVRE_ATENCAO_GB = 20.0
LIMITE_LIVRE_ALERTA_GB = 10.0

_TEMP_IDLE = 35.0
_TEMP_CARGA_MAXIMA = 85.0


class Status(Enum):
    NORMAL = "normal"
    ATENCAO = "atencao"
    ALERTA = "alerta"


_GRAVIDADE = {Status.NORMAL: 0, Status.ATENCAO: 1, Status.ALERTA: 2}


def classificar(percentual: float) -> Status:
    if percentual >= LIMITE_ALERTA:
        return Status.ALERTA
    if percentual >= LIMITE_ATENCAO:
        return Status.ATENCAO
    return Status.NORMAL


def classificar_unidade(percentual: float, livre_gb: float) -> Status:
    """Status de uma unidade pelo pior dos dois critérios."""
    if percentual >= LIMITE_DISCO_ALERTA or livre_gb < LIMITE_LIVRE_ALERTA_GB:
        return Status.ALERTA
    if percentual >= LIMITE_DISCO_ATENCAO or livre_gb < LIMITE_LIVRE_ATENCAO_GB:
        return Status.ATENCAO
    return Status.NORMAL


def classificar_disco(leitura) -> Status:
    """Status do cartão do Disco a partir de uma `LeituraDisco`.

    Desgaste manda em tudo: é o problema que a pessoa não resolve apagando arquivo.
    Sem desgaste, vale a pior unidade — uma em Alerta leva o cartão a Alerta.
    """
    if leitura.disco_desgastado:
        return Status.ALERTA
    return mais_grave(
        classificar_unidade(u.percentual, u.livre_gb) for u in leitura.unidades
    )


def gravidade(status: Status) -> int:
    """Quanto o status pesa. Existe para ordenar, não só para comparar dois."""
    return _GRAVIDADE[status]


def mais_grave(statuses) -> Status:
    """O status mais grave da sequência. Sequência vazia é NORMAL, não erro."""
    presentes = list(statuses)
    if not presentes:
        return Status.NORMAL
    return max(presentes, key=lambda s: _GRAVIDADE[s])


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
