from collections.abc import Callable

import customtkinter as ctk

from hardware.thresholds import Status
from ui.components.semaphore import Semaforo


class CartaoRecurso(ctk.CTkFrame):
    def __init__(
        self,
        master,
        titulo: str,
        descricao_fn: Callable[..., str],
        formatar_valor: Callable[[float], str] | None = None,
        linha_extra_fn: Callable[[object], str] | None = None,
        ao_clicar: Callable[[], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, corner_radius=12, **kwargs)
        self._status_atual = Status.NORMAL
        self._descricao_fn = descricao_fn
        self._formatar_valor = formatar_valor or (lambda v: f"{v:.0f}%")
        self._linha_extra_fn = linha_extra_fn or (lambda _: "")
        self._ao_clicar = ao_clicar

        self._criar_rotulos(titulo)
        self._organizar()
        if self._ao_clicar is not None:
            self._ligar_clique()

    def _criar_rotulos(self, titulo: str) -> None:
        self._semaforo = Semaforo(self, tamanho=32)
        self._label_titulo = ctk.CTkLabel(
            self,
            text=titulo,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        self._label_percentual = ctk.CTkLabel(
            self,
            text=self._formatar_valor(0.0),
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="e",
        )
        self._label_descricao = ctk.CTkLabel(
            self,
            text=self._descricao_fn(Status.NORMAL, None),
            wraplength=240,
            justify="left",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self._label_extra = ctk.CTkLabel(
            self,
            text="",
            wraplength=240,
            justify="left",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )

    @property
    def status_atual(self) -> Status:
        return self._status_atual

    def atualizar(self, status: Status, valor=0.0) -> None:
        self._status_atual = status
        self._semaforo.atualizar(status)
        self._label_descricao.configure(text=self._descricao_fn(status, valor))
        self._label_percentual.configure(text=self._formatar_valor(valor))
        self._atualizar_linha_extra(valor)

    @property
    def linha_extra(self) -> str:
        """O que a linha extra está dizendo agora. Vazio significa escondida."""
        return self._label_extra.cget("text")

    def _atualizar_linha_extra(self, valor) -> None:
        """Linha opcional abaixo da descrição, escondida enquanto não houver texto.

        Escondida e não vazia: um rótulo vazio ocupa altura e desalinharia o cartão do
        Disco em relação aos outros no dia a dia, que é quando não há nada a dizer.
        """
        texto = self._linha_extra_fn(valor)
        self._label_extra.configure(text=texto)
        if texto:
            self._label_descricao.grid_configure(pady=(2, 2))
            self._label_extra.grid()
        else:
            self._label_descricao.grid_configure(pady=(2, 16))
            self._label_extra.grid_remove()

    def _ligar_clique(self) -> None:
        """Liga o clique no cartão e em tudo que está dentro dele.

        O Tk não propaga clique de filho para o frame pai: sem ligar em cada rótulo,
        clicar no número não faria nada e clicar na borda faria — que é pior que não
        ter clique nenhum.
        """
        for widget in self._widgets():
            widget.bind("<Button-1>", lambda _evento: self._ao_clicar())

    def definir_clicavel(self, clicavel: bool) -> None:
        """Mostra ou esconde a mãozinha do cursor.

        Separado de ligar o clique porque só se sabe se há para onde ir depois de ler os
        dados: um cartão de disco numa máquina com uma unidade só continua ligado, mas
        não pode prometer com o cursor uma troca que não vai acontecer.
        """
        cursor = "hand2" if clicavel else ""
        for widget in self._widgets():
            widget.configure(cursor=cursor)

    @property
    def parece_clicavel(self) -> bool:
        """Existe para o teste poder verificar o que o cursor está prometendo."""
        return self.cget("cursor") == "hand2"

    def _widgets(self):
        return (self, *self._descendentes())

    def _descendentes(self):
        pendentes = list(self.winfo_children())
        while pendentes:
            widget = pendentes.pop()
            pendentes.extend(widget.winfo_children())
            yield widget

    def _organizar(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self._semaforo.grid(row=0, column=0, rowspan=2, padx=(16, 12), pady=16)
        self._label_titulo.grid(row=0, column=1, sticky="w", padx=(0, 8), pady=(16, 2))
        self._label_percentual.grid(
            row=0, column=2, sticky="e", padx=(0, 16), pady=(16, 2)
        )
        self._label_descricao.grid(
            row=1, column=1, columnspan=2, sticky="w", padx=(0, 16), pady=(2, 16)
        )
        self._label_extra.grid(
            row=2, column=1, columnspan=2, sticky="w", padx=(0, 16), pady=(0, 16)
        )
        self._label_extra.grid_remove()
