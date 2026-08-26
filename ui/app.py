import threading

import customtkinter as ctk

from hardware.collector import coletar
from hardware.processos import programa_dominante
from hardware.thresholds import RastreadorAlerta, Status
from notifications.manager import GerenciadorNotificacoes
from recursos import RECURSOS, pior_status
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
        self._status_atual: dict[str, Status] = {}

        self._rastreadores = {r.nome: RastreadorAlerta() for r in RECURSOS}
        self._notificadores = {r.nome: GerenciadorNotificacoes(r) for r in RECURSOS}
        self._cards = {
            r.nome: CartaoRecurso(
                self,
                titulo=r.rotulo,
                descricao_fn=r.descricao,
                formatar_valor=r.formatar_valor,
            )
            for r in RECURSOS
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

    @property
    def pior_status_atual(self) -> Status:
        """O status mais grave entre os recursos disponíveis.

        Calculado em `recursos.py`; aqui só se lê. É o que a bandeja (spec 5) consome.
        """
        return pior_status(self._status_atual.values())

    def _organizar(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        for i, card in enumerate(self._cards.values()):
            pady = (20, 0) if i == 0 else (8, 0)
            card.grid(row=i, column=0, padx=20, pady=pady, sticky="ew")
        self._botao_tema.grid(row=len(self._cards), column=0, pady=16)

    def _esconder_card(self, recurso) -> None:
        """Recurso sem leitura some da tela e sai da conta do pior status.

        Só vale para quem declarou `pode_sumir`: um recurso que sempre existe e
        falhou é problema de coleta, não motivo para a tela mudar sozinha.
        """
        self._status_atual.pop(recurso.nome, None)
        if recurso.pode_sumir:
            self._cards[recurso.nome].grid_remove()

    def _mostrar_card(self, recurso) -> None:
        card = self._cards[recurso.nome]
        if recurso.pode_sumir and not card.winfo_manager():
            card.grid()

    def cards_visiveis(self) -> list[str]:
        """Quais recursos estão na tela agora. Existe para o teste poder verificar.

        Usa `winfo_manager()` e não `winfo_ismapped()`: o segundo só é verdadeiro com a
        janela de fato visível, e nos testes a raiz nunca é exibida.
        """
        return [nome for nome, card in self._cards.items() if card.winfo_manager()]

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
        for recurso in RECURSOS:
            valor = recurso.extrair(dados)
            if valor is None:
                self._esconder_card(recurso)
                continue

            self._mostrar_card(recurso)

            status_bruto = recurso.classificar(valor)
            status = self._rastreadores[recurso.nome].atualizar(status_bruto)
            self._status_atual[recurso.nome] = status
            self._cards[recurso.nome].atualizar(status, valor)

            programa, consumo = self._identificar_programa(recurso, status)
            self._notificadores[recurso.nome].processar(
                status, programa=programa, valor=consumo
            )

    def _identificar_programa(self, recurso, status: Status):
        """Varre só no momento do alerta, e só para quem tem programa associado."""
        if status != Status.ALERTA or not recurso.varre_processos:
            return None, None
        dominante = programa_dominante(recurso.nome)
        if dominante is None:
            return None, None
        return dominante

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
