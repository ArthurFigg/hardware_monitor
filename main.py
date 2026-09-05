import customtkinter as ctk

from sistema import inicializacao, instancia_unica
from ui.app import AplicativoMonitor


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

    raiz = ctk.CTk()
    monitor = AplicativoMonitor(raiz)
    monitor.pack(fill="both", expand=True)

    monitor.iniciar_coleta()
    monitor.iniciar_bandeja()
    instancia_unica.vigiar_pedidos(monitor.pedir_para_abrir)

    # Subindo pela entrada do registro, o app não rouba a tela de quem acabou de ligar
    # o computador. Aberto pela pessoa, abre visível como sempre.
    if inicializacao.iniciado_minimizado():
        raiz.iconify()

    raiz.mainloop()


if __name__ == "__main__":
    main()
