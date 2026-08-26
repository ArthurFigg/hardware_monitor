"""Velocidade real do processador e o aviso de que ele freou para não esquentar.

`psutil.cpu_freq()` não serve aqui: nesta máquina devolve 3701 MHz parado ou sob carga,
porque lê a frequência nominal do registro, não o clock real. O contador
`% Processor Performance` é o que o Gerenciador de Tarefas mostra, e passa de 100%
quando há turbo — 120% em repouso nesta máquina.
"""

from dataclasses import dataclass

from hardware import pdh
from hardware.thresholds import ConfirmadorSustentado, reduzindo_por_calor

# Turbo passa de 100%, então o teto tem que ser folgado. Acima disso é leitura corrompida,
# não processador rápido.
_TETO_PLAUSIVEL = 1000.0


@dataclass(frozen=True)
class LeituraTemperatura:
    """Temperatura estimada mais o aviso de redução, que anda junto dela no cartão."""

    celsius: float
    reduzindo: bool = False


_contador: pdh.Contador | None = None
_tentou_abrir = False


def _obter_contador() -> pdh.Contador | None:
    """Abre a consulta na primeira leitura, e uma vez só.

    Preguiçoso de propósito: importar o módulo não pode abrir consulta ao Windows, ou o
    CI (que roda em Linux) quebraria no import.
    """
    global _contador, _tentou_abrir
    if _tentou_abrir:
        return _contador
    _tentou_abrir = True
    contador = pdh.Contador(
        pdh.IDX_PROCESSOR_INFORMATION,
        pdh.IDX_PROCESSOR_PERFORMANCE,
        "Processor Information",
        "% Processor Performance",
    )
    _contador = contador if contador.ok else None
    return _contador


def velocidade_processador() -> float | None:
    """Velocidade atual em % do nominal, ou None quando não dá para saber."""
    contador = _obter_contador()
    if contador is None:
        return None
    try:
        valor = contador.ler()
    except OSError:
        # `pdh.py` já se protege; esta é a fronteira que a spec encarrega de nunca
        # deixar passar erro para o cartão, mesmo que o contador venha de outro lugar.
        return None
    if valor is None or valor < 0 or valor > _TETO_PLAUSIVEL:
        return None
    return valor


_confirmador = ConfirmadorSustentado()


def confirmar_reducao(cpu: float, velocidade: float | None) -> bool:
    """Aplica a regra e a janela de 5 s. Uma queda de um segundo não pisca na tela."""
    return _confirmador.atualizar(reduzindo_por_calor(cpu, velocidade))
