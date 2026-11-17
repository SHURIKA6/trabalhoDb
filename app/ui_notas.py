"""Lançamento de notas e exame pelo coordenador."""
from decimal import Decimal, InvalidOperation
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
        ttk.Label(busca, text="(vw_boletim)",
                  style="Sub.TLabel").pack(side="left", padx=(10, 0))

        moldura = T.moldura(self)
        moldura.pack(fill="x", pady=(0, 10))
        self.tree = ttk.Treeview(moldura, columns=("mat", "disc", "n1", "n2", "ex", "faltas", "media", "sit"),
                                 show="headings", height=10)
        for c, t, w in (("mat", "Matric.", 60), ("disc", "Disciplina", 190),
                        ("n1", "N1", 60), ("n2", "N2", 60), ("ex", "Exame", 60),
                        ("faltas", "Faltas", 55), ("media", "Media", 65), ("sit", "Situacao", 130)):
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
        ttk.Label(form, text="Faltas:", style="Card.TLabel").grid(row=0, column=6, sticky="e", padx=4)
        self.ent_faltas = ttk.Entry(form, width=8, font=T.FONTS["body"])
        self.ent_faltas.grid(row=0, column=7, sticky="w")
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
        referencia = self.ent_ra.get().strip()
        if not referencia:
            messagebox.showwarning("Notas", "Informe o RA/ID do aluno.")
            return
        T.tree_clear(self.tree)
        try:
            id_aluno = _db.buscar_id_aluno(referencia)
            if id_aluno is None:
                messagebox.showinfo("Notas", "Aluno não encontrado.")
                return
            rows = _db.select_view("vw_boletim", filters={"id_aluno": id_aluno})
            for r in rows:
                T.tree_insert(self.tree, (
                    _txt(r.get("id_matricula", r.get("matricula", ""))),
                    _txt(r.get("disciplina", r.get("nome_disciplina", ""))),
                    _txt(r.get("n1", r.get("nota1", ""))),
                    _txt(r.get("n2", r.get("nota2", ""))),
                    _txt(r.get("exame", r.get("nota_exame", ""))),
                    _txt(r.get("faltas", 0)),
                    _txt(r.get("media", r.get("media_final", ""))),
                    _txt(r.get("situacao", r.get("status", ""))),
                ), status_idx=7)
            if not rows:
                messagebox.showinfo("Notas", "Este aluno ainda não tem matrículas no boletim.")
        except Exception as e:
            messagebox.showerror("Notas", _db.erro_amigavel(e))

    def _ao_selecionar(self):
        sel = self.tree.selection()
        if not sel:
            return
        matricula, _, n1, n2, exame, faltas, _, _ = self.tree.item(sel[0], "values")
        for campo, valor in ((self.ent_mat, matricula), (self.ent_n1, n1), (self.ent_n2, n2),
                             (self.ent_ex, exame), (self.ent_faltas, faltas)):
            campo.delete(0, "end")
            campo.insert(0, valor)

    def _situacao_da_linha(self):
        sel = self.tree.selection()
        if not sel:
            return ""
        return self.tree.set(sel[0], "sit")

    # -- escrita: somente CALL -------------------------------------------
    def lancar_notas(self):
        try:
            id_mat = int(self.ent_mat.get().strip())
            n1 = Decimal(self.ent_n1.get().strip().replace(",", "."))
            n2 = Decimal(self.ent_n2.get().strip().replace(",", "."))
            faltas = int(self.ent_faltas.get().strip())
            if not (0 <= n1 <= 10 and 0 <= n2 <= 10 and faltas >= 0):
                raise ValueError
        except (ValueError, InvalidOperation):
            messagebox.showwarning("Notas", "Informe o ID da matrícula, notas de 0 a 10 e faltas em número inteiro a partir de zero.")
            return
        try:
            _db.call_procedure("sp_lancar_notas", (id_mat, n1, n2, faltas, self.sessao["id_usuario"]))
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
            exame = Decimal(self.ent_ex.get().strip().replace(",", "."))
            if not 0 <= exame <= 10:
                raise ValueError
        except (ValueError, InvalidOperation):
            messagebox.showwarning("Exame", "Informe o ID da matrícula e uma nota de exame de 0 a 10.")
            return
        try:
            _db.call_procedure("sp_lancar_exame", (id_mat, exame, self.sessao["id_usuario"]))
            messagebox.showinfo("Exame", "Nota de exame lancada.")
            self.buscar()
        except Exception as e:
            messagebox.showerror("Exame", _db.erro_amigavel(e))
