"""Matriculas — Secretario e Coordenador.

Lotacao via SELECT vw_turmas_lotacao; matricula via CALL sp_matricular_aluno.
Erros de regra (SIGNAL 1644 / SQLSTATE 45000: turma lotada, sem
pre-requisito, aluno trancado) sao traduzidos em mensagem amigavel.
"""
import tkinter as tk
from tkinter import messagebox, ttk

try:
    from app import db as _db
except ImportError:
    import db as _db  # type: ignore


class MatriculasFrame(ttk.Frame):
    def __init__(self, parent, sessao: dict):
        super().__init__(parent)
        self.sessao = sessao
        self._turmas = []

        ttk.Label(self, text="Matricula de aluno em turma",
                  font=("TkDefaultFont", 12, "bold")).pack(anchor="w", pady=(0, 8))

        form = ttk.Frame(self)
        form.pack(fill="x", pady=4)
        ttk.Label(form, text="RA / ID aluno:").grid(row=0, column=0, sticky="e", padx=(0, 8), pady=4)
        self.ent_aluno = ttk.Entry(form, width=20)
        self.ent_aluno.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(form, text="Turma:").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=4)
        self.cmb_turma = ttk.Combobox(form, width=60, state="readonly")
        self.cmb_turma.grid(row=1, column=1, sticky="w", pady=4)

        botoes = ttk.Frame(self)
        botoes.pack(fill="x", pady=8)
        ttk.Button(botoes, text="Recarregar turmas", command=self.carregar_turmas).pack(side="left")
        ttk.Button(botoes, text="Matricular", command=self.matricular).pack(side="left", padx=8)

        ttk.Label(self, text="Lotacao das turmas (vw_turmas_lotacao):").pack(anchor="w", pady=(8, 2))
        self.tree = ttk.Treeview(self, columns=("turma", "disc", "vagas", "ocup", "sem"),
                                 show="headings", height=14)
        for c, t, w in (("turma", "Turma", 90), ("disc", "Disciplina", 260),
                        ("vagas", "Capacidade", 100), ("ocup", "Ocupadas", 100),
                        ("sem", "Semestre", 120)):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True)

        self.carregar_turmas()

    def carregar_turmas(self):
        try:
            rows = _db.select_view("vw_turmas_lotacao")
        except Exception as e:
            messagebox.showerror("Matriculas", _db.erro_amigavel(e))
            return
        self._turmas = rows
        for i in self.tree.get_children():
            self.tree.delete(i)
        opcoes = []
        for t in rows:
            tid = t.get("id_turma", t.get("turma", "?"))
            disc = t.get("disciplina", t.get("nome_disciplina", t.get("id_disciplina", "")))
            cap = t.get("capacidade", t.get("vagas", "?"))
            ocup = t.get("ocupadas", t.get("matriculados", t.get("total", "?")))
            sem = t.get("semestre", t.get("ano_semestre", ""))
            self.tree.insert("", "end", values=(tid, disc, cap, ocup, sem))
            opcoes.append(f"{tid} — {disc} (ocup. {ocup}/{cap})")
        self.cmb_turma["values"] = opcoes
        if opcoes:
            self.cmb_turma.current(0)

    def matricular(self):
        ra = self.ent_aluno.get().strip()
        if not ra:
            messagebox.showwarning("Matricula", "Informe o RA/ID do aluno.")
            return
        if not self._turmas or self.cmb_turma.current() < 0:
            messagebox.showwarning("Matricula", "Selecione uma turma.")
            return
        turma = self._turmas[self.cmb_turma.current()]
        id_turma = turma.get("id_turma", turma.get("turma"))
        try:
            _db.call_procedure("sp_matricular_aluno", (ra, id_turma))
            messagebox.showinfo("Matricula", "Matricula realizada com sucesso.")
            self.carregar_turmas()
        except Exception as e:
            # 45000 aqui significa regra academica (lotada, pre-requisito, trancado).
            messagebox.showerror("Matricula nao realizada", _db.erro_amigavel(e))
