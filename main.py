import customtkinter as ctk

from ui.app import AplicativoMonitor


def main() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    raiz = ctk.CTk()
    monitor = AplicativoMonitor(raiz)
    monitor.pack(fill="both", expand=True)
    raiz.mainloop()


if __name__ == "__main__":
    main()
