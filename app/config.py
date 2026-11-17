"""Configuração de acesso ao MySQL via variáveis de ambiente (.env).

Nunca hardcode senha no código. Copie `.env.example` para `.env` e ajuste.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv é opcional em runtime; sem ele lê só do ambiente real.
    pass


def _get(name: str, default: str = "") -> str:
    return os.getenv(name, default)


MYSQL_HOST: str = _get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT: int = int(_get("MYSQL_PORT", "3306") or 3306)
MYSQL_USER: str = _get("MYSQL_USER", "sga_app")
MYSQL_PASSWORD: str = _get("MYSQL_PASSWORD", "")
MYSQL_DB: str = _get("MYSQL_DB", "sga_fbi")
