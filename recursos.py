"""Fonte única do que o app vigia e do que ele diz sobre cada coisa.

Fica na raiz, e não em `hardware/`, porque carrega textos de interface — e a regra do
projeto é não misturar lógica de hardware com lógica de UI. `Recurso` é entidade de
domínio, consumida pelas duas camadas.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from hardware.collector import DadosHardware
from hardware.thresholds import (
    Status,
    classificar,
    classificar_temperatura,
    estimar_temperatura,
)

CAUSA_PADRAO = "padrao"
CAUSA_ESPACO = "espaco"
CAUSA_DESGASTE = "desgaste"


@dataclass(frozen=True)
class TextoNotificacao:
    """Título e corpo de uma notificação.

    `corpo_com_programa` só é usado quando há um programa identificado; sem ele, sobra
    `corpo`, que precisa fazer sentido sozinho — nunca deixar lacuna vazia no texto.
    """

    titulo: str
    corpo: str
    corpo_com_programa: str = ""


@dataclass(frozen=True)
class Recurso:
    nome: str
    rotulo: str
    classificar: Callable[[float], Status]
    extrair: Callable[[DadosHardware], float | None]
    formatar_valor: Callable[[float], str]
    descricoes: dict[Status, dict[str, str]]
    notificacoes: dict[Status, dict[str, TextoNotificacao]] = field(
        default_factory=dict
    )
    causa_padrao: str = CAUSA_PADRAO
    notifica: bool = True
    varre_processos: bool = False
    pode_sumir: bool = False

    def descricao(self, status: Status, causa: str | None = None) -> str:
        """Texto do cartão. Status sem texto cai no do NORMAL em vez de quebrar.

        A placa de vídeo (spec 6) não tem texto de ALERTA porque nunca chega lá; se
        algo a levar até lá por engano, o app degrada em vez de derrubar a tela.
        """
        por_causa = self.descricoes.get(status) or self.descricoes[Status.NORMAL]
        return por_causa.get(causa or self.causa_padrao) or next(
            iter(por_causa.values())
        )

    def texto_notificacao(
        self,
        status: Status,
        causa: str | None = None,
        programa: str | None = None,
        valor: float | None = None,
    ) -> tuple[str, str] | None:
        """(título, corpo), ou None quando o recurso não notifica nesse status."""
        if not self.notifica:
            return None
        por_causa = self.notificacoes.get(status)
        if not por_causa:
            return None
        texto = (
            por_causa.get(causa or self.causa_padrao) or por_causa[self.causa_padrao]
        )

        if programa and texto.corpo_com_programa:
            corpo = texto.corpo_com_programa.format(
                programa=programa, valor=f"{valor:.0f}" if valor is not None else "?"
            )
        else:
            corpo = texto.corpo
        return texto.titulo, corpo


_ACAO_FECHAR = "Feche programas que não estiver usando."

CPU = Recurso(
    nome="cpu",
    rotulo="CPU",
    classificar=classificar,
    extrair=lambda dados: dados.cpu,
    formatar_valor=lambda v: f"{v:.0f}%",
    varre_processos=True,
    descricoes={
        Status.NORMAL: {
            CAUSA_PADRAO: "Desempenho estável. O sistema está operando com folga."
        },
        Status.ATENCAO: {
            CAUSA_PADRAO: "Carga moderada. Vários processos estão exigindo recursos "
            "da máquina."
        },
        Status.ALERTA: {
            CAUSA_PADRAO: "Sobrecarga de memória/processamento. Feche aplicativos "
            "inativos para evitar travamentos."
        },
    },
    notificacoes={
        Status.ALERTA: {
            CAUSA_PADRAO: TextoNotificacao(
                titulo="CPU em sobrecarga",
                corpo=_ACAO_FECHAR,
                corpo_com_programa="{programa} está usando {valor}% da CPU. "
                + _ACAO_FECHAR,
            )
        }
    },
)

RAM = Recurso(
    nome="ram",
    rotulo="RAM",
    classificar=classificar,
    extrair=lambda dados: dados.ram,
    formatar_valor=lambda v: f"{v:.0f}%",
    varre_processos=True,
    descricoes=CPU.descricoes,
    notificacoes={
        Status.ALERTA: {
            CAUSA_PADRAO: TextoNotificacao(
                titulo="Memória em sobrecarga",
                corpo=_ACAO_FECHAR,
                corpo_com_programa="{programa} está usando {valor}% da memória. "
                + _ACAO_FECHAR,
            )
        }
    },
)

DISCO = Recurso(
    nome="disco",
    rotulo="Disco",
    classificar=classificar,
    extrair=lambda dados: dados.disco,
    formatar_valor=lambda v: f"{v:.0f}%",
    causa_padrao=CAUSA_ESPACO,
    descricoes={
        Status.NORMAL: {
            CAUSA_ESPACO: "Espaço em disco suficiente. Não há risco no momento."
        },
        Status.ATENCAO: {
            CAUSA_ESPACO: "Espaço em disco diminuindo. Vale apagar arquivos que "
            "você não usa mais."
        },
        Status.ALERTA: {
            CAUSA_ESPACO: "Espaço em disco acabando. Apague arquivos grandes ou "
            "mova para outro lugar.",
            CAUSA_DESGASTE: "Disco com sinais de desgaste. Faça uma cópia dos seus "
            "arquivos importantes.",
        },
    },
    notificacoes={
        Status.ALERTA: {
            CAUSA_ESPACO: TextoNotificacao(
                titulo="Espaço em disco acabando",
                corpo="Apague arquivos grandes ou mova para outro lugar.",
            ),
            CAUSA_DESGASTE: TextoNotificacao(
                titulo="Disco com sinais de desgaste",
                corpo="Faça uma cópia dos seus arquivos importantes.",
            ),
        }
    },
)

TEMPERATURA = Recurso(
    nome="temperatura",
    rotulo="Temperatura",
    classificar=classificar_temperatura,
    extrair=lambda dados: estimar_temperatura(dados.cpu),
    formatar_valor=lambda v: f"~{v:.0f}°C",
    descricoes={
        Status.NORMAL: {
            CAUSA_PADRAO: "Temperatura dentro do esperado. O processador está "
            "operando com segurança."
        },
        Status.ATENCAO: {
            CAUSA_PADRAO: "Temperatura elevada. Verifique a ventilação do computador."
        },
        Status.ALERTA: {
            CAUSA_PADRAO: "Temperatura crítica. Feche aplicativos pesados e verifique "
            "o sistema de resfriamento."
        },
    },
    notificacoes={
        Status.ALERTA: {
            CAUSA_PADRAO: TextoNotificacao(
                titulo="Temperatura crítica",
                corpo="O processador está muito quente. Feche programas pesados e "
                "verifique a ventilação.",
            )
        }
    },
)

RECURSOS: tuple[Recurso, ...] = (CPU, RAM, DISCO, TEMPERATURA)

_ORDEM_GRAVIDADE = {Status.NORMAL: 0, Status.ATENCAO: 1, Status.ALERTA: 2}


def por_nome(nome: str) -> Recurso:
    for recurso in RECURSOS:
        if recurso.nome == nome:
            return recurso
    raise KeyError(f"recurso desconhecido: {nome}")


def pior_status(statuses) -> Status:
    """O status mais grave entre os informados.

    Recurso indisponível não é informado e portanto fica de fora — cartão que sumiu não
    pode pesar na cor do ícone da bandeja.
    """
    presentes = [s for s in statuses if s is not None]
    if not presentes:
        return Status.NORMAL
    return max(presentes, key=lambda s: _ORDEM_GRAVIDADE[s])
