"""Autenticacao: hash SHA-256 no app + validacao via sp_LoginUsuario."""
import hashlib

try:
    from app import db as _db
except ImportError:
    import db as _db  # type: ignore


def hash_senha(senha: str) -> str:
    """SHA-256 hex da senha em claro (compativel com CHAR(64) do banco)."""
    return hashlib.sha256((senha or "").encode("utf-8")).hexdigest()


def autenticar(login: str, senha: str):
    """Valida via CALL sp_LoginUsuario(p_login, p_senha_hash).

    Retorna dict {id_usuario, nome, perfil} ou None se credencial invalida.
    Levanta ValueError se login/senha vazios.
    """
    login = (login or "").strip()
    senha = (senha or "")
    if not login:
        raise ValueError("Informe o login.")
    if not senha:
        raise ValueError("Informe a senha.")
    digest = hash_senha(senha)
    sets = _db.call_procedure("sp_LoginUsuario", (login, digest))
    rows = sets[0] if sets else []
    if not rows:
        return None
    r = rows[0]
    # Normaliza chaves (o banco pode usar id_usuario/id, nome, perfil).
    return {
        "id_usuario": r.get("id_usuario", r.get("id")),
        "nome": r.get("nome", login),
        "perfil": r.get("perfil", ""),
        "login": login,
    }
