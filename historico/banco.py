"""O arquivo do histórico, em `%LOCALAPPDATA%`, e todo o SQL do projeto.

Nenhuma instrução SQL mora fora daqui. A consulta que a spec 09a vai escrever recebe
linhas prontas: regra de negócio e acesso a dados não se misturam, e quem abriu o banco é
quem sabe fechá-lo.

Falha de escrita esconde a si mesma, como toda leitura de hardware deste app: banco que
não abre marca `disponivel` falso e aceita todas as chamadas sem fazer nada. O app roda
sem histórico; o que ele não pode é parar de rodar por causa dele.
"""

import logging
import os
import sqlite3
import time
from pathlib import Path

NOME_PASTA = "MonitorDeHardware"
NOME_ARQUIVO = "historico.db"
RETENCAO_DIAS = 90

_SEGUNDOS_POR_DIA = 24 * 60 * 60
_LOG = logging.getLogger(__name__)

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS amostras (
    recurso  TEXT NOT NULL,
    instante REAL NOT NULL,
    valor    REAL NOT NULL,
    unidade  TEXT,
    livre_gb REAL
);
CREATE TABLE IF NOT EXISTS episodios (
    recurso  TEXT NOT NULL,
    inicio   REAL NOT NULL,
    fim      REAL,
    pico     REAL NOT NULL,
    programa TEXT
);
CREATE TABLE IF NOT EXISTS lacunas (
    inicio REAL NOT NULL,
    fim    REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_amostras_instante ON amostras (instante);
CREATE INDEX IF NOT EXISTS ix_episodios_inicio  ON episodios (inicio);
CREATE INDEX IF NOT EXISTS ix_lacunas_inicio    ON lacunas (inicio);
"""


def pasta() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("TMP") or "."
    return Path(base) / NOME_PASTA


def caminho_padrao() -> Path:
    return pasta() / NOME_ARQUIVO


class Banco:
    """O arquivo do histórico. Indisponível é estado normal, nunca erro."""

    def __init__(self, caminho=None, agora=None):
        self._caminho = Path(caminho) if caminho is not None else caminho_padrao()
        self._conexao = self._abrir()
        if self._conexao is not None:
            self._aplicar_retencao(agora)

    @property
    def disponivel(self) -> bool:
        return self._conexao is not None

    def _abrir(self):
        try:
            self._caminho.parent.mkdir(parents=True, exist_ok=True)
            conexao = sqlite3.connect(self._caminho, check_same_thread=False)
            conexao.row_factory = sqlite3.Row
            conexao.executescript(_ESQUEMA)
            conexao.commit()
            return conexao
        except (OSError, sqlite3.Error) as erro:
            _LOG.warning("histórico indisponível em %s: %s", self._caminho, erro)
            return None

    def _executar(self, sql: str, parametros=()) -> None:
        """Escrita que falha derruba o histórico, nunca o app."""
        if self._conexao is None:
            return
        try:
            self._conexao.execute(sql, parametros)
            self._conexao.commit()
        except sqlite3.Error as erro:
            _LOG.warning("gravação no histórico falhou: %s", erro)
            self._conexao = None

    def _consultar(self, sql: str, parametros=()) -> list:
        if self._conexao is None:
            return []
        try:
            return self._conexao.execute(sql, parametros).fetchall()
        except sqlite3.Error as erro:
            _LOG.warning("leitura do histórico falhou: %s", erro)
            self._conexao = None
            return []

    def _aplicar_retencao(self, agora=None) -> None:
        corte = (agora if agora is not None else time.time()) - (
            RETENCAO_DIAS * _SEGUNDOS_POR_DIA
        )
        self._executar("DELETE FROM amostras WHERE instante < ?", (corte,))
        self._executar("DELETE FROM episodios WHERE inicio < ?", (corte,))
        self._executar("DELETE FROM lacunas WHERE inicio < ?", (corte,))

    def gravar_amostra(
        self, recurso, instante, valor, unidade=None, livre_gb=None
    ) -> None:
        self._executar(
            "INSERT INTO amostras (recurso, instante, valor, unidade, livre_gb)"
            " VALUES (?, ?, ?, ?, ?)",
            (recurso, instante, valor, unidade, livre_gb),
        )

    def abrir_episodio(self, recurso, inicio, pico, programa=None) -> None:
        self._executar(
            "INSERT INTO episodios (recurso, inicio, fim, pico, programa)"
            " VALUES (?, ?, NULL, ?, ?)",
            (recurso, inicio, pico, programa),
        )

    def atualizar_pico_episodio(self, recurso, pico) -> None:
        self._executar(
            "UPDATE episodios SET pico = ?"
            " WHERE rowid = (SELECT MAX(rowid) FROM episodios"
            "                WHERE recurso = ? AND fim IS NULL)",
            (pico, recurso),
        )

    def fechar_episodio(self, recurso, fim) -> None:
        self._executar(
            "UPDATE episodios SET fim = ?"
            " WHERE rowid = (SELECT MAX(rowid) FROM episodios"
            "                WHERE recurso = ? AND fim IS NULL)",
            (fim, recurso),
        )

    def gravar_lacuna(self, inicio, fim) -> None:
        self._executar("INSERT INTO lacunas (inicio, fim) VALUES (?, ?)", (inicio, fim))

    def ultimo_instante(self):
        """Instante da amostra mais recente, ou `None` quando não há nenhuma."""
        linhas = self._consultar("SELECT MAX(instante) AS ultimo FROM amostras")
        if not linhas:
            return None
        return linhas[0]["ultimo"]

    def amostras(self, desde=None, ate=None) -> list:
        return self._janela("amostras", "instante", desde, ate)

    def episodios(self, desde=None, ate=None) -> list:
        return self._janela("episodios", "inicio", desde, ate)

    def lacunas(self, desde=None, ate=None) -> list:
        return self._janela("lacunas", "inicio", desde, ate)

    def _janela(self, tabela: str, coluna: str, desde, ate) -> list:
        """Nomes de tabela e coluna são internos, nunca chegam de fora."""
        condicoes = []
        parametros = []
        if desde is not None:
            condicoes.append(f"{coluna} >= ?")
            parametros.append(desde)
        if ate is not None:
            condicoes.append(f"{coluna} <= ?")
            parametros.append(ate)

        onde = f" WHERE {' AND '.join(condicoes)}" if condicoes else ""
        linhas = self._consultar(
            f"SELECT * FROM {tabela}{onde} ORDER BY {coluna}", tuple(parametros)
        )
        return [dict(linha) for linha in linhas]

    def fechar(self) -> None:
        if self._conexao is None:
            return
        try:
            self._conexao.close()
        except sqlite3.Error as erro:
            _LOG.warning("fechamento do histórico falhou: %s", erro)
        self._conexao = None
