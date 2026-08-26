from dataclasses import dataclass

import psutil

from hardware import desempenho, discos
from hardware.discos import LeituraDisco


@dataclass
class DadosHardware:
    cpu: float
    ram: float
    disco: LeituraDisco
    velocidade: float | None = None
    reduzindo: bool = False


def coletar() -> DadosHardware:
    """Uma leitura completa da máquina.

    A janela de 5 s do aviso de calor avança aqui, e só aqui: é o único ponto que roda
    uma vez por ciclo. Deixá-la em quem lê os dados faria o relógio andar mais rápido a
    cada consumidor novo — a bandeja da spec 5 encurtaria a janela pela metade sem que
    ninguém percebesse.
    """
    cpu = psutil.cpu_percent(interval=1)
    velocidade = desempenho.velocidade_processador()
    return DadosHardware(
        cpu=cpu,
        ram=psutil.virtual_memory().percent,
        disco=discos.ler(),
        velocidade=velocidade,
        reduzindo=desempenho.confirmar_reducao(cpu, velocidade),
    )
