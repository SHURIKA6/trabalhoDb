"""Cadastro de alunos — Secretario e Coordenador.

Leitura via CALL sp_listar_alunos (fallback: SELECT vw_alunos).
Escrita somente via CALL sp_criar_aluno / sp_editar_aluno / sp_excluir_aluno
(definidas em sql/05_sp_apoio.sql). Nenhum INSERT/UPDATE/DELETE direto.

Painel inferior "Matriculas do aluno": ao selecionar um aluno na lista,
mostra as matriculas dele em turmas (SELECT vw_boletim WHERE id_aluno = ?).
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


def listar_matriculas_aluno(id_aluno):
    """Matriculas de um aluno em turmas — leitura somente por view (vw_boletim)."""
    return _db.select_view(
        "vw_boletim",
        filters={"id_aluno": id_aluno},
        order_by=["semestre", "disciplina"],
    )


class AlunosFrame(ttk.Frame):
    COLS = ("id", "ra", "nome", "cpf", "email", "curso", "status")
    COLS_MAT = ("mat", "turma", "disc", "sem", "prof", "sit", "media")

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

        # -- lista de alunos --------------------------------------------------
        moldura = T.moldura(self)
        moldura.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(moldura, columns=self.COLS, show="headings", height=10)
        for c, titulo, larg, ancor in (
                ("id",    "ID",               55,  "center"),
                ("ra",    "Matricula (RA)",   115, "center"),
                ("nome",  "Nome",             200, "w"),
                ("cpf",   "CPF",              115, "w"),
                ("email", "E-mail",           180, "w"),
                ("curso", "Curso",            140, "w"),
                ("status", "Status",          85,  "w")):
            self.tree.heading(c, text=titulo, anchor=ancor)
            self.tree.column(c, width=larg, anchor=ancor)
        scroll = ttk.Scrollbar(moldura, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="left", fill="y")
        T.tag_setup(self.tree)
        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar)

        # -- painel: matriculas do aluno selecionado --------------------------
        card = ttk.Frame(self, style="Card.TFrame", padding=(12, 10, 12, 12))
        card.pack(fill="x", pady=(10, 0))
        topo = ttk.Frame(card, style="Card.TFrame")
        topo.pack(fill="x")
        ttk.Label(topo, text="Matriculas do aluno",
                  style="CardTitle.TLabel").pack(side="left")
        self.lbl_aluno = ttk.Label(topo, text="Selecione um aluno na lista acima.",
                                   style="CardSub.TLabel")
        self.lbl_aluno.pack(side="right")

        mframe = ttk.Frame(card, style="Card.TFrame")
        mframe.pack(fill="x", pady=(8, 0))
        self.tree_mat = ttk.Treeview(mframe, columns=self.COLS_MAT,
                                     show="headings", height=6)
        for c, titulo, larg, ancor in (
                ("mat",   "Matricula",  80,  "center"),
                ("turma", "Turma",      60,  "center"),
                ("disc",  "Disciplina", 210, "w"),
                ("sem",   "Semestre",   90,  "w"),
                ("prof",  "Professor",  150, "w"),
                ("sit",   "Situacao",   100, "w"),
                ("media", "Media",      70,  "center")):
            self.tree_mat.heading(c, text=titulo, anchor=ancor)
            self.tree_mat.column(c, width=larg, anchor=ancor)
        scroll2 = ttk.Scrollbar(mframe, orient="vertical", command=self.tree_mat.yview)
        self.tree_mat.configure(yscrollcommand=scroll2.set)
        self.tree_mat.pack(side="left", fill="x", expand=True)
        scroll2.pack(side="left", fill="y")
        T.tag_setup(self.tree_mat)

        self.carregar()

    # -- dados ------------------------------------------------------------
    def carregar(self):
        T.tree_clear(self.tree)
        self._limpar_matriculas()
        try:
            for a in listar_alunos():
                T.tree_insert(self.tree, (
                    a.get("id_aluno", a.get("id", "")),
                    a.get("ra", ""),
                    a.get("nome", ""),
                    a.get("cpf", ""),
                    a.get("email", ""),
                    a.get("curso", a.get("nome_curso", a.get("id_curso", ""))),
                    a.get("status", a.get("situacao", "")),
                ), status_idx=6)
        except Exception as e:
            messagebox.showerror("Alunos", _db.erro_amigavel(e))

    # -- painel de matriculas ----------------------------------------------
    def _limpar_matriculas(self):
        T.tree_clear(self.tree_mat)
        self.lbl_aluno.configure(text="Selecione um aluno na lista acima.")

    def _ao_selecionar(self, _evento=None):
        sel = self.tree.selection()
        if not sel:
            self._limpar_matriculas()
            return
        vals = self.tree.item(sel[0], "values")
        id_aluno, ra, nome = vals[0], vals[1], vals[2]
        T.tree_clear(self.tree_mat)
        try:
            try:
                ref = int(str(id_aluno))
            except (TypeError, ValueError):
                ref = id_aluno
            total = 0
            for m in listar_matriculas_aluno(ref):
                media = m.get("media_final")
                T.tree_insert(self.tree_mat, (
                    m.get("id_matricula", ""),
                    m.get("id_turma", ""),
                    m.get("disciplina", ""),
                    m.get("semestre", ""),
                    m.get("professor") or "—",
                    m.get("situacao", ""),
                    "—" if media in (None, "") else media,
                ), status_idx=5)
                total += 1
        except Exception as e:
            messagebox.showerror("Alunos", _db.erro_amigavel(e))
            return
        ident = f"Matricula (RA) {ra}" if ra else f"ID {id_aluno}"
        sufixo = f" — {total} matricula(s)" if total else " — sem matriculas"
        self.lbl_aluno.configure(text=f"{nome} · {ident}{sufixo}")

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
            sets = _db.call_procedure(
                "sp_criar_aluno",
                (nome.strip(), cpf.strip(), email.strip(), id_curso.strip()))
            ra = ""
            if sets and sets[0]:
                ra = sets[0][0].get("ra", "") or ""
            if ra:
                messagebox.showinfo("Alunos", f"Aluno cadastrado.\nMatricula (RA): {ra}")
            else:
                messagebox.showinfo("Alunos", "Aluno cadastrado.")
            self.carregar()
        except Exception as e:
            messagebox.showerror("Alunos", _db.erro_amigavel(e))

    def editar(self):
        vals = self._selecionado()
        if not vals:
            return
        id_aluno, nome0, email0 = vals[0], vals[2], vals[4]
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
        if not messagebox.askyesno(
                "Excluir aluno",
                f"Excluir aluno {vals[2]} (Matricula {vals[1]}, ID {vals[0]})?"):
            return
        try:
            _db.call_procedure("sp_excluir_aluno", (vals[0],))
            messagebox.showinfo("Alunos", "Aluno excluido.")
            self.carregar()
        except Exception as e:
            messagebox.showerror("Alunos", _db.erro_amigavel(e))
