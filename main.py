import customtkinter as ctk

from sistema import inicializacao
from ui.app import AplicativoMonitor


def main() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    raiz = ctk.CTk()
    monitor = AplicativoMonitor(raiz)
    monitor.pack(fill="both", expand=True)

    # Subindo pela entrada do registro, o app não rouba a tela de quem acabou de ligar
    # o computador. Aberto pela pessoa, abre visível como sempre.
    if inicializacao.iniciado_minimizado():
        raiz.iconify()

    raiz.mainloop()


if __name__ == "__main__":
    main()
