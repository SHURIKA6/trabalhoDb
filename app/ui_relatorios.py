"""Relatorios e operacoes de encerramento.

Leituras (ambos os perfis, salvo indicacao):
- Boletim: SELECT vw_boletim (filtro por RA).
- Lotacao: SELECT vw_turmas_lotacao.
Apenas Coordenador:
- Desempenho: SELECT vw_desempenho_turma.
- Faturamento por curso: derivado de vw_desempenho_turma (colunas de
  alunos/mensalidade quando existirem; caso contrario contagem).
- Fechar semestre: CALL sp_fechar_semestre.
- Auditoria: CALL sp_listar_log (apoio) com fallback p/ vw_log_nota.
- Historico do aluno: CALL sp_historico_aluno.
"""
import tkinter as tk
from tkinter import messagebox, ttk

try:
    from app import db as _db
    from app import permissoes as P
    from app import ui_theme as T
except ImportError:
    import db as _db  # type: ignore
    import permissoes as P  # type: ignore
    import ui_theme as T  # type: ignore


def _tabela(pai, colunas):
    moldura = T.moldura(pai)
    moldura.pack(side="left", fill="both", expand=True, pady=(8, 0))
    tree = ttk.Treeview(moldura, columns=[c[0] for c in colunas], show="headings", height=12)
    for cid, titulo, larg in colunas:
        tree.heading(cid, text=titulo, anchor="w")
        tree.column(cid, width=larg)
    sb = ttk.Scrollbar(moldura, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="left", fill="y")
    T.tag_setup(tree)
    return tree


