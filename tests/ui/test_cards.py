from hardware.thresholds import Status
from recursos import CPU, TEMPERATURA
from ui.components.cards import CartaoRecurso


def test_cartao_status_inicial_normal(raiz):
    cartao = CartaoRecurso(raiz, titulo="CPU", descricao_fn=CPU.descricao)
    assert cartao.status_atual == Status.NORMAL


def test_cartao_descricao_inicial_normal(raiz):
    cartao = CartaoRecurso(raiz, titulo="CPU", descricao_fn=CPU.descricao)
    assert cartao._label_descricao.cget("text") == CPU.descricao(Status.NORMAL)


def test_cartao_valor_inicial_zero(raiz):
    cartao = CartaoRecurso(raiz, titulo="CPU", descricao_fn=CPU.descricao)
    assert cartao._label_percentual.cget("text") == "0%"


def test_cartao_atualizar_muda_status(raiz):
    cartao = CartaoRecurso(raiz, titulo="RAM", descricao_fn=CPU.descricao)
    cartao.atualizar(Status.ALERTA, 90.0)
    assert cartao.status_atual == Status.ALERTA


def test_cartao_atualizar_muda_descricao(raiz):
    cartao = CartaoRecurso(raiz, titulo="RAM", descricao_fn=CPU.descricao)
    cartao.atualizar(Status.ATENCAO, 70.0)
    assert cartao._label_descricao.cget("text") == CPU.descricao(Status.ATENCAO)


def test_cartao_atualizar_mostra_percentual(raiz):
    cartao = CartaoRecurso(raiz, titulo="RAM", descricao_fn=CPU.descricao)
    cartao.atualizar(Status.ATENCAO, 73.6)
    assert cartao._label_percentual.cget("text") == "74%"


def test_cartao_atualizar_propaga_semaforo(raiz):
    cartao = CartaoRecurso(raiz, titulo="Disco", descricao_fn=CPU.descricao)
    cartao.atualizar(Status.ATENCAO, 65.0)
    assert cartao._semaforo.status_atual == Status.ATENCAO


def test_cartao_temperatura_formato_celsius(raiz):
    cartao = CartaoRecurso(
        raiz,
        titulo="Temperatura",
        descricao_fn=TEMPERATURA.descricao,
        formatar_valor=lambda v: f"~{v:.0f}°C",
    )
    cartao.atualizar(Status.NORMAL, 65.7)
    assert cartao._label_percentual.cget("text") == "~66°C"


def test_cartao_temperatura_descricao_fn_customizada(raiz):
    cartao = CartaoRecurso(
        raiz,
        titulo="Temperatura",
        descricao_fn=TEMPERATURA.descricao,
        formatar_valor=lambda v: f"~{v:.0f}°C",
    )
    cartao.atualizar(Status.ATENCAO, 70.0)
    assert cartao._label_descricao.cget("text") == TEMPERATURA.descricao(Status.ATENCAO)
