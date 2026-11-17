"""Sistema visual do SGA — tema central (somente apresentacao).

Paleta "registro academico": tinta naval + papel frio + ouro.
Define fontes, estilos ttk e helpers usados por todas as telas.
Nenhuma regra de negocio aqui: este modulo nao acessa o banco.
"""
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

# -- paleta -----------------------------------------------------------------
INK       = "#1C2B3A"   # barra lateral e acoes primarias
INK_DEEP  = "#14202C"   # pressionado
INK_SOFT  = "#26394E"   # hover sobre tinta
INK_LINE  = "#2E4054"   # hairline sobre tinta
STEEL     = "#B9C4D0"   # texto claro sobre tinta
STEEL_DIM = "#7C8CA0"   # legenda sobre tinta
PAPER     = "#EEF1F4"   # fundo da area de trabalho
CARD      = "#FFFFFF"   # paineis, tabelas, cartoes
LINE      = "#D9DFE6"   # hairlines e bordas
HEAD_BG   = "#E9EDF2"   # cabecalho de tabela
HEAD_HOV  = "#DFE5EB"
TEXT      = "#1F2937"   # texto principal
MUTED     = "#5B6B7C"   # texto secundario
GOLD      = "#C99700"   # acento: CTA de login e item ativo
GOLD_HOV  = "#D9AC1F"
GOLD_PRE  = "#A87F00"
GOLD_SOFT = "#E3B341"   # acento sobre tinta
SEL_BG    = "#2E4B66"   # selecao de linha
SEL_FG    = "#FFFFFF"
STRIPE    = "#F7F9FB"   # linha zebrada

# cores de situacao (cor do texto da linha: informacao, nao decoracao)
ST_OK   = "#1E7A46"     # aprovado
ST_BAD  = "#B3372B"     # reprovado / turma cheia
ST_WARN = "#A66A00"     # em exame
ST_INFO = "#1D5FA0"     # cursando / matriculado
ST_OFF  = "#6B7684"     # trancado / inativo

# -- fontes -----------------------------------------------------------------
_UI_CAND   = ("Ubuntu", "Cantarell", "Noto Sans", "DejaVu Sans", "Segoe UI", "Helvetica")
_DISP_CAND = ("Georgia", "DejaVu Serif", "Liberation Serif", "Charter", "Times New Roman")

FONTS = {}


def _pick(root, cands, fallback):
    fams = set(tkfont.families(root))
    for name in cands:
        if name in fams:
            return name
    return fallback


def setup_fonts(root):
    ui = _pick(root, _UI_CAND, "Helvetica")
    disp = _pick(root, _DISP_CAND, "Times")
    FONTS.clear()
    FONTS["body"]    = tkfont.Font(family=ui,   size=10)
    FONTS["small"]   = tkfont.Font(family=ui,   size=8)
    FONTS["heading"] = tkfont.Font(family=ui,   size=9,  weight="bold")
    FONTS["section"] = tkfont.Font(family=ui,   size=10, weight="bold")
    FONTS["btn"]     = tkfont.Font(family=ui,   size=10, weight="bold")
    FONTS["title"]   = tkfont.Font(family=disp, size=15, weight="bold")
    FONTS["brand"]   = tkfont.Font(family=disp, size=12, weight="bold")
    FONTS["mark"]    = tkfont.Font(family=disp, size=22)


# -- helpers ----------------------------------------------------------------
def divisor(pai, cor=LINE):
    f = tk.Frame(pai, bg=cor, height=1)
    f.pack_propagate(False)
    return f


def screen_header(pai, titulo):
    """Titulo de tela (serifada) + hairline separando cabecalho e conteudo."""
    topo = ttk.Frame(pai)
    topo.pack(fill="x", pady=(0, 10))
    ttk.Label(topo, text=titulo, style="Title.TLabel").pack(anchor="w")
    divisor(topo).pack(fill="x", pady=(10, 0))


def moldura(pai):
    """Container branco com borda fina, para tabelas e formularios."""
    return tk.Frame(pai, bg=CARD, highlightthickness=1,
                    highlightbackground=LINE, highlightcolor=LINE)


def situacao_tag(valor):
    """Mapeia texto de situacao para a cor de linha correspondente.

    Somente estados excepcionais ganham cor (reprovado, em exame,
    trancado); estados normais ficam no texto padrao para nao poluir.
    """
    s = str(valor or "").strip().lower()
    if not s:
        return None
    if "reprov" in s:
        return "bad"
    if "exame" in s:
        return "warn"
    if "tranc" in s or "cancel" in s or "inativ" in s or "desist" in s:
        return "off"
    return None


