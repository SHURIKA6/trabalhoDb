"""Tela de login (Tkinter puro). Valida via sp_LoginUsuario."""
import tkinter as tk
from tkinter import messagebox, ttk

try:
    from app import auth as _auth
    from app import db as _db
    from app import ui_theme as T
except ImportError:
    import auth as _auth  # type: ignore
    import db as _db  # type: ignore
    import ui_theme as T  # type: ignore


class LoginFrame(ttk.Frame):
    def __init__(self, parent, on_sucesso):
        super().__init__(parent, style="Ink.TFrame")
        self.on_sucesso = on_sucesso

        cartao = ttk.Frame(self, style="Card.TFrame", padding=(44, 36, 44, 28))
        cartao.pack(expand=True)

        ttk.Label(cartao, text="∞", style="Card.TLabel",
                  foreground=T.GOLD, font=T.FONTS["mark"]).pack(anchor="w")
        ttk.Label(cartao, text="Faculdade do Bug Infinito", style="Card.TLabel",
                  font=T.FONTS["title"]).pack(anchor="w", pady=(2, 4))
        ttk.Label(cartao, text="Entrar com login institucional",
                  style="CardSub.TLabel").pack(anchor="w", pady=(0, 18))

        T.divisor(cartao).pack(fill="x", pady=(0, 18))

        ttk.Label(cartao, text="Login:", style="CardSub.TLabel").pack(anchor="w")
        self.ent_login = ttk.Entry(cartao, width=30, font=T.FONTS["body"])
        self.ent_login.pack(fill="x", pady=(2, 12))
        self.ent_login.bind("<Return>", lambda _e: self.entrar())

        ttk.Label(cartao, text="Senha:", style="CardSub.TLabel").pack(anchor="w")
        self.ent_senha = ttk.Entry(cartao, width=30, show="•", font=T.FONTS["body"])
        self.ent_senha.pack(fill="x", pady=(2, 20))
        self.ent_senha.bind("<Return>", lambda _e: self.entrar())

        self.btn = ttk.Button(cartao, text="Entrar", style="Gold.TButton",
                              command=self.entrar)
        self.btn.pack(fill="x")

        ttk.Label(cartao, text="Autenticacao via CALL sp_LoginUsuario (SHA-256)",
                  style="CardSub.TLabel").pack(anchor="w", pady=(18, 0))

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
