"""Quanto a placa de vídeo está sendo usada, pelo contador do Windows.

`psutil` não tem nada para placa de vídeo — verificado, não existe função. A leitura sai
do mesmo mecanismo PDH que o contador de velocidade do processador usa.

O contador lista um motor por processo e por tipo (3D, cópia, decodificação, codificação
de vídeo) — 336 instâncias nesta máquina. Somar tudo daria número acima de 100% sem
sentido. O que vale é o **maior valor entre os tipos de motor**, que é o número que o
Gerenciador de Tarefas mostra e portanto o que a pessoa reconhece.
"""

from dataclasses import dataclass

from hardware import pdh
from hardware.thresholds import RastreadorAlerta, Status, placa_no_limite

# Este contador não é traduzido: num Windows em português ele continua em inglês, e
# procurar o nome local devolve vazio. Aqui a queda para o inglês não é precaução, é o
# caminho único.
CAMINHO = r"\GPU Engine(*)\Utilization Percentage"

_TETO_PLAUSIVEL = 100.0


@dataclass(frozen=True)
class LeituraPlaca:
    """Uso da placa mais o "está no limite" já confirmado."""

    uso: float
    no_limite: bool = False


_contador: pdh.ContadorVetor | None = None
_tentou_abrir = False

# Vigia o ATENCAO e não o ALERTA: a placa nunca chega a Alerta, e sem a confirmação o
# cartão piscaria amarelo a cada pico de um segundo.
_rastreador = RastreadorAlerta(confirmar=Status.ATENCAO)


def _obter_contador() -> pdh.ContadorVetor | None:
    """Abre a consulta na primeira leitura, e uma vez só."""
    global _contador, _tentou_abrir
    if _tentou_abrir:
        return _contador
    _tentou_abrir = True
    contador = pdh.ContadorVetor(CAMINHO)
    _contador = contador if contador.ok else None
    return _contador


_MARCA_TIPO = "engtype_"
_MARCA_PLACA = "_luid_"
_MARCA_MOTOR = "_eng_"


def tipo_de_motor(instancia: str) -> str:
    """O que vem depois de `engtype_` no nome da instância.

    Nome típico: `pid_10060_luid_..._phys_0_eng_0_engtype_3D`. Instância sem esse trecho
    é agrupada à parte em vez de virar erro.
    """
    if _MARCA_TIPO not in instancia:
        return "desconhecido"
    return instancia.split(_MARCA_TIPO, 1)[1].strip()


def placa_de_motor(instancia: str) -> str:
    """Qual placa física a instância descreve, pelo `luid` e pelo `phys` do nome.

    Máquina com placa integrada **e** dedicada lista as duas. Sem separá-las, o motor 3D
    de uma somaria com o da outra e o cartão mostraria número alto sem que nenhuma das
    duas estivesse no limite.
    """
    if _MARCA_PLACA not in instancia:
        return "desconhecida"
    depois = instancia.split(_MARCA_PLACA, 1)[1]
    return depois.split(_MARCA_MOTOR, 1)[0]


def agregar(leituras) -> float | None:
    """Maior uso entre os motores, somando só os processos que dividem o mesmo motor.

    Somar tudo daria acima de 100%; pegar o maior valor solto ignoraria dois programas
    usando o mesmo motor ao mesmo tempo. O agrupamento é por placa **e** tipo: numa
    máquina com integrada e dedicada, somar o 3D das duas inventaria carga que nenhuma
    delas tem.
    """
    if not leituras:
        return None

    por_motor: dict[tuple[str, str], float] = {}
    for instancia, valor in leituras:
        if valor is None or valor < 0:
            continue
        chave = (placa_de_motor(instancia), tipo_de_motor(instancia))
        por_motor[chave] = por_motor.get(chave, 0.0) + valor

    if not por_motor:
        return None
    return min(max(por_motor.values()), _TETO_PLAUSIVEL)


def uso() -> float | None:
    """Uso atual da placa em percentual, ou None quando não dá para saber.

    `None` some com o cartão inteiro: sem contador não há número para mostrar. Diferente
    de máquina sem placa dedicada, onde o contador responde e o número é baixo e real.
    """
    contador = _obter_contador()
    if contador is None:
        return None
    try:
        leituras = contador.ler()
    except OSError:
        return None
    return agregar(leituras)


def ler() -> LeituraPlaca | None:
    """Leitura completa para um ciclo de coleta.

    A janela de 5 s avança aqui, e só aqui: é o ponto que roda uma vez por ciclo. Em quem
    lê os dados, cada consumidor novo faria o relógio andar mais rápido.
    """
    atual = uso()
    if atual is None:
        return None

    bruto = Status.ATENCAO if placa_no_limite(atual) else Status.NORMAL
    return LeituraPlaca(
        uso=atual, no_limite=_rastreador.atualizar(bruto) is Status.ATENCAO
    )
