"""Regras de perfil (usadas pela GUI e cobertas por teste sem banco).

Perfis do edital: 'Coordenador' e 'Secretario'.
- Secretario: Alunos, Matriculas, relatorios basicos (boletim, lotacao).
- Coordenador: tudo do Secretario + lancar notas/exame, fechar semestre,
  faturamento/desempenho financeiro, log de auditoria.
"""
COORDENADOR = "Coordenador"
SECRETARIO = "Secretario"


def normalizar(perfil: str) -> str:
    return (perfil or "").strip()


def eh_coordenador(perfil: str) -> bool:
    return normalizar(perfil) == COORDENADOR


def pode_ver_alunos(perfil: str) -> bool:
    return normalizar(perfil) in (COORDENADOR, SECRETARIO)


def pode_matricular(perfil: str) -> bool:
    return normalizar(perfil) in (COORDENADOR, SECRETARIO)


def pode_lancar_notas(perfil: str) -> bool:
    return eh_coordenador(perfil)


def pode_ver_boletim(perfil: str) -> bool:
    return normalizar(perfil) in (COORDENADOR, SECRETARIO)


def pode_ver_lotacao(perfil: str) -> bool:
    return normalizar(perfil) in (COORDENADOR, SECRETARIO)


def pode_ver_financeiro(perfil: str) -> bool:
    """Faturamento/desempenho financeiro por curso: so Coordenador."""
    return eh_coordenador(perfil)


def pode_ver_desempenho(perfil: str) -> bool:
    return eh_coordenador(perfil)


def pode_fechar_semestre(perfil: str) -> bool:
    return eh_coordenador(perfil)


def pode_ver_log(perfil: str) -> bool:
    return eh_coordenador(perfil)
