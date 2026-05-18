from dataclasses import dataclass

import psutil


@dataclass
class DadosHardware:
    cpu: float
    ram: float
    disco: float


def coletar() -> DadosHardware:
    return DadosHardware(
        cpu=psutil.cpu_percent(interval=1),
        ram=psutil.virtual_memory().percent,
        disco=psutil.disk_usage("/").percent,
    )
