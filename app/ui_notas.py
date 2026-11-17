"""Lancamento de notas — SOMENTE Coordenador.

- Consulta: SELECT vw_boletim (filtro por RA) e CALL sp_historico_aluno.
- Escrita: CALL sp_lancar_notas e CALL sp_lancar_exame
  (exame permitido apenas quando situacao = 'Em exame').
A GUI bloqueia o botao de exame fora dessa condicao; a procedure tambem
recusa via SIGNAL 45000, tratado com mensagem amigavel.
"""
import tkinter as tk
from tkinter import messagebox, ttk

try:
    from app import db as _db
    from app import ui_theme as T
except ImportError:
    import db as _db  # type: ignore
    import ui_theme as T  # type: ignore


def _txt(valor):
    """None e Decimal ficam legiveis na tabela: NULL -> vazio."""
    return "" if valor is None else valor


class NotasFrame(ttk.Frame):
    def __init__(self, parent, sessao: dict):
        super().__init__(parent)
        self.sessao = sessao
        if sessao.get("perfil") != "Coordenador":
            ttk.Label(self, text="Acesso restrito ao Coordenador.").pack(pady=20)
            return

        T.screen_header(self, "Lancar notas")

        busca = ttk.Frame(self)
        busca.pack(fill="x", pady=(0, 10))
        ttk.Label(busca, text="RA / ID aluno:", style="Muted.TLabel").pack(side="left")
        self.ent_ra = ttk.Entry(busca, width=18, font=T.FONTS["body"])
        self.ent_ra.pack(side="left", padx=(6, 8))
        ttk.Button(busca, text="Buscar boletim", style="Primary.TButton",
                   command=self.buscar).pack(side="left")
        ttk.Label(busca, text="(vw_boletim + sp_historico_aluno)",
                  style="Sub.TLabel").pack(side="left", padx=(10, 0))

        moldura = T.moldura(self)
        moldura.pack(fill="x", pady=(0, 10))
        self.tree = ttk.Treeview(moldura, columns=("mat", "disc", "n1", "n2", "ex", "media", "sit"),
                                 show="headings", height=10)
        for c, t, w in (("mat", "Matric.", 70), ("disc", "Disciplina", 220),
                        ("n1", "N1", 60), ("n2", "N2", 60), ("ex", "Exame", 60),
                        ("media", "Media", 70), ("sit", "Situacao", 130)):
            self.tree.heading(c, text=t, anchor="w")
            self.tree.column(c, width=w)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(moldura, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="left", fill="y")
        T.tag_setup(self.tree)
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._ao_selecionar())

        form = ttk.LabelFrame(self, text="Lancamento (selecione uma linha acima)", padding=12)
        form.pack(fill="x", pady=(0, 4))
        ttk.Label(form, text="ID matricula:", style="Card.TLabel").grid(
            row=0, column=0, sticky="e", padx=4, pady=2)
        self.ent_mat = ttk.Entry(form, width=12, font=T.FONTS["body"])
        self.ent_mat.grid(row=0, column=1, pady=2, sticky="w")
        ttk.Label(form, text="N1:", style="Card.TLabel").grid(row=0, column=2, sticky="e", padx=4)
        self.ent_n1 = ttk.Entry(form, width=8, font=T.FONTS["body"])
        self.ent_n1.grid(row=0, column=3, sticky="w")
        ttk.Label(form, text="N2:", style="Card.TLabel").grid(row=0, column=4, sticky="e", padx=4)
        self.ent_n2 = ttk.Entry(form, width=8, font=T.FONTS["body"])
        self.ent_n2.grid(row=0, column=5, sticky="w")
        ttk.Label(form, text="Exame:", style="Card.TLabel").grid(row=1, column=2, sticky="e", padx=4)
        self.ent_ex = ttk.Entry(form, width=8, font=T.FONTS["body"])
        self.ent_ex.grid(row=1, column=3, sticky="w", pady=2)
        self.btn_notas = ttk.Button(form, text="Lancar N1/N2", style="Primary.TButton",
                                    command=self.lancar_notas)
        self.btn_notas.grid(row=1, column=0, columnspan=2, pady=6)
        self.btn_exame = ttk.Button(form, text="Lancar exame (so 'Em exame')",
                                    command=self.lancar_exame)
        self.btn_exame.grid(row=1, column=4, columnspan=2, pady=6)

    # -- leitura ---------------------------------------------------------
    def buscar(self):
        ra = self.ent_ra.get().strip()
        if not ra:
            messagebox.showwarning("Notas", "Informe o RA/ID do aluno.")
            return
        T.tree_clear(self.tree)
        try:
            # Tenta filtro por colunas mais provaveis de RA na view.
            rows = []
            for col in ("ra", "id_aluno", "RA"):
                try:
                    rows = _db.select_view("vw_boletim", filters={col: ra})
                    if rows:
                        break
                except Exception:
                    continue
            if not rows:
                # Sem filtro exato: traz amostra e filtra em memoria.
                todas = _db.select_view("vw_boletim", limit=500)
                rows = [r for r in todas
                        if str(r.get("ra", r.get("id_aluno", r.get("RA", "")))) == ra]
            for r in rows:
                T.tree_insert(self.tree, (
                    _txt(r.get("id_matricula", r.get("matricula", ""))),
                    _txt(r.get("disciplina", r.get("nome_disciplina", ""))),
                    _txt(r.get("n1", r.get("nota1", ""))),
                    _txt(r.get("n2", r.get("nota2", ""))),
                    _txt(r.get("exame", r.get("nota_exame", ""))),
                    _txt(r.get("media", r.get("media_final", ""))),
                    _txt(r.get("situacao", r.get("status", ""))),
                ), status_idx=6)
            if not rows:
                messagebox.showinfo("Notas", "Nenhum registro no boletim para este RA.")
        except Exception as e:
            messagebox.showerror("Notas", _db.erro_amigavel(e))

    def _ao_selecionar(self):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        self.ent_mat.delete(0, "end")
        self.ent_mat.insert(0, str(vals[0]))
        self.ent_n1.delete(0, "end")
        self.ent_n1.insert(0, str(vals[2] or ""))
        self.ent_n2.delete(0, "end")
        self.ent_n2.insert(0, str(vals[3] or ""))
        self.ent_ex.delete(0, "end")
        self.ent_ex.insert(0, str(vals[4] or ""))

    def _situacao_da_linha(self):
        sel = self.tree.selection()
        if not sel:
            return ""
        return str(self.tree.item(sel[0], "values")[6] or "")

    # -- escrita: somente CALL -------------------------------------------
    def lancar_notas(self):
        try:
            id_mat = int(self.ent_mat.get().strip())
            n1 = float(self.ent_n1.get().strip().replace(",", "."))
            n2 = float(self.ent_n2.get().strip().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Notas", "Informe matricula (int) e N1/N2 numericas.")
            return
        try:
            _db.call_procedure("sp_lancar_notas", (id_mat, n1, n2))
            messagebox.showinfo("Notas", "Notas lancadas.")
            self.buscar()
        except Exception as e:
            messagebox.showerror("Notas", _db.erro_amigavel(e))

    def lancar_exame(self):
        sit = self._situacao_da_linha()
        if sit and sit.strip().lower() not in ("em exame", "em_exame", "exame"):
            messagebox.showwarning(
                "Exame",
                f"Lancamento de exame permitido apenas quando a situacao e 'Em exame' (atual: {sit!r}).")
            return
        try:
            id_mat = int(self.ent_mat.get().strip())
            ex = float(self.ent_ex.get().strip().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Exame", "Informe matricula (int) e nota de exame numerica.")
            return
        try:
            _db.call_procedure("sp_lancar_exame", (id_mat, ex))
            messagebox.showinfo("Exame", "Nota de exame lancada.")
            self.buscar()
        except Exception as e:
            messagebox.showerror("Exame", _db.erro_amigavel(e))
