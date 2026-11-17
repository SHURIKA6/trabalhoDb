# Apresentação — SGA / Faculdade do Bug Infinito (roteiro slide-a-slide)

**Formato:** 8 slides, ~15 minutos + demo e perguntas.
**Deck executável:** `slides/apresentacao.html` (standalone, setas/click para navegar, `P` para imprimir).
**Integrantes:** Manuela Albuquerque Wentz, Danieli Cristina de Carvalho Breves, Fernando Riad da Silva Ribeiro, Nickson Henrique Cavéquia Silva — **Professor:** Francisco Sanches Banhos Filho — **Disciplina:** LBD — **Data:** 23/11/2026.

---

## Slide 1 — Título

**Título:** SGA — Sistema de Gestão Acadêmica da Faculdade do Bug Infinito
**Subtítulo:** Banco íntegro, seguro e auditável | MySQL 8 + Python (só SP/View)
**Equipe:** Manuela Albuquerque Wentz · Danieli Cristina de Carvalho Breves · Fernando Riad da Silva Ribeiro · Nickson Henrique Cavéquia Silva
**Rodapé:** LBD · Prof. Francisco Sanches Banhos Filho · 23/11/2026

> **Notas do orador:** Cumprimentar a banca, apresentar o grupo em 20 segundos e
> anunciar o roteiro: problema, modelagem, arquitetura, regras, segurança, testes,
> dificuldades e conclusão. Não entrar em detalhes ainda.

## Slide 2 — Problema e objetivos

- Controle acadêmico descentralizado: matrículas sem pré-requisito, turmas
  lotadas, médias divergentes, notas alteradas sem auditoria, senhas frágeis.
- Objetivo: centralizar no banco `sga_fbi`, com regras **dentro do SGBD**,
  aplicação Python consumindo apenas procedures e views.
- Roteiro: modelagem → arquitetura → regras → segurança → testes → dificuldades → conclusão.

> **Notas do orador:** Dar 1 exemplo concreto de cada dor. Avisar que a demo ao vivo
> (matrícula + notas + auditoria) ocorre no slide 5.

## Slide 3 — Modelagem (MER + relacional + 3FN)

- 9 entidades: `usuario`, `curso`, `disciplina`, `pre_requisito` (N:N
  auto-relacionamento), `professor`, `aluno`, `turma`, `matricula`, `log_nota`.
- Destaques: R3 (pré-requisito N:N), R6 (matrícula como associativa com
  atributos avaliativos + `UNIQUE`), R7/R8 (auditoria).
- Lógico: 9 relações, PKs simples, FKs, `UNIQUE`s, `ENUM`s, `CHECK`s.
- 1FN: sem listas em célula (`pre_requisito` é tabela, não coluna).
- 2FN: PKs simples (sem dependência parcial); `pre_requisito` sem atributos.
- 3FN: sem transitivas; `media_final`/`situacao` são derivados calculados pelo
  banco, não entrada manual.

> **Notas do orador:** Explicar por que matrícula é associativa e pré-requisito
> auto-relacionamento. Ciclos: `CHECK` anti-auto-referência + validação na procedure.
> media_final é fato derivado materializado, não viola 3FN.

## Slide 4 — Arquitetura: só SP/View

- `app/db.py`: `call_procedure` (só `sp_*`) + `select_view` (só `vw_*`);
  sem função de query livre; regex valida identificadores.
- Usuário `sga_app`: `EXECUTE` + `SELECT` em views; sem DML direto.
- Erros de regra via `SIGNAL 45000` → `erro_amigavel()` na tela.
- Frase-chave: a aplicação não consegue violar as regras mesmo que queira.

> **Notas do orador:** Mostrar `app/db.py` (30 segundos): apontar as regexes
> `_PROC_RE`/`_VIEW_RE` e a ausência de `query(sql)`.

## Slide 5 — RN + demo (matrícula, notas e auditoria)

