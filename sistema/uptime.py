"""Há quanto tempo a máquina está ligada, em texto.

Módulo próprio e não dentro de `app.py` porque tem regra e teste; e não em
`inicializacao.py` nem em `estado.py` porque nenhum dos dois trata disso — arquivo que
precisa de "e" no nome para fazer sentido está fazendo coisas demais.
"""

_SEGUNDOS_POR_HORA = 3600
_SEGUNDOS_POR_MINUTO = 60


def formatar(segundos: float | None) -> str:
    """ "Ligado há 5h 23min", ou vazio quando não deu para saber.

    Vazio esconde a linha inteira. Nunca "Ligado há 0h 0min" nem mensagem de erro: o
    rodapé é informação de canto, e informação de canto que dá defeito é pior que
    ausência.
    """
    if segundos is None or segundos < 0:
        return ""
    horas = int(segundos // _SEGUNDOS_POR_HORA)
    minutos = int((segundos % _SEGUNDOS_POR_HORA) // _SEGUNDOS_POR_MINUTO)
    return f"Ligado há {horas}h {minutos}min"
