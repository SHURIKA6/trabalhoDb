"""Teste de permissoes por perfil (sem banco — logico puro).

Execucao:  python -m app.test_permissoes   ou   python app/test_permissoes.py
Exigencia do edital: botoes de faturamento/desempenho financeiro,
fechar semestre e auditoria VISIVEIS APENAS para Coordenador.
"""
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")

try:
    from app import permissoes as P
except ImportError:
    import permissoes as P  # type: ignore


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"[{'OK' if ok else 'FALHA'}] {nome}: obtido={obtido} esperado={esperado}")
    return ok


def main():
    ok = True
    # Secretario: basico liberado, sensivel bloqueado.
    ok &= check("secretario.alunos", P.pode_ver_alunos("Secretario"), True)
    ok &= check("secretario.matricular", P.pode_matricular("Secretario"), True)
    ok &= check("secretario.boletim", P.pode_ver_boletim("Secretario"), True)
    ok &= check("secretario.lotacao", P.pode_ver_lotacao("Secretario"), True)
    ok &= check("secretario.notas", P.pode_lancar_notas("Secretario"), False)
    ok &= check("secretario.financeiro", P.pode_ver_financeiro("Secretario"), False)
    ok &= check("secretario.desempenho", P.pode_ver_desempenho("Secretario"), False)
    ok &= check("secretario.fechar", P.pode_fechar_semestre("Secretario"), False)
    ok &= check("secretario.log", P.pode_ver_log("Secretario"), False)
    # Coordenador: tudo liberado.
    for nome, fn in [("alunos", P.pode_ver_alunos), ("matricular", P.pode_matricular),
                     ("boletim", P.pode_ver_boletim), ("lotacao", P.pode_ver_lotacao),
                     ("notas", P.pode_lancar_notas), ("financeiro", P.pode_ver_financeiro),
                     ("desempenho", P.pode_ver_desempenho), ("fechar", P.pode_fechar_semestre),
                     ("log", P.pode_ver_log)]:
        ok &= check(f"coordenador.{nome}", fn("Coordenador"), True)
    # Perfil desconhecido: nada sensivel.
    ok &= check("desconhecido.financeiro", P.pode_ver_financeiro("Aluno"), False)
    ok &= check("desconhecido.log", P.pode_ver_log(""), False)
    print("RESULTADO:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
