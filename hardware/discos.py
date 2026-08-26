"""O que o app enxerga do disco: as unidades fixas e a saúde dos discos físicos.

Duas leituras com ritmos muito diferentes convivem aqui. O espaço livre é lido a cada
ciclo, como CPU e RAM. A saúde é consultada uma vez a cada 6 horas — desgaste evolui em
semanas, e a consulta abre um processo do PowerShell, que é caro demais para o ciclo de
um segundo.

Ambas seguem a regra do projeto: leitura que falha esconde a si mesma. Unidade que
sumiu sai da lista; consulta de saúde que falhou devolve `None`, que é diferente de
"todos saudáveis".
"""

import json
import subprocess
import time
from dataclasses import dataclass, field

import psutil

from hardware.thresholds import classificar_unidade, gravidade

GB = 1024**3

# Abaixo disso a unidade não é um lugar onde a pessoa guarda arquivos. Exclui a partição
# de recuperação do Windows (~500 MB, sempre quase cheia), que sem o filtro deixaria o
# app em Alerta permanente apontando para algo sobre o que não há nada a fazer.
TAMANHO_MINIMO = 10 * GB

_OPCOES_EXCLUIDAS = ("cdrom", "removable", "remote", "net")

INTERVALO_SAUDE = 6 * 60 * 60

_COMANDO_SAUDE = (
    "Get-PhysicalDisk | Select-Object FriendlyName, HealthStatus | ConvertTo-Json"
)
_TIMEOUT_SAUDE = 15

# Sem isso o PowerShell pisca uma janela de console preta a cada consulta. Só existe no
# Windows; o `getattr` mantém o módulo importável no CI, que roda em Linux.
_SEM_JANELA = getattr(subprocess, "CREATE_NO_WINDOW", 0)


@dataclass(frozen=True)
class Unidade:
    ponto: str
    percentual: float
    livre_gb: float


@dataclass(frozen=True)
class VistaDisco:
    """Uma unidade só, do jeito que o cartão a exibe agora.

    Tem `unidades` e `disco_desgastado` como a leitura completa, de propósito: assim
    `classificar_disco()` e os textos funcionam nela sem saber que é uma vista.
    """

    unidades: tuple[Unidade, ...]
    disco_desgastado: str | None
    indice: int
    total: int
    exibe_pior: bool
    pior_ponto: str | None

    @property
    def pior_unidade(self) -> Unidade | None:
        return self.unidades[0] if self.unidades else None


@dataclass(frozen=True)
class LeituraDisco:
    """Tudo que o cartão do Disco precisa saber, numa leitura só.

    `disco_desgastado` é o nome do disco físico, e não da unidade: a saúde é do
    dispositivo, e um disco com várias partições faria o mapeamento errar.
    """

    unidades: tuple[Unidade, ...] = ()
    disco_desgastado: str | None = None

    @property
    def pior_unidade(self) -> Unidade | None:
        """A unidade que decide o status — obrigatoriamente a mesma que o cartão exibe.

        Ordena pelo status antes do percentual. Ordenar só por percentual quebra quando
        as duas regras apontam para discos diferentes: um SSD de sistema com 8 GB livres
        está em Alerta pela regra de espaço, mas perde no percentual para um HD de dados
        em 94% que está só em Atenção — e o cartão acenderia vermelho exibindo o disco
        errado.
        """
        if not self.unidades:
            return None
        return max(self.unidades, key=_ranking)

    def vista(self, indice: int | None = None) -> VistaDisco:
        """A unidade que o cartão mostra agora. `None` significa "a pior".

        Índice fora da faixa volta para a pior em vez de quebrar: uma unidade pode
        desaparecer com o app aberto, e a seleção não pode ficar apontando para o vazio.
        """
        if not self.unidades:
            return VistaDisco((), self.disco_desgastado, 0, 0, True, None)

        pior = self.pior_unidade
        ordem = list(self.unidades)
        if indice is None or not (0 <= indice < len(ordem)):
            indice = ordem.index(pior)

        return VistaDisco(
            unidades=(ordem[indice],),
            disco_desgastado=self.disco_desgastado,
            indice=indice,
            total=len(ordem),
            exibe_pior=ordem[indice] == pior,
            pior_ponto=pior.ponto,
        )


def _ranking(unidade: Unidade) -> tuple[int, float, float]:
    status = classificar_unidade(unidade.percentual, unidade.livre_gb)
    return (gravidade(status), unidade.percentual, -unidade.livre_gb)


def _e_fixa(particao) -> bool:
    opcoes = (particao.opts or "").lower()
    if any(excluida in opcoes for excluida in _OPCOES_EXCLUIDAS):
        return False
    return bool(particao.fstype)


def listar_unidades() -> tuple[Unidade, ...]:
    """Unidades fixas com mais de 10 GB, na ordem em que o sistema as devolve."""
    unidades = []
    for particao in psutil.disk_partitions(all=False):
        if not _e_fixa(particao):
            continue
        try:
            uso = psutil.disk_usage(particao.mountpoint)
        except OSError:
            continue
        if uso.total < TAMANHO_MINIMO:
            continue
        unidades.append(
            Unidade(
                ponto=particao.mountpoint.rstrip("\\/") or particao.mountpoint,
                percentual=uso.percent,
                livre_gb=uso.free / GB,
            )
        )
    return tuple(unidades)


def _consultar_saude() -> tuple[str, ...] | None:
    """Nomes dos discos físicos que não estão saudáveis, ou None se não deu para saber.

    Tupla vazia significa "consultei e está tudo bem"; `None` significa "não consegui
    consultar" — Windows antigo, comando ausente, permissão negada. Os dois casos
    escondem a linha de desgaste, mas só o primeiro é informação.
    """
    saida = _rodar_consulta()
    if saida is None:
        return None
    return _extrair_doentes(saida)


def _rodar_consulta() -> str | None:
    try:
        resultado = subprocess.run(
            ["powershell", "-NoProfile", "-Command", _COMANDO_SAUDE],
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SAUDE,
            creationflags=_SEM_JANELA,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if resultado.returncode != 0 or not resultado.stdout.strip():
        return None
    return resultado.stdout


def _extrair_doentes(saida: str) -> tuple[str, ...] | None:
    try:
        dados = json.loads(saida)
    except json.JSONDecodeError:
        return None

    # Com um disco só, o PowerShell devolve um objeto em vez de uma lista.
    if isinstance(dados, dict):
        dados = [dados]
    if not isinstance(dados, list):
        return None

    return tuple(
        str(disco.get("FriendlyName") or "disco")
        for disco in dados
        if isinstance(disco, dict)
        and str(disco.get("HealthStatus") or "").lower() != "healthy"
    )


@dataclass
class CacheSaude:
    """Guarda o resultado da consulta de saúde pelo intervalo definido."""

    intervalo: float = INTERVALO_SAUDE
    _consultado_em: float | None = field(default=None, init=False)
    _valor: tuple[str, ...] | None = field(default=None, init=False)

    def obter(self) -> tuple[str, ...] | None:
        agora = time.monotonic()
        if (
            self._consultado_em is None
            or (agora - self._consultado_em) >= self.intervalo
        ):
            self._valor = _consultar_saude()
            self._consultado_em = agora
        return self._valor


_cache_saude = CacheSaude()


def ler() -> LeituraDisco:
    """Leitura completa do disco para um ciclo de coleta."""
    doentes = _cache_saude.obter()
    return LeituraDisco(
        unidades=listar_unidades(),
        disco_desgastado=doentes[0] if doentes else None,
    )
