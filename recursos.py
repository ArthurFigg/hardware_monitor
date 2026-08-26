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
    classificar_disco,
    classificar_temperatura,
    estimar_temperatura,
    mais_grave,
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
    causa_fn: Callable[[object], str] | None = None
    linha_extra_fn: Callable[[object], str] | None = None
    detalhe_fn: Callable[[object], str] | None = None
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

    def descricao_de(self, status: Status, valor=None) -> str:
        """Texto do cartão já resolvido para esta leitura.

        É o que o cartão chama. `descricao()` continua existindo para quem já sabe a
        causa; aqui ela é derivada do valor, que é o que a tela tem em mãos.
        """
        return self.descricao(status, self.causa(valor))

    def causa(self, valor=None) -> str:
        """Qual variante de texto vale para esta leitura.

        Só o Disco varia: falta de espaço e desgaste pedem conselhos opostos. Quem não
        declara `causa_fn` fica na causa padrão para sempre.
        """
        if self.causa_fn is None or valor is None:
            return self.causa_padrao
        return self.causa_fn(valor)

    def linha_extra(self, valor=None) -> str:
        """Linha abaixo da descrição no cartão. Vazia é o normal, e o cartão a esconde."""
        if self.linha_extra_fn is None or valor is None:
            return ""
        return self.linha_extra_fn(valor)

    def texto_notificacao(
        self,
        status: Status,
        causa: str | None = None,
        programa: str | None = None,
        valor: float | None = None,
        leitura=None,
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

        detalhe = self._detalhe(leitura)
        if detalhe:
            corpo = f"{detalhe} {corpo}"
        return texto.titulo, corpo

    def _detalhe(self, leitura) -> str:
        """Frase de dados que antecede a ação, quando o recurso souber os números."""
        if self.detalhe_fn is None or leitura is None:
            return ""
        return self.detalhe_fn(leitura)


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

_LINHA_DESGASTE = "O disco {disco} está dando sinais de desgaste."
_DESGASTE = (
    "Disco com sinais de desgaste. Faça uma cópia dos seus arquivos importantes."
)


def _valor_disco(leitura) -> str:
    """Percentual da unidade que decidiu o status, com o nome dela.

    Sem nenhuma unidade — todas filtradas — o cartão não exibe número nenhum. Vazio é
    melhor que "0%", que seria mentira sobre um disco que o app não está olhando.
    """
    unidade = getattr(leitura, "pior_unidade", None)
    if unidade is None:
        return ""
    return f"{unidade.ponto} — {unidade.percentual:.0f}%"


def _linha_desgaste(leitura) -> str:
    if not getattr(leitura, "disco_desgastado", None):
        return ""
    return _LINHA_DESGASTE.format(disco=leitura.disco_desgastado)


def _detalhe_disco(leitura) -> str:
    """Quanto sobrou e onde. Não sai no alerta de desgaste: lá o espaço é irrelevante."""
    unidade = getattr(leitura, "pior_unidade", None)
    if unidade is None or getattr(leitura, "disco_desgastado", None):
        return ""
    livre = f"{unidade.livre_gb:.1f}".replace(".", ",")
    return f"Restam {livre} GB na unidade {unidade.ponto}."


DISCO = Recurso(
    nome="disco",
    rotulo="Disco",
    classificar=classificar_disco,
    extrair=lambda dados: dados.disco,
    formatar_valor=_valor_disco,
    causa_fn=lambda leitura: (
        CAUSA_DESGASTE if getattr(leitura, "disco_desgastado", None) else CAUSA_ESPACO
    ),
    linha_extra_fn=_linha_desgaste,
    detalhe_fn=_detalhe_disco,
    causa_padrao=CAUSA_ESPACO,
    descricoes={
        Status.NORMAL: {
            CAUSA_ESPACO: "Espaço em disco suficiente. Não há risco no momento."
        },
        Status.ATENCAO: {
            CAUSA_ESPACO: "Espaço em disco diminuindo. Vale apagar arquivos que "
            "você não usa mais.",
            # Mesma frase do Alerta, de propósito. O RastreadorAlerta segura o disco em
            # Atenção pelos primeiros 5 s, e sem esta entrada o cartão cairia no texto
            # de espaço — mandando apagar arquivo para resolver defeito de hardware.
            CAUSA_DESGASTE: _DESGASTE,
        },
        Status.ALERTA: {
            CAUSA_ESPACO: "Espaço em disco acabando. Apague arquivos grandes ou "
            "mova para outro lugar.",
            CAUSA_DESGASTE: _DESGASTE,
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
    return mais_grave(s for s in statuses if s is not None)
