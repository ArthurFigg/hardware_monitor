from hardware.thresholds import Status, descricao
from ui.components.cards import CartaoRecurso


def test_cartao_status_inicial_normal(raiz):
    cartao = CartaoRecurso(raiz, titulo="CPU")
    assert cartao.status_atual == Status.NORMAL


def test_cartao_descricao_inicial_normal(raiz):
    cartao = CartaoRecurso(raiz, titulo="CPU")
    assert cartao._label_descricao.cget("text") == descricao(Status.NORMAL)


def test_cartao_atualizar_muda_status(raiz):
    cartao = CartaoRecurso(raiz, titulo="RAM")
    cartao.atualizar(Status.ALERTA)
    assert cartao.status_atual == Status.ALERTA


def test_cartao_atualizar_muda_descricao(raiz):
    cartao = CartaoRecurso(raiz, titulo="RAM")
    cartao.atualizar(Status.ATENCAO)
    assert cartao._label_descricao.cget("text") == descricao(Status.ATENCAO)


def test_cartao_atualizar_propaga_semaforo(raiz):
    cartao = CartaoRecurso(raiz, titulo="Disco")
    cartao.atualizar(Status.ATENCAO)
    assert cartao._semaforo.status_atual == Status.ATENCAO
