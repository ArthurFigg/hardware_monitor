import customtkinter as ctk

from hardware.thresholds import Status

CORES = {
    Status.NORMAL: "#4CAF50",
    Status.ATENCAO: "#FFC107",
    Status.ALERTA: "#F44336",
}


class Semaforo(ctk.CTkFrame):
    def __init__(self, master, tamanho: int = 32, **kwargs):
        super().__init__(
            master,
            width=tamanho,
            height=tamanho,
            corner_radius=tamanho // 2,
            fg_color=CORES[Status.NORMAL],
            **kwargs,
        )
        self.grid_propagate(False)
        self.pack_propagate(False)
        self._status_atual = Status.NORMAL

    @property
    def status_atual(self) -> Status:
        return self._status_atual

    def atualizar(self, status: Status) -> None:
        self._status_atual = status
        self.configure(fg_color=CORES[status])
