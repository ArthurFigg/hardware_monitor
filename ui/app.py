import threading

import customtkinter as ctk

from hardware.collector import coletar
from hardware.thresholds import (
    RastreadorAlerta,
    classificar,
    classificar_temperatura,
    descricao_temperatura,
    estimar_temperatura,
)
from notifications.manager import GerenciadorNotificacoes
from ui.components.cards import CartaoRecurso


class AplicativoMonitor(ctk.CTkFrame):
    _INTERVALO_VERIFICACAO_MS = 100

    def __init__(self, master: ctk.CTk, **kwargs):
        super().__init__(master, **kwargs)

        master.title("Monitor de Hardware")
        master.resizable(False, False)
        master.protocol("WM_DELETE_WINDOW", self._ao_fechar)

        self._rodando = True
        self._dados_pendentes = None
        self._lock = threading.Lock()
        self._rastreadores = {
            "cpu": RastreadorAlerta(),
            "ram": RastreadorAlerta(),
            "disco": RastreadorAlerta(),
            "temperatura": RastreadorAlerta(),
        }
        self._notificadores = {
            "cpu": GerenciadorNotificacoes(),
            "ram": GerenciadorNotificacoes(),
            "disco": GerenciadorNotificacoes(),
            "temperatura": GerenciadorNotificacoes(),
        }
        self._cards = {
            "cpu": CartaoRecurso(self, titulo="CPU"),
            "ram": CartaoRecurso(self, titulo="RAM"),
            "disco": CartaoRecurso(self, titulo="Disco"),
            "temperatura": CartaoRecurso(
                self,
                titulo="Temperatura",
                descricao_fn=descricao_temperatura,
                formatar_valor=lambda v: f"~{v:.0f}°C",
            ),
        }
        self._botao_tema = ctk.CTkButton(
            self,
            text="Modo Claro",
            width=120,
            height=28,
            command=self._alternar_tema,
        )

        self._organizar()
        self._iniciar_coleta()
        self._agendar_atualizacao()

    def _organizar(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        for i, card in enumerate(self._cards.values()):
            pady = (20, 0) if i == 0 else (8, 0)
            card.grid(row=i, column=0, padx=20, pady=pady, sticky="ew")
        self._botao_tema.grid(row=4, column=0, pady=16)

    def _iniciar_coleta(self) -> None:
        thread = threading.Thread(target=self._loop_coleta, daemon=True)
        thread.start()

    def _loop_coleta(self) -> None:
        while self._rodando:
            dados = coletar()
            with self._lock:
                self._dados_pendentes = dados

    def _agendar_atualizacao(self) -> None:
        with self._lock:
            dados = self._dados_pendentes
            self._dados_pendentes = None

        if dados is not None:
            self._atualizar_cards(dados)

        if self._rodando:
            self.after(self._INTERVALO_VERIFICACAO_MS, self._agendar_atualizacao)

    def _atualizar_cards(self, dados) -> None:
        mapeamento = {"cpu": dados.cpu, "ram": dados.ram, "disco": dados.disco}
        for recurso, percentual in mapeamento.items():
            status_bruto = classificar(percentual)
            status = self._rastreadores[recurso].atualizar(status_bruto)
            self._cards[recurso].atualizar(status, percentual)
            self._notificadores[recurso].processar(status)

        temp_estimada = estimar_temperatura(dados.cpu)
        status_bruto = classificar_temperatura(temp_estimada)
        status = self._rastreadores["temperatura"].atualizar(status_bruto)
        self._cards["temperatura"].atualizar(status, temp_estimada)
        self._notificadores["temperatura"].processar(status)

    def _alternar_tema(self) -> None:
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("light")
            self._botao_tema.configure(text="Modo Escuro")
        else:
            ctk.set_appearance_mode("dark")
            self._botao_tema.configure(text="Modo Claro")

    def _ao_fechar(self) -> None:
        self._rodando = False
        self.master.destroy()
