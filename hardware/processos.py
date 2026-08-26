"""Descobre qual programa está consumindo mais de um recurso.

Roda sob demanda, só quando um recurso entra em alerta — nunca a cada ciclo de coleta.
Medido em 25/08/2026: varrer os processos custa ~163 ms, o que a cada segundo
seria 16% de um núcleo. Um monitor que come 16% de CPU para avisar que a CPU
está alta é uma piada.
"""

import time

import psutil

# O "processo" do tempo ocioso aparece com valores acima de 1000% e não é um programa.
_IGNORADOS = {"System Idle Process", "Idle"}

# Abaixo disso não vale a pena nomear ninguém — o consumo está espalhado.
_MINIMO_RELEVANTE = 1.0


def _somar_por_nome(coletar_valor) -> dict[str, float]:
    total: dict[str, float] = {}
    for processo in psutil.process_iter(["name"]):
        try:
            nome = processo.info["name"]
            if not nome or nome in _IGNORADOS:
                continue
            total[nome] = total.get(nome, 0.0) + coletar_valor(processo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return total


def programa_dominante_cpu(intervalo: float = 0.3) -> tuple[str, float] | None:
    """Programa que mais consome CPU agora, com o percentual normalizado por núcleo.

    Precisa de duas leituras espaçadas: a primeira chamada de `cpu_percent()` por
    processo sempre devolve 0.0.
    """
    for processo in psutil.process_iter():
        try:
            processo.cpu_percent()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    time.sleep(intervalo)

    nucleos = psutil.cpu_count() or 1
    total = _somar_por_nome(lambda p: p.cpu_percent() / nucleos)
    return _dominante(total)


def programa_dominante_ram() -> tuple[str, float] | None:
    """Programa que mais consome memória agora, em percentual do total."""
    return _dominante(_somar_por_nome(lambda p: p.memory_percent()))


def _dominante(total: dict[str, float]) -> tuple[str, float] | None:
    if not total:
        return None
    nome, valor = max(total.items(), key=lambda item: item[1])
    if valor < _MINIMO_RELEVANTE:
        return None
    return nome, min(valor, 100.0)


def programa_dominante(recurso: str) -> tuple[str, float] | None:
    """Ponto de entrada por recurso. Só CPU e RAM têm programa associado."""
    if recurso == "cpu":
        return programa_dominante_cpu()
    if recurso == "ram":
        return programa_dominante_ram()
    return None
