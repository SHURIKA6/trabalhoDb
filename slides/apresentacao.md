# Apresentação — SGA / Faculdade do Bug Infinito (roteiro slide-a-slide)

**Formato:** 14 slides, ~15 minutos (aprox. 1 min/slide) + 5 min de demo e perguntas.
**Deck executável:** `slides/apresentacao.html` (standalone, setas/click para navegar, `P` para imprimir).
**Integrantes:** Nome 1, Nome 2, Nome 3, Nome 4 — **Disciplina:** LBD — **Data:** 23/11/2026.

---

## Slide 1 — Título

**Título:** SGA — Sistema de Gestão Acadêmica da Faculdade do Bug Infinito
**Subtítulo:** Banco íntegro, seguro e auditável | MySQL 8 + Python (só SP/View)
**Rodapé:** LBD · 23/11/2026 · Nome 1 · Nome 2 · Nome 3 · Nome 4

> **Notas do orador:** Cumprimentar a banca, apresentar o grupo em 20 segundos e
> anunciar o roteiro: problema, modelagem, arquitetura, regras, segurança, testes,
> dificuldades e conclusão. Não entrar em detalhes ainda.

## Slide 2 — Agenda

1. Problema e objetivos
2. Modelagem (MER + relacional)
3. Arquitetura: só SP/View
4. Regras RN01–RN09 (com demo)
5. Segurança e perfis
6. Testes (9/9)
7. Dificuldades e soluções
8. Divisão e conclusão

> **Notas do orador:** A agenda espelha o relatório. Avisar que a demo ao vivo
> (matrícula + notas + auditoria) ocorre no slide 7.

## Slide 3 — Problema

- Controle acadêmico descentralizado: matrículas sem pré-requisito, turmas
  lotadas, médias divergentes, notas alteradas sem auditoria, senhas frágeis.
- Objetivo: centralizar no banco `sga_fbi`, com regras **dentro do SGBD**,
  aplicação Python consumindo apenas procedures e views.

