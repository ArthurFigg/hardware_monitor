import time
from enum import Enum

LIMITE_ATENCAO = 60.0
LIMITE_ALERTA = 85.0

# 65°C corresponde exatamente a CPU 60%, o mesmo ponto em que o cartão de CPU acende.
# Com 60°C a temperatura acendia em CPU 50% — antes da CPU —, e toda carga entre 50% e
# 59% mostrava amarelo na Temperatura com a CPU em verde. O Alerta continua em 80°C
# (CPU 90%) de propósito: calor demora a subir, então temperatura atrasada em relação à
# carga é fisicamente correto. O defeito era estar adiantada.
LIMITE_TEMP_ATENCAO = 65.0
LIMITE_TEMP_ALERTA = 80.0

# Carga alta com velocidade baixa é o processador se protegendo do calor. As duas juntas
# são obrigatórias: o contador também cai com o PC ocioso, e ali a queda é economia de
# energia, não calor. O 90% é fundamentado e não medido — não dá para provocar
# superaquecimento real —, então é o primeiro número a ajustar se o aviso nunca aparecer
# ou aparecer demais.
LIMITE_CARGA_REDUCAO = 85.0
LIMITE_VELOCIDADE_REDUCAO = 90.0

# Placa de vídeo em 100% durante um jogo é o esperado — é para estar assim. Usar os 60 e
# 85 de CPU e RAM deixaria o cartão amarelo o jogo inteiro e vermelho sem nada errado. O
# único caso em que o número significa algo para este público é a placa no limite de forma
# sustentada, que explica o jogo engasgando e tem ação clara: baixar a qualidade gráfica.
# Não mudar para 60/85 "por consistência": a inconsistência aqui é proposital.
LIMITE_PLACA_ATENCAO = 95.0

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


def reduzindo_por_calor(cpu: float, velocidade: float | None) -> bool:
    """Carga alta e processador freado ao mesmo tempo. Sem velocidade, não se afirma nada."""
    if velocidade is None:
        return False
    return cpu >= LIMITE_CARGA_REDUCAO and velocidade < LIMITE_VELOCIDADE_REDUCAO


class ConfirmadorSustentado:
    """Só confirma uma condição depois dela se manter pelo tempo mínimo.

    Mesma ideia do `RastreadorAlerta`, mas sobre um booleano em vez de um `Status` — ele
    continua como está porque é de outra spec e funciona; unificar os dois é refatoração
    a combinar, não efeito colateral desta.
    """

    def __init__(self, atraso: float = 5.0):
        self._atraso = atraso
        self._inicio: float | None = None

    def atualizar(self, condicao: bool) -> bool:
        if not condicao:
            self._inicio = None
            return False
        agora = time.monotonic()
        if self._inicio is None:
            self._inicio = agora
        return (agora - self._inicio) >= self._atraso


def menos_grave(a: Status, b: Status) -> Status:
    """O menos grave dos dois. Usado para o que o cartão exibe nunca passar do que o
    app já confirmou — a janela de 5 s vale para a tela também."""
    return min((a, b), key=gravidade)


def gravidade(status: Status) -> int:
    """Quanto o status pesa. Existe para ordenar, não só para comparar dois."""
    return _GRAVIDADE[status]


def mais_grave(statuses) -> Status:
    """O status mais grave da sequência. Sequência vazia é NORMAL, não erro."""
    presentes = list(statuses)
    if not presentes:
        return Status.NORMAL
    return max(presentes, key=lambda s: _GRAVIDADE[s])


def placa_no_limite(uso: float) -> bool:
    """Acima de 95%, e não a partir de 95%: em 95 redondo ainda há folga."""
    return uso > LIMITE_PLACA_ATENCAO


def classificar_placa_video(leitura) -> Status:
    """Status do cartão da placa. **Nunca** chega a Alerta.

    Placa no limite não é emergência e não tem ação urgente — por isso não existe
    vermelho aqui. `no_limite` já vem com a confirmação de 5 segundos aplicada na coleta.
    """
    return Status.ATENCAO if getattr(leitura, "no_limite", False) else Status.NORMAL


def classificar_temperatura(celsius: float) -> Status:
    if celsius >= LIMITE_TEMP_ALERTA:
        return Status.ALERTA
    if celsius >= LIMITE_TEMP_ATENCAO:
        return Status.ATENCAO
    return Status.NORMAL


def estimar_temperatura(cpu: float) -> float:
    return _TEMP_IDLE + (cpu / 100) * (_TEMP_CARGA_MAXIMA - _TEMP_IDLE)


# Para o que cada status cai enquanto a confirmação não vem.
_ENQUANTO_ESPERA = {Status.ALERTA: Status.ATENCAO, Status.ATENCAO: Status.NORMAL}


class RastreadorAlerta:
    """Confirma um status só depois dele se manter pelo tempo mínimo.

    Por padrão vigia o ALERTA e devolve ATENCAO enquanto espera, que é o comportamento
    de sempre. A placa de vídeo pede o mesmo para o ATENCAO dela, porque nunca chega a
    Alerta — e sem isso o cartão piscaria amarelo a cada pico de um segundo.
    """

    def __init__(
        self,
        atraso: float = 5.0,
        confirmar: Status = Status.ALERTA,
        enquanto_espera: Status | None = None,
    ):
        self._atraso = atraso
        self._confirmar = confirmar
        self._enquanto_espera = enquanto_espera or _ENQUANTO_ESPERA[confirmar]
        self._inicio: float | None = None

    def atualizar(self, status: Status) -> Status:
        agora = time.monotonic()
        if status == self._confirmar:
            if self._inicio is None:
                self._inicio = agora
            if (agora - self._inicio) < self._atraso:
                return self._enquanto_espera
            return self._confirmar
        self._inicio = None
        return status
