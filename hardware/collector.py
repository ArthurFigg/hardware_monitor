from dataclasses import dataclass

import psutil

from hardware import discos
from hardware.discos import LeituraDisco


@dataclass
class DadosHardware:
    cpu: float
    ram: float
    disco: LeituraDisco


def coletar() -> DadosHardware:
    return DadosHardware(
        cpu=psutil.cpu_percent(interval=1),
        ram=psutil.virtual_memory().percent,
        disco=discos.ler(),
    )