- RN01 pré-requisito (`fn_VerificarPreRequisito`) · RN02 vaga (`FOR UPDATE`) · RN03 duplicidade
- RN04 média/situação · RN05 domínio 0–10, `NULL` = não lançada · RN06 auditoria · RN09 exame/trancamento/cancelamento
- **Demo:** matrícula sem pré-requisito → erro amigável; matrícula válida → `vagas_ocupadas` incrementa
- **Demo:** `sp_LancarNotas` → trigger calcula média/situação; linha nova em `log_nota`

> **Notas do orador:** Executar `CALL sp_MatricularAluno` com caso inválido
> primeiro (mostra o SIGNAL), depois o válido. Mostrar `vw_boletim` antes e depois
> do lançamento, e a linha de auditoria com antes/depois + autor. Backup: 06_matricula.png.

## Slide 6 — Segurança, perfis e testes

- Hash SHA-256 hex (`SHA2` no banco, `hashlib` no app); `CHAR(64)`;
  `sp_LoginUsuario` nunca retorna senha; `.env` fora do código.
- Matriz Secretário × Coordenador: Secretário (alunos, matrículas, boletim/histórico/lotação);
  Coordenador (tudo + notas/exame, desempenho, faturamento, fechar semestre, auditoria).
  Dupla barreira: tela oculta (`permissoes.py`) + banco (`sp_fechar_semestre` exige Coordenador).
- Testes: 9/9 conforme esperado (`sql/04_testes.sql`).

| Bloco | Testes | Cobertura |
|---|---|---|
| Autenticação | T01 | RN07 |
| Matrícula | T02–T05 | RN01, RN02, RN03 |
| Avaliação | T06–T07 | RN04, RN05 |
| Auditoria/acesso | T08–T09 | RN06, RN08 |

> **Notas do orador:** Destacar T04 (concorrência) e T07 (NULL). Se perguntarem
> "por que não bcrypt?": escopo didático do edital + registrado como evolução futura.
> Demonstrar que `vw_*` nunca expõe `senha_hash`.

## Slide 7 — Dificuldades, soluções e divisão

1. Trigger recursivo/erro 1442 → cálculo em `BEFORE` (`NEW`), auditoria em
   `AFTER` em tabela distinta.
2. `NULL` em notas → convenção "não lançada" + `Cursando` (`fn_calcular_media` pura).
3. Pré-requisito N:N → `NOT EXISTS` (só `Aprovado` habilita) + anti-ciclo.
4. Acesso só-via-SP → `db.py` (regex `sp_`/`vw_`) + `erro_amigavel` + bloqueio no banco.
5. Concorrência de vagas → dupla checagem (procedure + `trg_valida_vagas`); `FOR UPDATE` como evolução.
6. `CHECK` pré-8.0.16 → validação duplicada em procedures/triggers.

| Integrante | Frente |
|---|---|
| Manuela Albuquerque Wentz | Modelagem, schema, 3FN |
| Danieli Cristina de Carvalho Breves | Procedures/functions/triggers, testes |
| Fernando Riad da Silva Ribeiro | Aplicação, integração, criptografia, telas |
| Nickson Henrique Cavéquia Silva | Relatório, slides, views, perfis |

> **Notas do orador:** Escolher 2 itens para detalhar conforme o tempo (sugerido:
> 1 e 5). Matriz completa em `docs/divisao_trabalho.md`.

## Slide 8 — Conclusão e encerramento

**Título:** Obrigado — perguntas?

- Regras no banco, aplicação disciplinada, senhas com hash, auditoria total,
  9/9 testes.
- Futuro: bcrypt/argon2, paginação, nota de exame persistida, testes de
  concorrência, CI.

**Artefatos:** `docs/relatorio.md` · `sql/*.sql` · `app/` ·
`app/screenshots/` · banco `sga_fbi`.

> **Notas do orador:** Fechar com a frase-síntese do projeto e abrir para perguntas.
> Deixar este slide projetado durante as perguntas. Ter à mão: diagrama Mermaid,
> `sql/04_testes.sql` e `vw_boletim`.