import customtkinter as ctk

from hardware.thresholds import Status, descricao
from ui.components.semaphore import Semaforo


class CartaoRecurso(ctk.CTkFrame):
    def __init__(self, master, titulo: str, **kwargs):
        super().__init__(master, corner_radius=12, **kwargs)
        self._status_atual = Status.NORMAL

        self._semaforo = Semaforo(self, tamanho=32)
        self._label_titulo = ctk.CTkLabel(
            self,
            text=titulo,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        self._label_descricao = ctk.CTkLabel(
            self,
            text=descricao(Status.NORMAL),
            wraplength=240,
            justify="left",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self._organizar()

    @property
    def status_atual(self) -> Status:
        return self._status_atual

    def atualizar(self, status: Status) -> None:
        self._status_atual = status
        self._semaforo.atualizar(status)
        self._label_descricao.configure(text=descricao(status))

    def _organizar(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self._semaforo.grid(row=0, column=0, rowspan=2, padx=(16, 12), pady=16)
        self._label_titulo.grid(row=0, column=1, sticky="w", padx=(0, 16), pady=(16, 2))
        self._label_descricao.grid(row=1, column=1, sticky="w", padx=(0, 16), pady=(2, 16))
