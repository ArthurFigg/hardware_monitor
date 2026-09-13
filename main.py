import time

import customtkinter as ctk

from hardware.collector import segundos_ligado
from historico.banco import Banco
from historico.gravacao import Gravador
from sistema import inicializacao, instancia_unica
from ui.app import AplicativoMonitor


def _abrir_historico() -> tuple[Banco, Gravador]:
    """Sobe o histórico e registra o tempo de PC ligado sem o app.

    Banco que não abre devolve indisponível em vez de erro, e o gravador segue aceitando
    chamadas sem fazer nada: o app roda sem histórico, nunca para por causa dele.
    """
    banco = Banco()
    gravador = Gravador(banco)

    ligado_ha = segundos_ligado()
    if ligado_ha is not None:
        gravador.registrar_lacuna(boot_em=time.time() - ligado_ha)

    return banco, gravador


def main() -> None:
    # Antes de qualquer janela: com o app entrando junto com o Windows, ele já pode
    # estar rodando. A janela que aparece é a da instância que já existe.
    if not instancia_unica.reservar():
        instancia_unica.pedir_para_abrir()
        return

    # A entrada do registro guarda o caminho de onde o executável estava, e sem
    # instalador nada impede que ele tenha sido movido desde então.
    inicializacao.sincronizar()

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    banco, gravador = _abrir_historico()

    raiz = ctk.CTk()
    monitor = AplicativoMonitor(raiz, gravador=gravador)
    monitor.pack(fill="both", expand=True)

    monitor.iniciar_coleta()
    monitor.iniciar_bandeja()
    instancia_unica.vigiar_pedidos(monitor.pedir_para_abrir)

    # Subindo pela entrada do registro, o app não rouba a tela de quem acabou de ligar
    # o computador. Aberto pela pessoa, abre visível como sempre.
    if inicializacao.iniciado_minimizado():
        raiz.iconify()

    raiz.mainloop()

    # Só a saída limpa fecha. Encerrado pelo Gerenciador de Tarefas, o minuto em curso
    # se perde — que é o comportamento que a spec escolheu para a média parcial.
    gravador.fechar()
    banco.fechar()


if __name__ == "__main__":
    main()
