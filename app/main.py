"""Ponto de entrada do SGA (Tkinter puro, sem dependencia pesada)."""
import sys
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")

try:
    from app.ui_login import LoginFrame
    from app.ui_main import MainFrame
except ImportError:
    from ui_login import LoginFrame  # type: ignore
    from ui_main import MainFrame  # type: ignore


def main():
    root = tk.Tk()
    root.title("SGA — Faculdade do Bug Infinito")
    root.geometry("1020x660")
    try:
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass

    holder = ttk.Frame(root)
    holder.pack(fill="both", expand=True)

    def mostrar_login():
        for w in holder.winfo_children():
            w.destroy()
        LoginFrame(holder, on_sucesso=mostrar_menu).pack(expand=True)

    def mostrar_menu(sessao: dict):
        for w in holder.winfo_children():
            w.destroy()
        MainFrame(holder, sessao, on_sair=mostrar_login).pack(fill="both", expand=True)

    mostrar_login()
    root.mainloop()


if __name__ == "__main__":
    main()
