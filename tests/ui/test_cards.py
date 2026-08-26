from hardware.thresholds import Status
from recursos import CPU, TEMPERATURA
from ui.components.cards import CartaoRecurso


def test_cartao_status_inicial_normal(raiz):
    cartao = CartaoRecurso(raiz, titulo="CPU", descricao_fn=CPU.descricao_de)
    assert cartao.status_atual == Status.NORMAL


def test_cartao_descricao_inicial_normal(raiz):
    cartao = CartaoRecurso(raiz, titulo="CPU", descricao_fn=CPU.descricao_de)
    assert cartao._label_descricao.cget("text") == CPU.descricao(Status.NORMAL)


def test_cartao_valor_inicial_zero(raiz):
    cartao = CartaoRecurso(raiz, titulo="CPU", descricao_fn=CPU.descricao_de)
    assert cartao._label_percentual.cget("text") == "0%"


def test_cartao_atualizar_muda_status(raiz):
    cartao = CartaoRecurso(raiz, titulo="RAM", descricao_fn=CPU.descricao_de)
    cartao.atualizar(Status.ALERTA, 90.0)
    assert cartao.status_atual == Status.ALERTA


def test_cartao_atualizar_muda_descricao(raiz):
    cartao = CartaoRecurso(raiz, titulo="RAM", descricao_fn=CPU.descricao_de)
    cartao.atualizar(Status.ATENCAO, 70.0)
    assert cartao._label_descricao.cget("text") == CPU.descricao(Status.ATENCAO)


def test_cartao_atualizar_mostra_percentual(raiz):
    cartao = CartaoRecurso(raiz, titulo="RAM", descricao_fn=CPU.descricao_de)
    cartao.atualizar(Status.ATENCAO, 73.6)
    assert cartao._label_percentual.cget("text") == "74%"


def test_cartao_atualizar_propaga_semaforo(raiz):
    cartao = CartaoRecurso(raiz, titulo="Disco", descricao_fn=CPU.descricao_de)
    cartao.atualizar(Status.ATENCAO, 65.0)
    assert cartao._semaforo.status_atual == Status.ATENCAO


def test_cartao_temperatura_formato_celsius(raiz):
    cartao = CartaoRecurso(
        raiz,
        titulo="Temperatura",
        descricao_fn=TEMPERATURA.descricao_de,
        formatar_valor=lambda v: f"~{v:.0f}°C",
    )
    cartao.atualizar(Status.NORMAL, 65.7)
    assert cartao._label_percentual.cget("text") == "~66°C"


def test_cartao_temperatura_descricao_fn_customizada(raiz):
    cartao = CartaoRecurso(
        raiz,
        titulo="Temperatura",
        descricao_fn=TEMPERATURA.descricao_de,
        formatar_valor=lambda v: f"~{v:.0f}°C",
    )
    cartao.atualizar(Status.ATENCAO, 70.0)
    assert cartao._label_descricao.cget("text") == TEMPERATURA.descricao(Status.ATENCAO)


def test_cartao_sem_linha_extra_fica_identico_ao_de_hoje(raiz):
    """CPU, RAM e Temperatura não passam linha extra — o cartão não pode mudar."""
    cartao = CartaoRecurso(raiz, titulo="CPU", descricao_fn=CPU.descricao_de)
    cartao.atualizar(Status.ALERTA, 90.0)
    assert cartao.linha_extra == ""


def test_cartao_esconde_a_linha_extra_quando_vazia(raiz):
    cartao = CartaoRecurso(
        raiz,
        titulo="Disco",
        descricao_fn=CPU.descricao_de,
        linha_extra_fn=lambda _: "",
    )
    cartao.atualizar(Status.NORMAL, 30.0)
    raiz.update_idletasks()
    assert not cartao._label_extra.winfo_manager()


def test_cartao_exibe_a_linha_extra_quando_preenchida(raiz):
    cartao = CartaoRecurso(
        raiz,
        titulo="Disco",
        descricao_fn=CPU.descricao_de,
        linha_extra_fn=lambda _: "O disco X está dando sinais de desgaste.",
    )
    cartao.atualizar(Status.ALERTA, 30.0)
    raiz.update_idletasks()
    assert cartao.linha_extra == "O disco X está dando sinais de desgaste."


def test_cartao_volta_a_esconder_a_linha_extra(raiz):
    """Disco trocado: a linha precisa sumir, não ficar como texto velho na tela."""
    textos = iter(["desgaste detectado", ""])
    cartao = CartaoRecurso(
        raiz,
        titulo="Disco",
        descricao_fn=CPU.descricao_de,
        linha_extra_fn=lambda _: next(textos),
    )
    cartao.atualizar(Status.ALERTA, 30.0)
    cartao.atualizar(Status.NORMAL, 30.0)
    raiz.update_idletasks()
    assert not cartao._label_extra.winfo_manager()


def test_cartao_sem_ao_clicar_nao_tem_cursor_de_mao(raiz):
    cartao = CartaoRecurso(raiz, titulo="CPU", descricao_fn=CPU.descricao_de)
    assert not cartao.parece_clicavel


def _recebe_clique(widget) -> bool:
    """Se um clique nesse widget chega ao cartão.

    O CustomTkinter esconde de `winfo_children()` o canvas onde de fato desenha, e é
    nele que o `bind` acaba caindo — olhar só os filhos visíveis dá falso negativo.
    """
    if "<Button-1>" in (widget.bind() or ()):
        return True
    canvas = getattr(widget, "_canvas", None)
    return canvas is not None and "<Button-1>" in (canvas.bind() or ())


def test_cartao_clicavel_liga_o_clique_em_cada_parte(raiz):
    """O Tk não propaga clique de filho para o frame pai.

    Verificado pelo binding e não por `event_generate`: o Tk não entrega evento
    sintético em janela que nunca foi exibida, e nos testes a raiz nunca é. Sem ligar em
    cada parte, clicar no número não faria nada e clicar na borda faria — pior que não
    ter clique.
    """
    cartao = CartaoRecurso(
        raiz, titulo="Disco", descricao_fn=CPU.descricao_de, ao_clicar=lambda: None
    )
    assert all(_recebe_clique(w) for w in (cartao, *cartao.winfo_children()))


def test_cartao_sem_ao_clicar_nao_liga_clique_nenhum(raiz):
    cartao = CartaoRecurso(raiz, titulo="CPU", descricao_fn=CPU.descricao_de)
    assert not any(_recebe_clique(w) for w in (cartao, *cartao.winfo_children()))


def test_definir_clicavel_liga_a_maozinha(raiz):
    cartao = CartaoRecurso(
        raiz, titulo="Disco", descricao_fn=CPU.descricao_de, ao_clicar=lambda: None
    )
    cartao.definir_clicavel(True)
    assert cartao.parece_clicavel


def test_definir_clicavel_desliga_a_maozinha(raiz):
    cartao = CartaoRecurso(
        raiz, titulo="Disco", descricao_fn=CPU.descricao_de, ao_clicar=lambda: None
    )
    cartao.definir_clicavel(True)
    cartao.definir_clicavel(False)
    assert not cartao.parece_clicavel
