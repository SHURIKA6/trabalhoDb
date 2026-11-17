"""Menu principal com controle de permissoes por perfil."""
import tkinter as tk
from tkinter import ttk

try:
    from app import permissoes as P
    from app.ui_alunos import AlunosFrame
    from app.ui_matriculas import MatriculasFrame
    from app.ui_notas import NotasFrame
    from app.ui_relatorios import RelatoriosFrame
except ImportError:
    import permissoes as P  # type: ignore
    from ui_alunos import AlunosFrame  # type: ignore
    from ui_matriculas import MatriculasFrame  # type: ignore
    from ui_notas import NotasFrame  # type: ignore
    from ui_relatorios import RelatoriosFrame  # type: ignore


class MainFrame(ttk.Frame):
    """Container com barra lateral de modulos conforme o perfil."""

    def __init__(self, parent, sessao: dict, on_sair):
        super().__init__(parent)
        self.sessao = sessao
        self.on_sair = on_sair
        perfil = sessao.get("perfil", "")

        topo = ttk.Frame(self, padding=(12, 10))
        topo.pack(fill="x")
        ttk.Label(topo, text=f"SGA — Faculdade do Bug Infinito",
                  font=("TkDefaultFont", 12, "bold")).pack(side="left")
        ttk.Label(topo, text=f"  {sessao.get('nome','')}  ({perfil})").pack(side="left")
        ttk.Button(topo, text="Sair", command=self.on_sair).pack(side="right")

        corpo = ttk.Frame(self)
        corpo.pack(fill="both", expand=True)
        lateral = ttk.Frame(corpo, padding=10, width=190)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        self.area = ttk.Frame(corpo, padding=10)
        self.area.pack(side="left", fill="both", expand=True)
        self._tela_atual = None

        def botao(texto, cls):
            ttk.Button(lateral, text=texto,
                       command=lambda: self.abrir(cls)).pack(fill="x", pady=3)

        # Visiveis para ambos os perfis:
        if P.pode_ver_alunos(perfil):
            botao("Alunos", AlunosFrame)
        if P.pode_matricular(perfil):
            botao("Matriculas", MatriculasFrame)
        if P.pode_ver_boletim(perfil) or P.pode_ver_lotacao(perfil):
            botao("Relatorios", RelatoriosFrame)
        # Exclusivos do Coordenador (Secretario nao ve esses botoes):
        if P.pode_lancar_notas(perfil):
            botao("Lancar notas", NotasFrame)

        ttk.Label(lateral, text="").pack(pady=6)
        ttk.Label(lateral, text="Acesso via\nCALL sp_* / vw_*",
                  foreground="gray", justify="center").pack()

        self.abrir(AlunosFrame if P.pode_ver_alunos(perfil) else RelatoriosFrame)

    def abrir(self, cls):
        if self._tela_atual is not None:
            self._tela_atual.destroy()
        self._tela_atual = cls(self.area, self.sessao)
        self._tela_atual.pack(fill="both", expand=True)
