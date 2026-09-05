"""Uma instância só do app, e o segundo clique abre a janela da primeira.

Com o app entrando junto com o Windows, ele já está rodando quando a pessoa clica no
executável. Sem isto sobem dois processos, dois ícones ao lado do relógio e notificação
em dobro — situação que nunca aparece em desenvolvimento e é a normal de quem baixou.

Simplesmente sair calado seria pior que o problema: a pessoa clicou, nada aconteceu, e
ela conclui que o programa está quebrado. Por isso a segunda instância avisa a primeira,
que mostra a janela, e só então sai.
"""

import ctypes
import threading

NOME_MUTEX = r"Local\MonitorDeHardware"
NOME_EVENTO = r"Local\MonitorDeHardware_Abrir"

_JA_EXISTE = 183  # ERROR_ALREADY_EXISTS
_ESPERA_SEM_FIM = 0xFFFFFFFF
_SINALIZADO = 0  # WAIT_OBJECT_0
_ESPERA_FALHOU = 0xFFFFFFFF  # WAIT_FAILED

try:
    _kernel32 = ctypes.windll.kernel32
except AttributeError:  # Linux, onde o CI roda
    _kernel32 = None

# O identificador precisa viver enquanto o processo viver: se o coletor de lixo o
# recolher, o Windows solta o mutex e a próxima instância se acha a primeira.
_mutex = None


def reservar() -> bool:
    """True se esta é a primeira instância. False se já havia outra rodando."""
    global _mutex
    if _kernel32 is None:
        return True
    _mutex = _kernel32.CreateMutexW(None, False, NOME_MUTEX)
    return _kernel32.GetLastError() != _JA_EXISTE


def pedir_para_abrir() -> bool:
    """Pede à instância que já roda para mostrar a janela dela. Devolve se conseguiu."""
    if _kernel32 is None:
        return False
    evento = _kernel32.CreateEventW(None, False, False, NOME_EVENTO)
    if not evento:
        return False
    try:
        return bool(_kernel32.SetEvent(evento))
    finally:
        _kernel32.CloseHandle(evento)


def vigiar_pedidos(ao_pedir) -> threading.Thread | None:
    """Thread que chama `ao_pedir` a cada pedido de outra instância.

    `ao_pedir` roda numa thread de fora do Tkinter, então quem passa a função é
    responsável por serializar com `after(0, ...)` — a mesma regra do ícone na bandeja.
    """
    if _kernel32 is None:
        return None
    # Evento de rearme automático: volta sozinho ao estado não-sinalizado depois de
    # liberar a espera, então cada pedido novo acorda a thread uma vez.
    evento = _kernel32.CreateEventW(None, False, False, NOME_EVENTO)
    if not evento:
        return None

    def esperar() -> None:
        # Espera que não é sinal é identificador inválido: insistir num que falha
        # queimaria um núcleo em laço apertado pelo resto da execução.
        while _kernel32.WaitForSingleObject(evento, _ESPERA_SEM_FIM) == _SINALIZADO:
            ao_pedir()

    thread = threading.Thread(target=esperar, daemon=True)
    thread.start()
    return thread
