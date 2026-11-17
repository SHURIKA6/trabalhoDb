"""Cadastro de alunos — Secretario e Coordenador.

Leitura via CALL sp_listar_alunos (fallback: SELECT vw_alunos).
Escrita somente via CALL sp_criar_aluno / sp_editar_aluno / sp_excluir_aluno
(definidas em sql/05_sp_apoio.sql). Nenhum INSERT/UPDATE/DELETE direto.
"""
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

try:
    from app import db as _db
    from app import ui_theme as T
except ImportError:
    import db as _db  # type: ignore
    import ui_theme as T  # type: ignore


def listar_alunos():
    """Retorna lista de dicts de alunos (procedure apoio ou view)."""
    try:
        sets = _db.call_procedure("sp_listar_alunos", ())
        if sets and sets[0]:
            return sets[0]
    except Exception:
        pass
    # Fallback conforme edital: leitura via view.
    return _db.select_view("vw_alunos", order_by=None)


class AlunosFrame(ttk.Frame):
    COLS = ("id", "nome", "cpf", "email", "curso", "status")

    def __init__(self, parent, sessao: dict):
        super().__init__(parent)
        self.sessao = sessao

        T.screen_header(self, "Alunos")

        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(0, 10))
        ttk.Button(barra, text="Atualizar", command=self.carregar).pack(side="left")
        ttk.Button(barra, text="Cadastrar", style="Primary.TButton",
                   command=self.cadastrar).pack(side="left", padx=6)
        ttk.Button(barra, text="Editar", command=self.editar).pack(side="left")
        ttk.Button(barra, text="Excluir", style="Danger.TButton",
                   command=self.excluir).pack(side="left", padx=6)

        moldura = T.moldura(self)
        moldura.pack(side="left", fill="both", expand=True)
        self.tree = ttk.Treeview(moldura, columns=self.COLS, show="headings", height=16)
        for c, titulo, larg in (("id", "RA/ID", 80), ("nome", "Nome", 220),
                                ("cpf", "CPF", 120), ("email", "E-mail", 200),
                                ("curso", "Curso", 160), ("status", "Status", 100)):
            self.tree.heading(c, text=titulo, anchor="w" if c != "id" else "center")
            self.tree.column(c, width=larg, anchor="w" if c != "id" else "center")
        scroll = ttk.Scrollbar(moldura, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="left", fill="y")
        T.tag_setup(self.tree)

        self.carregar()

    # -- dados ------------------------------------------------------------
    def carregar(self):
        T.tree_clear(self.tree)
        try:
            for a in listar_alunos():
                T.tree_insert(self.tree, (
                    a.get("id_aluno", a.get("ra", a.get("id", ""))),
                    a.get("nome", ""),
                    a.get("cpf", ""),
                    a.get("email", ""),
                    a.get("curso", a.get("nome_curso", a.get("id_curso", ""))),
                    a.get("status", a.get("situacao", "")),
                ), status_idx=5)
        except Exception as e:
            messagebox.showerror("Alunos", _db.erro_amigavel(e))

    def _selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Alunos", "Selecione um aluno na lista.")
            return None
        return self.tree.item(sel[0], "values")

    # -- escrita: somente CALL -------------------------------------------
    def cadastrar(self):
        nome = simpledialog.askstring("Cadastrar aluno", "Nome completo:")
        if not nome:
            return
        cpf = simpledialog.askstring("Cadastrar aluno", "CPF:") or ""
        email = simpledialog.askstring("Cadastrar aluno", "E-mail:") or ""
        id_curso = simpledialog.askstring("Cadastrar aluno", "ID do curso:") or ""
        if not id_curso.strip():
            messagebox.showwarning("Cadastrar aluno", "ID do curso e obrigatorio.")
            return
        try:
            _db.call_procedure("sp_criar_aluno", (nome.strip(), cpf.strip(), email.strip(), id_curso.strip()))
            messagebox.showinfo("Alunos", "Aluno cadastrado.")
            self.carregar()
        except Exception as e:
            messagebox.showerror("Alunos", _db.erro_amigavel(e))

    def editar(self):
        vals = self._selecionado()
        if not vals:
            return
        id_aluno, nome0, cpf0, email0 = vals[0], vals[1], vals[2], vals[3]
        nome = simpledialog.askstring("Editar aluno", "Nome:", initialvalue=nome0)
        if nome is None:
            return
        email = simpledialog.askstring("Editar aluno", "E-mail:", initialvalue=email0) or ""
        try:
            _db.call_procedure("sp_editar_aluno", (id_aluno, nome.strip(), email.strip()))
            messagebox.showinfo("Alunos", "Aluno atualizado.")
            self.carregar()
        except Exception as e:
            messagebox.showerror("Alunos", _db.erro_amigavel(e))

    def excluir(self):
        vals = self._selecionado()
        if not vals:
            return
        if not messagebox.askyesno("Excluir aluno", f"Excluir aluno {vals[1]} (RA/ID {vals[0]})?"):
            return
        try:
            _db.call_procedure("sp_excluir_aluno", (vals[0],))
            messagebox.showinfo("Alunos", "Aluno excluido.")
            self.carregar()
        except Exception as e:
            messagebox.showerror("Alunos", _db.erro_amigavel(e))
