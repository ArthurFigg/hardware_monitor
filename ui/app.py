import threading

import customtkinter as ctk

from hardware.collector import coletar, segundos_ligado
from hardware.processos import programa_dominante
from hardware.thresholds import RastreadorAlerta, Status
from notifications.manager import GerenciadorNotificacoes
from recursos import RECURSOS, pior_status
from sistema import inicializacao, uptime
from ui.components.cards import CartaoRecurso

AVISO_FALHA_ATIVAR = (
    "Não foi possível ativar. Algum programa de segurança pode estar bloqueando."
)
# A falha ao desativar é a pior das duas: a caixa desmarcada diz que o app não vai
# abrir, e ele abre. A pessoa descobre pela presença, sem entender de onde veio.
AVISO_FALHA_DESATIVAR = (
    "Não foi possível desativar. O app ainda vai abrir junto com o Windows — "
    "algum programa de segurança pode estar bloqueando."
)


class AplicativoMonitor(ctk.CTkFrame):
    _INTERVALO_VERIFICACAO_MS = 100
    # O rodapé muda de minuto em minuto. Reler a cada segundo faria o texto piscar sem
    # que nada tivesse mudado.
    _INTERVALO_UPTIME_MS = 60_000

    def __init__(self, master: ctk.CTk, **kwargs):
        super().__init__(master, **kwargs)

        self._preparar_janela(master)

        self._rodando = True
        self._dados_pendentes = None
        self._lock = threading.Lock()
        self._status_atual: dict[str, Status] = {}

        self._rastreadores = {r.nome: RastreadorAlerta() for r in RECURSOS}
        self._notificadores = {r.nome: GerenciadorNotificacoes(r) for r in RECURSOS}
        self._cards = self._criar_cards()
        self._criar_rodape()

        self._organizar()
        self._iniciar_coleta()
        self._agendar_atualizacao()
        self._atualizar_uptime()

    def _preparar_janela(self, master: ctk.CTk) -> None:
        master.title("Monitor de Hardware")
        master.resizable(False, False)
        master.protocol("WM_DELETE_WINDOW", self._ao_fechar)

    def _criar_cards(self) -> dict:
        return {
            r.nome: CartaoRecurso(
                self,
                titulo=r.rotulo,
                descricao_fn=r.descricao_de,
                formatar_valor=r.formatar_valor,
                linha_extra_fn=r.linha_extra,
            )
            for r in RECURSOS
        }

    def _criar_rodape(self) -> None:
        """Interruptor, botão de tema, uptime e a linha de aviso, nesta ordem visual.

        Tudo em `grid` dentro de um frame próprio, e não em `pack`: a regra de packing do
        projeto (`side="right"` antes de qualquer `expand=True`) é fácil de violar sem
        perceber, e o `grid` não tem esse problema.
        """
        self._rodape = ctk.CTkFrame(self, fg_color="transparent")

        self._interruptor_inicio = ctk.CTkSwitch(
            self._rodape,
            text="Abrir junto com o Windows",
            font=ctk.CTkFont(size=12),
            command=self._alternar_inicio,
        )
        # A entrada no registro é o estado: o interruptor nasce do que está lá agora, e
        # não de arquivo de configuração que poderia discordar da realidade.
        if inicializacao.ativado():
            self._interruptor_inicio.select()

        self._botao_tema = ctk.CTkButton(
            self._rodape,
            text="Modo Claro",
            width=120,
            height=28,
            command=self._alternar_tema,
        )
        self._label_aviso_inicio = ctk.CTkLabel(
            self._rodape,
            text="",
            wraplength=320,
            justify="left",
            font=ctk.CTkFont(size=11),
            anchor="w",
        )
        self._label_uptime = ctk.CTkLabel(
            self._rodape,
            text="",
            font=ctk.CTkFont(size=11),
            anchor="w",
        )

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

        self._rodape.grid(
            row=len(self._cards), column=0, sticky="ew", padx=20, pady=(16, 16)
        )
        self._rodape.grid_columnconfigure(0, weight=1)
        self._interruptor_inicio.grid(row=0, column=0, sticky="w")
        self._botao_tema.grid(row=0, column=1, sticky="e")
        self._label_aviso_inicio.grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )
        self._label_aviso_inicio.grid_remove()
        self._label_uptime.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self._label_uptime.grid_remove()

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
        # App parado não mexe mais na tela. Sem isso, um callback já agendado ainda
        # dispara depois do fechamento e escreve em widget em destruição.
        if not self._rodando:
            return

        with self._lock:
            dados = self._dados_pendentes
            self._dados_pendentes = None

        if dados is not None:
            self._atualizar_cards(dados)

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
                status,
                causa=recurso.causa(valor),
                programa=programa,
                valor=consumo,
                leitura=valor,
            )

    def _identificar_programa(self, recurso, status: Status):
        """Varre só no momento do alerta, e só para quem tem programa associado."""
        if status != Status.ALERTA or not recurso.varre_processos:
            return None, None
        dominante = programa_dominante(recurso.nome)
        if dominante is None:
            return None, None
        return dominante

    @property
    def abrir_com_o_windows(self) -> bool:
        """Estado do interruptor na tela. Existe para o teste poder verificar."""
        return bool(self._interruptor_inicio.get())

    @property
    def aviso_inicio(self) -> str:
        return self._label_aviso_inicio.cget("text")

    @property
    def texto_uptime(self) -> str:
        return self._label_uptime.cget("text")

    def _alternar_inicio(self) -> None:
        """Ação que a pessoa pediu — falhar calado faria o interruptor mentir.

        Vale nos dois sentidos. Se a escrita não passa (antivírus, política
        corporativa), o interruptor volta sozinho para o que o registro de fato diz e a
        linha explica. Só voltar, sem texto, pareceria defeito do app.
        """
        if self._interruptor_inicio.get():
            self._aplicar_inicio(
                inicializacao.ativar, volta_para_marcado=False, aviso=AVISO_FALHA_ATIVAR
            )
            return

        self._aplicar_inicio(
            inicializacao.desativar,
            volta_para_marcado=True,
            aviso=AVISO_FALHA_DESATIVAR,
        )

    def _aplicar_inicio(self, acao, volta_para_marcado: bool, aviso: str) -> None:
        if acao():
            self._mostrar_aviso_inicio("")
            return

        if volta_para_marcado:
            self._interruptor_inicio.select()
        else:
            self._interruptor_inicio.deselect()
        self._mostrar_aviso_inicio(aviso)

    def _mostrar_aviso_inicio(self, texto: str) -> None:
        self._label_aviso_inicio.configure(text=texto)
        if texto:
            self._label_aviso_inicio.grid()
        else:
            self._label_aviso_inicio.grid_remove()

    def _atualizar_uptime(self) -> None:
        if not self._rodando:
            return

        texto = uptime.formatar(segundos_ligado())
        self._label_uptime.configure(text=texto)
        if texto:
            self._label_uptime.grid()
        else:
            self._label_uptime.grid_remove()

        self.after(self._INTERVALO_UPTIME_MS, self._atualizar_uptime)

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