class RelatoriosFrame(ttk.Frame):
    def __init__(self, parent, sessao: dict):
        super().__init__(parent)
        self.sessao = sessao
        perfil = sessao.get("perfil", "")
        self.coord = P.eh_coordenador(perfil)

        T.screen_header(self, "Relatorios")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, pady=(6, 0))

        self.aba_boletim = ttk.Frame(nb, style="Card.TFrame", padding=10)
        self.aba_hist = ttk.Frame(nb, style="Card.TFrame", padding=10)
        self.aba_lot = ttk.Frame(nb, style="Card.TFrame", padding=10)
        nb.add(self.aba_boletim, text="Boletim")
        nb.add(self.aba_hist, text="Historico")
        nb.add(self.aba_lot, text="Lotacao")
        if self.coord:
            self.aba_des = ttk.Frame(nb, style="Card.TFrame", padding=10)
            self.aba_fin = ttk.Frame(nb, style="Card.TFrame", padding=10)
            self.aba_fech = ttk.Frame(nb, style="Card.TFrame", padding=10)
            self.aba_log = ttk.Frame(nb, style="Card.TFrame", padding=10)
            nb.add(self.aba_des, text="Desempenho")
            nb.add(self.aba_fin, text="Faturamento")
            nb.add(self.aba_fech, text="Fechar semestre")
            nb.add(self.aba_log, text="Auditoria (log_nota)")

        self._montar_boletim()
        self._montar_historico()
        self._montar_lotacao()
        if self.coord:
            self._montar_desempenho()
            self._montar_faturamento()
            self._montar_fechar()
            self._montar_log()

    # -- boletim ----------------------------------------------------------
    def _montar_boletim(self):
        topo = ttk.Frame(self.aba_boletim, style="Card.TFrame")
        topo.pack(fill="x")
        ttk.Label(topo, text="RA / ID aluno:", style="Card.TLabel").pack(side="left")
        self.ent_ra_bol = ttk.Entry(topo, width=16, font=T.FONTS["body"])
        self.ent_ra_bol.pack(side="left", padx=(6, 8))
        ttk.Button(topo, text="Consultar (vw_boletim)",
                   command=self.consultar_boletim).pack(side="left")
        self.tree_bol = _tabela(self.aba_boletim,
                                [("a", "Aluno/RA", 120), ("b", "Disciplina", 220),
                                 ("c", "N1", 60), ("d", "N2", 60),
                                 ("e", "Media", 70), ("f", "Situacao", 130)])

    def consultar_boletim(self):
        ra = self.ent_ra_bol.get().strip()
        T.tree_clear(self.tree_bol)
        try:
            rows = []
            if ra:
                for col in ("ra", "id_aluno", "RA"):
                    try:
                        rows = _db.select_view("vw_boletim", filters={col: ra})
                        if rows:
                            break
                    except Exception:
                        continue
                if not rows:
                    todas = _db.select_view("vw_boletim", limit=500)
                    rows = [r for r in todas
                            if str(r.get("ra", r.get("id_aluno", r.get("RA", "")))) == ra]
            else:
                rows = _db.select_view("vw_boletim", limit=200)
            for r in rows:
                T.tree_insert(self.tree_bol, (
                    r.get("ra", r.get("id_aluno", r.get("aluno", ""))),
                    r.get("disciplina", r.get("nome_disciplina", "")),
                    r.get("n1", ""), r.get("n2", ""),
                    r.get("media", r.get("media_final", "")),
                    r.get("situacao", r.get("status", "")),
                ), status_idx=5)
        except Exception as e:
            messagebox.showerror("Boletim", _db.erro_amigavel(e))

    # -- historico --------------------------------------------------------
    def _montar_historico(self):
        topo = ttk.Frame(self.aba_hist, style="Card.TFrame")
        topo.pack(fill="x")
        ttk.Label(topo, text="RA / ID aluno:", style="Card.TLabel").pack(side="left")
        self.ent_ra_hist = ttk.Entry(topo, width=16, font=T.FONTS["body"])
        self.ent_ra_hist.pack(side="left", padx=(6, 8))
        ttk.Button(topo, text="Consultar (sp_historico_aluno)",
                   command=self.consultar_hist).pack(side="left")
        self.tree_hist = _tabela(self.aba_hist,
                                 [("a", "Disciplina", 240), ("b", "Media", 80),
                                  ("c", "Situacao", 140), ("d", "Semestre", 120)])

    def consultar_hist(self):
        ra = self.ent_ra_hist.get().strip()
        if not ra:
            messagebox.showwarning("Historico", "Informe o RA/ID do aluno.")
            return
        T.tree_clear(self.tree_hist)
        try:
            sets = _db.call_procedure("sp_historico_aluno", (ra,))
            rows = sets[0] if sets else []
            for r in rows:
                T.tree_insert(self.tree_hist, (
                    r.get("disciplina", r.get("nome_disciplina", "")),
                    r.get("media", r.get("media_final", "")),
                    r.get("situacao", r.get("status", "")),
                    r.get("semestre", r.get("ano_semestre", "")),
                ), status_idx=2)
            if not rows:
                messagebox.showinfo("Historico", "Sem registros para este aluno.")
        except Exception as e:
            messagebox.showerror("Historico", _db.erro_amigavel(e))

    # -- lotacao ----------------------------------------------------------
    def _montar_lotacao(self):
        ttk.Button(self.aba_lot, text="Atualizar (vw_turmas_lotacao)",
                   command=self.consultar_lot).pack(anchor="w")
        self.tree_lot = _tabela(self.aba_lot,
                                [("a", "Turma", 90), ("b", "Disciplina", 240),
                                 ("c", "Capacidade", 100), ("d", "Ocupadas", 100),
                                 ("e", "Semestre", 120)])
        self.consultar_lot()

    def consultar_lot(self):
        T.tree_clear(self.tree_lot)
        try:
            for t in _db.select_view("vw_turmas_lotacao"):
                T.tree_insert(self.tree_lot, (
                    t.get("id_turma", t.get("turma", "")),
                    t.get("disciplina", t.get("nome_disciplina", "")),
                    t.get("capacidade", t.get("vagas_totais", t.get("vagas", ""))),
                    t.get("ocupadas", t.get("matriculados", t.get("total", ""))),
                    t.get("semestre", t.get("ano_semestre", "")),
                ))
        except Exception as e:
            messagebox.showerror("Lotacao", _db.erro_amigavel(e))

    # -- desempenho (coord) ------------------------------------------------
    def _montar_desempenho(self):
        ttk.Button(self.aba_des, text="Atualizar (vw_desempenho_turma)",
                   command=self.consultar_des).pack(anchor="w")
        self.tree_des = _tabela(self.aba_des,
                                [("a", "Turma/Disciplina", 260), ("b", "Media turma", 110),
                                 ("c", "Aprovados", 100), ("d", "Reprovados", 100)])
        self.consultar_des()

    def consultar_des(self):
        T.tree_clear(self.tree_des)
        try:
            for r in _db.select_view("vw_desempenho_turma"):
                vals = list(r.values())
                rotulo = str(r.get("disciplina", r.get("turma", r.get("id_turma", vals[0] if vals else ""))))
                T.tree_insert(self.tree_des, (
                    rotulo,
                    r.get("media_turma", r.get("media", r.get("media_geral", ""))),
                    r.get("aprovados", r.get("total_aprovados", "")),
                    r.get("reprovados", r.get("total_reprovados", "")),
                ))
        except Exception as e:
            messagebox.showerror("Desempenho", _db.erro_amigavel(e))

    # -- faturamento (coord, derivado) -------------------------------------
    def _montar_faturamento(self):
        ttk.Label(self.aba_fin, text="Faturamento / desempenho financeiro por curso (Coordenador)",
                  style="CardTitle.TLabel").pack(anchor="w", pady=(0, 4))
        ttk.Label(self.aba_fin, text="Derivado de vw_desempenho_turma (contagem de matriculas por curso).",
                  style="CardSub.TLabel").pack(anchor="w", pady=(0, 8))
        ttk.Button(self.aba_fin, text="Atualizar",
                   command=self.consultar_fin).pack(anchor="w")
        self.tree_fin = _tabela(self.aba_fin,
                                [("a", "Curso", 260), ("b", "Matriculas", 110), ("c", "Info", 220)])

    def consultar_fin(self):
        T.tree_clear(self.tree_fin)
        try:
            rows = _db.select_view("vw_desempenho_turma")
            agg: dict = {}
            for r in rows:
                curso = str(r.get("curso", r.get("nome_curso", r.get("id_curso", "—"))))
                qtd = r.get("matriculas", r.get("total", r.get("ocupadas", 1)))
                try:
                    qtd = int(qtd)
                except Exception:
                    qtd = 1
                agg[curso] = agg.get(curso, 0) + qtd
            for curso, total in sorted(agg.items()):
                T.tree_insert(self.tree_fin, (curso, total, "ver vw_desempenho_turma"))
            if not agg:
                messagebox.showinfo("Faturamento", "Sem dados em vw_desempenho_turma.")
        except Exception as e:
            messagebox.showerror("Faturamento", _db.erro_amigavel(e))

    # -- fechar semestre (coord) -------------------------------------------
    def _montar_fechar(self):
        ttk.Label(self.aba_fech, text="Encerrar semestre letivo (Coordenador)",
                  style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(self.aba_fech, text="Executa CALL sp_fechar_semestre. Operacao sensivel: confirme.",
                  style="CardSub.TLabel").pack(anchor="w", pady=4)
        ttk.Button(self.aba_fech, text="Fechar semestre agora", style="Danger.TButton",
                   command=self.fechar).pack(anchor="w", pady=8)

    def fechar(self):
        if not messagebox.askyesno("Fechar semestre", "Confirmar encerramento do semestre?"):
            return
        try:
            sets = _db.call_procedure("sp_fechar_semestre", ())
            messagebox.showinfo("Fechar semestre", "Semestre fechado com sucesso.")
            _ = sets
        except Exception as e:
            messagebox.showerror("Fechar semestre", _db.erro_amigavel(e))

    # -- auditoria (coord) --------------------------------------------------
    def _montar_log(self):
        ttk.Button(self.aba_log, text="Atualizar (sp_listar_log)",
                   command=self.consultar_log).pack(anchor="w")
        self.tree_log = _tabela(self.aba_log,
                                [("a", "Data", 150), ("b", "Matricula", 90),
                                 ("c", "Campo", 120), ("d", "Antigo → Novo", 260)])
        self.consultar_log()

    def consultar_log(self):
        T.tree_clear(self.tree_log)
        try:
            try:
                sets = _db.call_procedure("sp_listar_log", ())
                rows = sets[0] if sets else []
            except Exception:
                rows = _db.select_view("vw_log_nota")
            for r in rows:
                T.tree_insert(self.tree_log, (
                    r.get("data", r.get("data_hora", r.get("criado_em", ""))),
                    r.get("id_matricula", r.get("matricula", "")),
                    r.get("campo_alterado", r.get("campo", "")),
                    f"{r.get('valor_antigo', r.get('de', ''))} -> {r.get('valor_novo', r.get('para', ''))}",
                ))
        except Exception as e:
            messagebox.showerror("Auditoria", _db.erro_amigavel(e))
