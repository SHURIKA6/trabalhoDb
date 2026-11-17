"""Camada de acesso ao banco — CONFORMIDADE COM O EDITAL.

REGRAS (nao quebrar):
1. PROIBIDO PHP e PROIBIDO SQL cru pela rede.
2. TODA comunicacao com MySQL deve ser:
   - CALL sp_*  (via `call_procedure`), ou
   - SELECT * FROM vw_* (via `select_view`).
3. E PROIBIDO SELECT/INSERT/UPDATE/DELETE diretos em tabelas
   (usuario, curso, disciplina, professor, aluno, turma, matricula,
   log_nota, pre_requisito). Nao existe funcao de query livre neste
   modulo de proposito — nao adicione uma.

Se precisar de operacao nova, crie uma Stored Procedure em
`sql/05_sp_apoio.sql` e chame via `call_procedure`.
"""
import re

import mysql.connector
from mysql.connector import Error as MySQLError

try:
    from app import config as _config
except ImportError:
    import config as _config  # type: ignore

_PROC_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_VIEW_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_COL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validar_procedure(nome: str) -> str:
    nome = (nome or "").strip()
    if not nome.startswith("sp_") or not _PROC_RE.match(nome):
        raise ValueError(
            f"Procedure bloqueada: '{nome}'. "
            "Permitido apenas CALL sp_<nome> com identificador valido."
        )
    return nome


def _validar_view(nome: str) -> str:
    nome = (nome or "").strip()
    if not nome.startswith("vw_") or not _VIEW_RE.match(nome):
        raise ValueError(
            f"View bloqueada: '{nome}'. "
            "Permitido apenas SELECT de vw_* (ex.: vw_boletim)."
        )
    return nome


def _validar_coluna(nome: str) -> str:
    nome = (nome or "").strip()
    if not _COL_RE.match(nome):
        raise ValueError(f"Nome de coluna invalido: '{nome}'.")
    return nome


def get_connection():
    """Abre conexao MySQL a partir de app/config.py (.env)."""
    return mysql.connector.connect(
        host=_config.MYSQL_HOST,
        port=_config.MYSQL_PORT,
        user=_config.MYSQL_USER,
        password=_config.MYSQL_PASSWORD,
        database=_config.MYSQL_DB,
    )


def call_procedure(proc_name: str, params=()):
    """Executa `CALL sp_*(%s, ...)` e retorna lista de result-sets.

    Retorno: List[List[dict]] — cada result-set vira lista de dicionarios
    (cursor dictionary=True). Procedures sem SELECT retornam [[]] ou [].
    Faz commit em sucesso e rollback em erro.
    """
    proc = _validar_procedure(proc_name)
    args = list(params) if params else []
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        try:
            cur.callproc(proc, args)
        except MySQLError:
            conn.rollback()
            raise
        result_sets = []
        try:
            for rs in cur.stored_results():
                result_sets.append(rs.fetchall())
        except MySQLError:
            # Procedure sem result-set (somentee OUT/efeito colateral).
            result_sets = []
        try:
            conn.commit()
        except MySQLError:
            pass
        cur.close()
        return result_sets
    finally:
        try:
            conn.close()
        except Exception:
            pass


def select_view(view_name: str, filters=None, order_by=None, limit=None):
    """Executa `SELECT * FROM vw_* [WHERE col=%s ...]` parametrizado.

    - view_name: obrigatorio comecar com `vw_` (ex.: vw_boletim).
    - filters: dict {coluna: valor} com igualdade (AND). None = sem filtro.
      Para filtro LIKE, use chave "coluna__like".
    - order_by: str ou lista de colunas (validadas por regex).
    - limit: int positivo opcional.
    Retorna: List[dict].
    """
    view = _validar_view(view_name)
    sql = f"SELECT * FROM `{view}`"
    params: list = []
    if filters:
        if not isinstance(filters, dict):
            raise ValueError("filters deve ser dict {coluna: valor}.")
        conds = []
        for chave, valor in filters.items():
            if chave.endswith("__like"):
                col = _validar_coluna(chave[:-6])
                conds.append(f"`{col}` LIKE %s")
            else:
                col = _validar_coluna(chave)
                conds.append(f"`{col}` = %s")
            params.append(valor)
        if conds:
            sql += " WHERE " + " AND ".join(conds)
    if order_by:
        cols = [order_by] if isinstance(order_by, str) else list(order_by)
        cols = [_validar_coluna(c) for c in cols]
        sql += " ORDER BY " + ", ".join(f"`{c}`" for c in cols)
    if limit is not None:
        limit = int(limit)
        if limit <= 0:
            raise ValueError("limit deve ser positivo.")
        sql += f" LIMIT {limit}"
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        try:
            conn.close()
        except Exception:
            pass


def erro_amigavel(exc: Exception) -> str:
    """Traduz erro MySQL (incl. SIGNAL 1644 / SQLSTATE 45000) p/ mensagem UX."""
    if isinstance(exc, MySQLError):
        msg = str(exc)
        # Mensagens vindas de SIGNAL SQLSTATE '45000' das SPs do edital:
        # turma lotada, pre-requisito, aluno trancado, exame indevido etc.
        # O texto do SIGNAL ja e amigavel — repassa limpo.
        low = msg.lower()
        if "45000" in low or getattr(exc, "errno", None) in (1644,):
            # Remove prefixo tecnico "1644 (45000): " se houver.
            for pref in ("1644 (45000): ", "45000: "):
                if pref in msg:
                    msg = msg.split(pref, 1)[-1]
                    break
            return msg.strip() or "Operacao recusada pela regra academica."
        if getattr(exc, "errno", None) in (1045,):
            return "Acesso ao banco negado. Confira .env (usuario/senha)."
        if getattr(exc, "errno", None) in (2003, 2005, 2013):
            return "Nao foi possivel conectar ao MySQL. Verifique host/porta e se o banco sga_fbi existe."
        return f"Erro de banco: {msg}"
    return str(exc)


# NOTA: intencionalmente NAO existe funcao `query(sql)` / `execute(sql)`.
# Qualquer necessidade de SQL novo deve virar procedure em sql/05_sp_apoio.sql.
