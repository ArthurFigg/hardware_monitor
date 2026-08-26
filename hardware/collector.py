import time
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


def segundos_ligado() -> float | None:
    """Há quanto tempo a máquina está ligada, ou None quando não dá para saber.

    Da máquina, não do app: é o que interessa a quem quer saber como ela se comportou.
    Não entra em `DadosHardware` porque muda de minuto em minuto, e o resto do ciclo
    roda a cada segundo.
    """
    try:
        return time.time() - psutil.boot_time()
    except (OSError, RuntimeError):
        return None


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