> **Notas do orador:** Dar 1 exemplo concreto de cada dor (ex.: "aluno cursando
> LBD avançado sem ter sido aprovado no básico"). Conectar cada dor a uma regra
> RN que a elimina (antecipar sem detalhar).

## Slide 4 — MER (entidades e cardinalidades)

- 9 entidades: `usuario`, `curso`, `disciplina`, `pre_requisito` (N:N
  auto-relacionamento), `professor`, `aluno`, `turma`, `matricula`, `log_nota`.
- Destaques: R3 (pré-requisito N:N), R6 (matrícula como associativa com
  atributos avaliativos + `UNIQUE`), R7/R8 (auditoria).
- Apontar para o diagrama Mermaid do relatório (Seção 6).

> **Notas do orador:** Explicar por que matrícula é associativa (carrega notas,
> frequência, situação) e por que pré-requisito é auto-relacionamento. Se
> perguntarem de ciclos: `CHECK` anti-auto-referência + validação na procedure.

## Slide 5 — Modelo lógico + 3FN

- Lógico: 9 relações, PKs simples, FKs, `UNIQUE`s, `ENUM`s, `CHECK`s.
- 1FN: sem listas em célula (`pre_requisito` é tabela, não coluna).
- 2FN: PKs simples (sem dependência parcial); `pre_requisito` sem atributos.
- 3FN: sem transitivas; `media_final`/`situacao` são derivados calculados pelo
  banco, não entrada manual.

> **Notas do orador:** Usar o exemplo `media_final`: parece redundância, mas é
> fato derivado materializado sob regra determinística — por isso não viola 3FN.

## Slide 6 — Arquitetura: só SP/View

- `app/db.py`: `call_procedure` (só `sp_*`) + `select_view` (só `vw_*`);
  sem função de query livre; regex valida identificadores.
- Usuário `sga_app`: `EXECUTE` + `SELECT` em views; sem DML direto.
- Erros de regra via `SIGNAL 45000` → `erro_amigavel()` na tela.

> **Notas do orador:** Mostrar `app/db.py` (30 segundos): apontar as regexes
> `_PROC_RE`/`_VIEW_RE` e a ausência de `query(sql)`. Frase-chave: "a aplicação
> não consegue violar as regras mesmo que queira".

## Slide 7 — RN + demo (parte 1: matrícula)

- RN05 (vagas: `trg_valida_vagas` + `sp_matricular_aluno`), RN06 (pré-requisito via `NOT EXISTS`
  só com `Aprovado`), RN09 (status `Ativo`), duplicidade (`UNIQUE`).
- **Demo ao vivo:** matricular aluno sem pré-requisito → erro amigável 45000;
  tentar turma 5 lotada 3/3 → erro; matrícula válida → ok.

> **Notas do orador:** Executar `CALL sp_matricular_aluno` com caso inválido
> primeiro (mostra o SIGNAL), depois o válido. Ter prints de backup
> (`05_matricula.png`) caso o banco ao vivo falhe.

## Slide 8 — RN + demo (parte 2: notas e auditoria)

- RN01/RN02 (média parcial), RN03 (exame: `sp_lancar_exame` só se `Em exame`),
  RN04 (falta: `fn_frequencia`/`fn_situacao`, prioridade), RN07 (0–10, `NULL` = não lançada),
  RN08 (auditoria `trg_auditoria_nota` → `log_nota`).
- **Demo:** `sp_lancar_notas` → trigger calcula média/situação; mostrar linha
  nova em `log_nota`.

> **Notas do orador:** Mostrar `vw_boletim` antes e depois do lançamento, e a
> linha de auditoria com antes/depois + autor. Reforçar: a aplicação nunca envia
> média — o banco calcula.

## Slide 9 — Segurança e perfis

- Hash SHA-256 hex (`SHA2` no banco, `hashlib` no app); `CHAR(64)`;
  `sp_LoginUsuario` nunca retorna senha; `.env` fora do código.
- Matriz Secretário × Coordenador (tabela do relatório, Seção 10.2):
  Secretário: alunos, matrículas, boletim/histórico/lotação;
  Coordenador: tudo + notas/exame, desempenho, faturamento, fechar semestre, auditoria.
  Dupla barreira: tela oculta (`permissoes.py`) + banco (`sp_fechar_semestre` exige Coordenador).

> **Notas do orador:** Se perguntarem "por que não bcrypt?": escopo didático do
> edital + registrado como evolução futura. Demonstrar que `vw_*` nunca expõe
> `senha_hash`.

## Slide 10 — Testes (9 obrigatórios)

| Bloco | Testes | Cobertura |
|---|---|---|
| Login | 1 | senha errada → vazio |
| Matrícula | 2–4 | RN05 lotada, RN06 pré-req, RN09 trancado |
| Notas | 5–7 | RN07 CHECK 11.0, RN02/RN03 exame, RN04 falta com média 9 |
| Auditoria/views | 8–9 | RN08 `log_nota`, 3 views |

Resultado: **9/9 conforme esperado** (`sql/04_testes.sql`).

> **Notas do orador:** Não ler a tabela inteira; destacar Teste 7 (média 9 + falta →
> `Reprovado por Falta`) e Teste 6 (fluxo exame). Dizer como reproduzir: 01_schema → 02_objetos → 03_dados → 04_testes.

## Slide 11 — Dificuldades e soluções (resumo)

1. Trigger recursivo/erro 1442 → cálculo em `BEFORE` (`NEW`), auditoria em
   `AFTER` em tabela distinta.
2. `NULL` em notas → convenção "não lançada" + `Cursando` (`fn_calcular_media` pura).
3. Pré-requisito N:N → `NOT EXISTS` (só `Aprovado` habilita) + anti-ciclo.
4. Acesso só-via-SP → `db.py` (regex `sp_`/`vw_`) + `erro_amigavel` + bloqueio no banco.
5. Concorrência de vagas → dupla checagem (procedure + `trg_valida_vagas`); `FOR UPDATE` como evolução.
6. `CHECK` pré-8.0.16 → validação duplicada em procedures/triggers.

> **Notas do orador:** Escolher 2 itens para detalhar conforme o tempo (sugerido:
> 1 e 5). Remeter à Seção 14 do relatório para o detalhamento de 1 página.

## Slide 12 — Divisão do trabalho

| Integrante | Frente |
|---|---|
| Nome 1 | Modelagem, schema, 3FN |
| Nome 2 | Procedures/functions/triggers, testes |
| Nome 3 | Aplicação, integração, criptografia, telas |
| Nome 4 | Relatório, slides, views, perfis |

> **Notas do orador:** 20 segundos. Destacar que todos revisaram o relatório e
> que a matriz completa está em `docs/divisao_trabalho.md`.

## Slide 13 — Conclusão

- Regras no banco, aplicação disciplinada, senhas com hash, auditoria total,
  9/9 testes.
- Futuro: bcrypt/argon2, paginação, nota de exame persistida, testes de
  concorrência, CI.

> **Notas do orador:** Fechar com a frase-síntese do projeto e abrir para perguntas.

## Slide 14 — Encerramento / perguntas

**Título:** Obrigado — perguntas?
**Contatos/artefatos:** `docs/relatorio.md` · `sql/*.sql` · `app/` ·
`app/screenshots/` · banco `sga_fbi`.

> **Notas do orador:** Deixar este slide projetado durante as perguntas. Ter à mão:
> diagrama Mermaid, `sql/04_testes.sql` e `vw_boletim` para perguntas técnicas.
