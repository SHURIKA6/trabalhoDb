"""Menu principal com controle de permissoes por perfil."""
import tkinter as tk
from tkinter import ttk

try:
    from app import permissoes as P
    from app import ui_theme as T
    from app.ui_alunos import AlunosFrame
    from app.ui_matriculas import MatriculasFrame
    from app.ui_notas import NotasFrame
    from app.ui_relatorios import RelatoriosFrame
except ImportError:
    import permissoes as P  # type: ignore
    import ui_theme as T  # type: ignore
    from ui_alunos import AlunosFrame  # type: ignore
    from ui_matriculas import MatriculasFrame  # type: ignore
    from ui_notas import NotasFrame  # type: ignore
    from ui_relatorios import RelatoriosFrame  # type: ignore


class MainFrame(ttk.Frame):
    """Barra lateral de modulos conforme o perfil + area de trabalho."""

    def __init__(self, parent, sessao: dict, on_sair):
        super().__init__(parent)
        self.sessao = sessao
        self.on_sair = on_sair
        perfil = sessao.get("perfil", "")
        self._nav = {}

        lateral = ttk.Frame(self, style="Ink.TFrame", width=224)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)

        # marca
        marca = ttk.Frame(lateral, style="Ink.TFrame", padding=(16, 20, 16, 14))
        marca.pack(fill="x")
        ttk.Label(marca, text="∞", style="InkMark.TLabel").pack(side="left")
        col = ttk.Frame(marca, style="Ink.TFrame")
        col.pack(side="left", padx=(12, 0))
        ttk.Label(col, text="SGA", style="InkTitle.TLabel").pack(anchor="w")
        ttk.Label(col, text="Faculdade do Bug Infinito", style="InkBrand.TLabel",
                  wraplength=150, justify="left").pack(anchor="w")

        T.divisor(lateral, T.INK_LINE).pack(fill="x", padx=16, pady=(0, 8))

        # navegacao
        nav = ttk.Frame(lateral, style="Ink.TFrame", padding=(12, 4))
        nav.pack(fill="x")

        def botao(texto, cls):
            b = ttk.Button(nav, text=texto, style="Nav.TButton",
                           command=lambda: self.abrir(cls))
            b.pack(fill="x", pady=2)
            self._nav[cls] = b

        # Visiveis para ambos os perfis:
        if P.pode_ver_alunos(perfil):
            botao("Alunos", AlunosFrame)
        if P.pode_matricular(perfil):
            botao("Matriculas", MatriculasFrame)
        if P.pode_ver_boletim(perfil) or P.pode_ver_lotacao(perfil):
            botao("Relatorios", RelatoriosFrame)
        # Exclusivos do Coordenador (Secretario nao ve esse botao):
        if P.pode_lancar_notas(perfil):
            botao("Lancar notas", NotasFrame)

        # rodape: usuario, perfil, sair e nota de acesso
        rodape = ttk.Frame(lateral, style="Ink.TFrame", padding=(16, 12))
        rodape.pack(side="bottom", fill="x")
        ttk.Label(rodape, text=sessao.get("nome", "") or "—",
                  style="InkUser.TLabel").pack(anchor="w")
        ttk.Label(rodape, text=perfil, style="InkPerfil.TLabel").pack(anchor="w")
        ttk.Button(rodape, text="Sair", style="InkGhost.TButton",
                   command=self.on_sair).pack(fill="x", pady=(12, 10))
        T.divisor(rodape, T.INK_LINE).pack(fill="x", pady=(0, 8))
        ttk.Label(rodape, text="Acesso via\nCALL sp_* / vw_*",
                  style="InkSub.TLabel", justify="left").pack(anchor="w")

        # area de trabalho
        self.area = ttk.Frame(self, padding=18)
        self.area.pack(side="left", fill="both", expand=True)
        self._tela_atual = None

        self.abrir(AlunosFrame if P.pode_ver_alunos(perfil) else RelatoriosFrame)

    def abrir(self, cls):
        for c, b in self._nav.items():
            b.configure(style="NavActive.TButton" if c is cls else "Nav.TButton")
        if self._tela_atual is not None:
            self._tela_atual.destroy()
        self._tela_atual = cls(self.area, self.sessao)
        self._tela_atual.pack(fill="both", expand=True)
