"""Ponto de entrada do SGA (Tkinter puro, sem dependencia pesada)."""
import sys
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")

try:
    from app import ui_theme as T
    from app.ui_login import LoginFrame
    from app.ui_main import MainFrame
except ImportError:
    import ui_theme as T  # type: ignore
    from ui_login import LoginFrame  # type: ignore
    from ui_main import MainFrame  # type: ignore


def main():
    root = tk.Tk()
    root.title("SGA — Faculdade do Bug Infinito")
    root.geometry("1120x700")
    root.minsize(960, 620)
    T.apply_theme(root)

    holder = ttk.Frame(root)
    holder.pack(fill="both", expand=True)

    def mostrar_login():
        for w in holder.winfo_children():
            w.destroy()
        root.configure(bg=T.INK)
        LoginFrame(holder, on_sucesso=mostrar_menu).pack(fill="both", expand=True)

    def mostrar_menu(sessao: dict):
        for w in holder.winfo_children():
            w.destroy()
        root.configure(bg=T.PAPER)
        MainFrame(holder, sessao, on_sair=mostrar_login).pack(fill="both", expand=True)

    mostrar_login()
    root.mainloop()


if __name__ == "__main__":
    main()