def tag_setup(tree):
    tree.tag_configure("stripe", background=STRIPE)
    tree.tag_configure("ok", foreground=ST_OK)
    tree.tag_configure("bad", foreground=ST_BAD)
    tree.tag_configure("warn", foreground=ST_WARN)
    tree.tag_configure("info", foreground=ST_INFO)
    tree.tag_configure("off", foreground=ST_OFF)
    tree.tag_configure("cheio", foreground=ST_BAD)


def tree_clear(tree):
    for i in tree.get_children():
        tree.delete(i)
    tree._stripe_n = 0


def tree_insert(tree, values, status_idx=None, extra_tags=()):
    """Insere linha com zebra e cor de situacao (tags posteriores vencem)."""
    n = getattr(tree, "_stripe_n", 0)
    tags = []
    if n % 2 == 1:
        tags.append("stripe")
    if status_idx is not None and status_idx < len(values):
        t = situacao_tag(values[status_idx])
        if t:
            tags.append(t)
    tags.extend(extra_tags)
    tree._stripe_n = n + 1
    if tags:
        tree.insert("", "end", values=values, tags=tags)
    else:
        tree.insert("", "end", values=values)


# -- aplicacao do tema -------------------------------------------------------
def apply_theme(root):
    setup_fonts(root)
    root.configure(bg=PAPER)
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    b = FONTS["body"]

    # frames
    style.configure("TFrame", background=PAPER)
    style.configure("Card.TFrame", background=CARD)
    style.configure("Ink.TFrame", background=INK)

    # rotulos
    style.configure("TLabel", background=PAPER, foreground=TEXT, font=b)
    style.configure("Muted.TLabel", background=PAPER, foreground=MUTED, font=b)
    style.configure("Sub.TLabel", background=PAPER, foreground=MUTED, font=FONTS["small"])
    style.configure("Title.TLabel", background=PAPER, foreground=INK, font=FONTS["title"])
    style.configure("Card.TLabel", background=CARD, foreground=TEXT, font=b)
    style.configure("CardSub.TLabel", background=CARD, foreground=MUTED, font=FONTS["small"])
    style.configure("CardTitle.TLabel", background=CARD, foreground=INK, font=FONTS["section"])
    style.configure("Ink.TLabel", background=INK, foreground=STEEL, font=b)
    style.configure("InkTitle.TLabel", background=INK, foreground="#FFFFFF", font=FONTS["section"])
    style.configure("InkBrand.TLabel", background=INK, foreground=STEEL_DIM, font=FONTS["small"])
    style.configure("InkUser.TLabel", background=INK, foreground="#FFFFFF", font=b)
    style.configure("InkPerfil.TLabel", background=INK, foreground=GOLD_SOFT, font=FONTS["small"])
    style.configure("InkSub.TLabel", background=INK, foreground=STEEL_DIM, font=FONTS["small"])
    style.configure("InkMark.TLabel", background=INK, foreground=GOLD_SOFT, font=FONTS["mark"])

    # botoes: base = contorno claro; Primary = tinta; Danger = destrutivo;
    # Gold = acao unica de login; Nav = itens da barra lateral
    style.configure("TButton", background=CARD, foreground=INK, font=b,
                    borderwidth=1, padding=(12, 6),
                    bordercolor="#C3CCD6", lightcolor="#C3CCD6", darkcolor="#C3CCD6")
    style.map("TButton",
              background=[("disabled", "#EDF0F3"), ("pressed", "#E2E7EC"), ("active", "#F0F3F6")],
              foreground=[("disabled", "#9AA6B2")],
              bordercolor=[("disabled", "#DDE2E7")],
              lightcolor=[("disabled", "#DDE2E7")],
              darkcolor=[("disabled", "#DDE2E7")])

    style.configure("Primary.TButton", background=INK, foreground="#FFFFFF",
                    font=FONTS["btn"], borderwidth=1, padding=(12, 6),
                    bordercolor=INK, lightcolor=INK, darkcolor=INK)
    style.map("Primary.TButton",
              background=[("disabled", "#9DAAB7"), ("pressed", INK_DEEP), ("active", "#2A3E52")],
              bordercolor=[("disabled", "#9DAAB7")],
              lightcolor=[("disabled", "#9DAAB7")],
              darkcolor=[("disabled", "#9DAAB7")])

    style.configure("Danger.TButton", background=CARD, foreground=ST_BAD, font=b,
                    borderwidth=1, padding=(12, 6),
                    bordercolor="#D9B3AE", lightcolor="#D9B3AE", darkcolor="#D9B3AE")
    style.map("Danger.TButton",
              background=[("disabled", "#EDF0F3"), ("pressed", "#F3E2DF"), ("active", "#FAEFEE")],
              foreground=[("disabled", "#C9A6A1")],
              bordercolor=[("disabled", "#E8DCDB")],
              lightcolor=[("disabled", "#E8DCDB")],
              darkcolor=[("disabled", "#E8DCDB")])

    style.configure("Gold.TButton", background=GOLD, foreground=INK_DEEP,
                    font=FONTS["btn"], borderwidth=0, padding=(14, 8))
    style.map("Gold.TButton",
              background=[("disabled", "#DCC68A"), ("pressed", GOLD_PRE), ("active", GOLD_HOV)],
              foreground=[("disabled", "#6E5A2A")])

    style.configure("Nav.TButton", background=INK, foreground=STEEL, font=b,
                    borderwidth=0, relief="flat", padding=(16, 8), anchor="w")
    style.map("Nav.TButton",
              background=[("active", INK_SOFT), ("pressed", INK_SOFT)],
              foreground=[("active", "#FFFFFF")])

    style.configure("NavActive.TButton", background=INK_SOFT, foreground=GOLD_SOFT,
                    font=FONTS["section"], borderwidth=0, relief="flat",
                    padding=(16, 8), anchor="w")
    style.map("NavActive.TButton",
              background=[("active", "#2E4560"), ("pressed", "#2E4560")],
              foreground=[("active", GOLD_SOFT)])

    style.configure("InkGhost.TButton", background=INK, foreground=STEEL, font=b,
                    borderwidth=1, padding=(10, 5),
                    bordercolor=INK_LINE, lightcolor=INK_LINE, darkcolor=INK_LINE)
    style.map("InkGhost.TButton",
              background=[("active", INK_SOFT), ("pressed", INK_DEEP)],
              foreground=[("active", "#FFFFFF")])

    # campos
    style.configure("TEntry", fieldbackground=CARD, foreground=TEXT, insertcolor=TEXT,
                    borderwidth=1, padding=(8, 5), font=b,
                    bordercolor=LINE, lightcolor=LINE, darkcolor=LINE)
    style.map("TEntry",
              bordercolor=[("focus", SEL_BG)],
              lightcolor=[("focus", SEL_BG)],
              darkcolor=[("focus", SEL_BG)],
              fieldbackground=[("disabled", "#F2F4F7")])

    style.configure("TCombobox", fieldbackground=CARD, background=CARD, foreground=TEXT,
                    borderwidth=1, padding=(8, 5), arrowsize=13, arrowcolor=INK,
                    bordercolor=LINE, lightcolor=LINE, darkcolor=LINE, font=b)
    style.map("TCombobox",
              bordercolor=[("focus", SEL_BG)],
              lightcolor=[("focus", SEL_BG)],
              darkcolor=[("focus", SEL_BG)],
              fieldbackground=[("readonly", CARD), ("disabled", "#F2F4F7")],
              foreground=[("disabled", "#9AA6B2")])
    root.option_add("*TCombobox*Listbox.background", CARD)
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", SEL_BG)
    root.option_add("*TCombobox*Listbox.selectForeground", SEL_FG)
    root.option_add("*TCombobox*Listbox.font", FONTS["body"])

    # tabelas
    style.configure("Treeview", background=CARD, fieldbackground=CARD, foreground=TEXT,
                    rowheight=27, borderwidth=0, relief="flat", font=b)
    style.configure("Treeview.Heading", background=HEAD_BG, foreground=INK,
                    font=FONTS["heading"], relief="flat", borderwidth=0, padding=(8, 6))
    style.map("Treeview.Heading", background=[("active", HEAD_HOV)])
    style.map("Treeview",
              background=[("selected", SEL_BG)],
              foreground=[("selected", SEL_FG)])

    style.configure("Vertical.TScrollbar", background="#C7D0DA", troughcolor=CARD,
                    bordercolor=CARD, arrowcolor=MUTED, gripcount=0, arrowsize=12)
    style.map("Vertical.TScrollbar", background=[("active", "#AEB9C4")])

    # abas de relatorio
    style.configure("TNotebook", background=PAPER, borderwidth=0, tabmargins=(0, 6, 0, 0))
    style.configure("TNotebook.Tab", background=PAPER, foreground=MUTED, font=b,
                    borderwidth=0, padding=(14, 7))
    style.map("TNotebook.Tab",
              background=[("selected", CARD)],
              foreground=[("selected", INK), ("active", INK)])

    # formularios em caixa
    style.configure("TLabelframe", background=CARD, borderwidth=1, relief="solid",
                    bordercolor=LINE, lightcolor=LINE, darkcolor=LINE)
    style.configure("TLabelframe.Label", background=CARD, foreground=INK,
                    font=FONTS["section"])
