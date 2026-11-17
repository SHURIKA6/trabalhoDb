"""Tela de login (Tkinter puro). Valida via sp_LoginUsuario."""
import tkinter as tk
from tkinter import messagebox, ttk

try:
    from app import auth as _auth
    from app import db as _db
except ImportError:
    import auth as _auth  # type: ignore
    import db as _db  # type: ignore


class LoginFrame(ttk.Frame):
    def __init__(self, parent, on_sucesso):
        super().__init__(parent, padding=24)
        self.on_sucesso = on_sucesso

        ttk.Label(self, text="SGA — Faculdade do Bug Infinito",
                  font=("TkDefaultFont", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 4))
        ttk.Label(self, text="Entrar com login institucional").grid(row=1, column=0, columnspan=2, pady=(0, 16))

        ttk.Label(self, text="Login:").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=4)
        self.ent_login = ttk.Entry(self, width=28)
        self.ent_login.grid(row=2, column=1, pady=4, sticky="w")

        ttk.Label(self, text="Senha:").grid(row=3, column=0, sticky="e", padx=(0, 8), pady=4)
        self.ent_senha = ttk.Entry(self, width=28, show="•")
        self.ent_senha.grid(row=3, column=1, pady=4, sticky="w")
        self.ent_senha.bind("<Return>", lambda _e: self.entrar())

        self.btn = ttk.Button(self, text="Entrar", command=self.entrar)
        self.btn.grid(row=4, column=0, columnspan=2, pady=16)

        self.ent_login.focus_set()

    def entrar(self):
        login = self.ent_login.get()
        senha = self.ent_senha.get()
        if not login.strip() or not senha:
            messagebox.showwarning("Login", "Preencha login e senha.")
            return
        try:
            sessao = _auth.autenticar(login, senha)
        except ValueError as e:
            messagebox.showwarning("Login", str(e))
            return
        except Exception as e:
            messagebox.showerror("Login", _db.erro_amigavel(e))
            return
        if not sessao or not sessao.get("id_usuario"):
            messagebox.showerror("Login", "Login ou senha invalidos.")
            return
        if sessao.get("perfil") not in ("Coordenador", "Secretario"):
            messagebox.showerror("Login", f"Perfil desconhecido: {sessao.get('perfil')!r}.")
            return
        self.on_sucesso(sessao)
