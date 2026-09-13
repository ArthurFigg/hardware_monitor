"""Acumula o minuto em curso, fecha episódios de alerta e registra a lacuna na abertura.

Quem é gravado vem do campo `grava_historico` de cada recurso, nunca de uma lista de
nomes aqui. Recurso novo entra em `recursos.py` e passa a ser gravado sozinho — o mesmo
motivo pelo qual a tela não conhece recurso por nome.

O banco é a fronteira: tudo aqui é regra, e o que falha do outro lado falha em silêncio
por decisão da spec 08.
"""

import time

from hardware.thresholds import Status

SEGUNDOS_POR_MINUTO = 60


class _Acumulado:
    """Soma do minuto em curso, para uma chave de recurso."""

    def __init__(self):
        self.soma = 0.0
        self.quantidade = 0
        self.soma_livre = 0.0
        self.quantidade_livre = 0

    def somar(self, valor, livre_gb) -> None:
        self.soma += valor
        self.quantidade += 1
        if livre_gb is not None:
            self.soma_livre += livre_gb
            self.quantidade_livre += 1

    @property
    def media(self) -> float:
        return self.soma / self.quantidade

    @property
    def media_livre(self):
        if not self.quantidade_livre:
            return None
        return self.soma_livre / self.quantidade_livre


class Gravador:
    """Transforma o que a coleta entrega em linhas de histórico."""

    def __init__(self, banco, relogio=time.time):
        self._banco = banco
        self._relogio = relogio
        self._minuto = None
        self._acumulado = {}
        self._episodios = {}

    def registrar(
        self, recurso, valor, unidade=None, livre_gb=None, agora=None
    ) -> None:
        """Acumula o valor no minuto em curso; na virada, grava a média do anterior."""
        if not recurso.grava_historico:
            return

        instante = self._instante(agora)
        minuto = int(instante // SEGUNDOS_POR_MINUTO)
        if self._minuto is not None and minuto != self._minuto:
            self._fechar_minuto()
        self._minuto = minuto

        chave = (recurso.nome, unidade)
        if chave not in self._acumulado:
            self._acumulado[chave] = _Acumulado()
        self._acumulado[chave].somar(valor, livre_gb)

    def registrar_status(
        self, recurso, status, valor, programa=None, agora=None
    ) -> None:
        """Abre o episódio no instante em que o alerta é confirmado, e fecha na saída."""
        if not recurso.grava_historico:
            return

        instante = self._instante(agora)
        nome = recurso.nome
        pico_aberto = self._episodios.get(nome)

        if status is Status.ALERTA:
            if pico_aberto is None:
                self._banco.abrir_episodio(
                    recurso=nome, inicio=instante, pico=valor, programa=programa
                )
                self._episodios[nome] = valor
            elif valor > pico_aberto:
                self._banco.atualizar_pico_episodio(recurso=nome, pico=valor)
                self._episodios[nome] = valor
            return

        if pico_aberto is not None:
            self._banco.fechar_episodio(recurso=nome, fim=instante)
            del self._episodios[nome]

    def registrar_lacuna(self, boot_em, agora=None) -> None:
        """O tempo de PC ligado sem o app. Começa no mais recente: boot ou último minuto."""
        instante = self._instante(agora)
        ultimo = self._banco.ultimo_instante()
        inicio = boot_em if ultimo is None else max(ultimo, boot_em)

        # Reabertura imediata não é lacuna: uma linha por clique encheria o banco sem
        # dizer nada.
        if instante - inicio < SEGUNDOS_POR_MINUTO:
            return

        self._banco.gravar_lacuna(inicio=inicio, fim=instante)

    def fechar(self) -> None:
        """Descarta a média parcial: 12 segundos rotulados como "o minuto" mentiriam."""
        self._acumulado.clear()
        self._minuto = None

    def _instante(self, agora):
        return self._relogio() if agora is None else agora

    def _fechar_minuto(self) -> None:
        instante = self._minuto * SEGUNDOS_POR_MINUTO
        for (nome, unidade), acumulado in self._acumulado.items():
            self._banco.gravar_amostra(
                recurso=nome,
                instante=instante,
                valor=acumulado.media,
                unidade=unidade,
                livre_gb=acumulado.media_livre,
            )
        self._acumulado.clear()
