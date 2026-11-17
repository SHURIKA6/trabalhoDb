# SGA-FBI — Banco de Dados (`sga_fbi`)

MySQL 8.0+ / MySQL Workbench compatível · InnoDB · `utf8mb4_unicode_ci`.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `sql/01_schema.sql` | `DROP/CREATE DATABASE sga_fbi` + 9 tabelas (3FN) + CHECKs + UNIQUEs + INDEXes |
| `sql/02_objetos.sql` | 4 functions, 3 views, 6 procedures, 4 triggers (RN01–RN09) |
| `sql/03_dados.sql` | Massa de dados: 5 usuários, 3 cursos, 6 disciplinas, 5 professores, 20 alunos, 5 turmas, 35 matrículas |
| `sql/04_testes.sql` | 9 testes de aceitação do edital |
| `sql/05_sp_apoio.sql` | Apoio à aplicação: `vw_alunos`, `vw_log_nota`, `sp_listar/criar/editar/excluir_aluno`, `sp_listar_cursos/turmas/log` (rode por último) |
| `sql/05_sp_apoio.sql` | Apoio ao app (time do app): `vw_alunos`, `vw_log_nota`, `sp_listar/criar/editar/excluir_aluno`, `sp_listar_cursos/turmas/log` — executado por último, usa o esquema deste README |

> Nota de compatibilidade: o `05_sp_apoio.sql` é mantido pelo time do app;
> ele referencia apenas colunas reais deste esquema (`aluno.ra`,
> `turma.vagas`, `log_nota.campo/usuario/...`). Não renomear colunas do
> `01_schema.sql` sem atualizar o 05.

## Como executar no Workbench (na ordem)

1. Abra uma conexão local (ex.: `root@localhost`).
2. Abra e execute `sql/01_schema.sql` (ícone ⚡ ou `Ctrl+Shift+Enter`) — cria o banco do zero.
3. Abra e execute `sql/02_objetos.sql` — cria funções/views/procedures/triggers.
4. Abra e execute `sql/03_dados.sql` — carga inicial (IDs fixos).
5. Abra e execute `sql/04_testes.sql` **por blocos** (selecione cada TESTE + `Ctrl+Enter`):
   os testes 2–5 têm o `CALL` de erro **comentado** de propósito (MySQL não tem
   TRY/CATCH em script; um `SIGNAL` abortaria o restante). Para ver o erro,
   descomente a linha indicada e execute-a isoladamente.

Via CLI (alternativo):

```bash
mysql -u root -p < sql/01_schema.sql
mysql -u root -p < sql/02_objetos.sql
mysql -u root -p < sql/03_dados.sql
mysql -u root -p < sql/04_testes.sql
```

## Logins / senhas (massa de dados)

`senha_hash = SHA2(<senha>, 256)` (hex de 64 chars). Senhas em texto puro
existem **apenas** neste README e nos comentários do `03_dados.sql`.

| login | senha | perfil | nome |
|---|---|---|---|
| `coord1` | `senha123` | Coordenador | Ana Coordenadora (id 1) |
| `coord2` | `coord123` | Coordenador | Bruno Chefia (id 2) |
| `sec1` | `sec123` | Secretario | Carla Secretaria (id 3) |
| `sec2` | `sec123` | Secretario | Diego Atendente (id 4) |
| `sec3` | `sec123` | Secretario | Elisa Balcão (id 5) |

Teste rápido: `CALL sp_LoginUsuario('coord1', SHA2('senha123',256));` → 1 linha;
com senha errada → 0 linhas.

## Decisões de modelagem

- **3FN**: `pre_requisito` extraída (N:M de `disciplina` com PK composta +
  trigger `trg_valida_pr_diferente` anti-auto-requisito — MySQL aceitaria `CHECK`, MariaDB retorna erro 1901); `log_nota` separada da
  `matricula`; dados de curso/disciplina/turma não duplicados nas views.
- **FKs**: `disciplina→curso` CASCADE; `aluno→curso` SET NULL (preserva aluno
  se curso for removido); `turma→disciplina` RESTRICT (não apaga disciplina
  com turma); `matricula→aluno/turma` CASCADE; `matricula→usuario` SET NULL
  (auditoria não impede apagar operador); `log_nota→matricula` CASCADE.
- **CHECKs**: `vagas>0`, `total_aulas>0`, `carga_horaria>0`, notas 0–10
  (`NULL` permitido = nota ainda não lançada), `faltas>=0`.
- **RN04 × trigger**: `trg_atualiza_situacao` (BEFORE UPDATE) **e**
  `trg_atualiza_situacao_ins` (BEFORE INSERT, mesma regra) recalculam
  `media_final`/`situacao` de forma *inline* com `NEW` + `total_aulas`
  (não chamam `fn_situacao`, que leria a linha antiga). A frequência
  `<75%` tem prioridade sobre qualquer nota — inclusive média 9+.
- **Sem recursão**: procedures fazem `UPDATE matricula` (disparam triggers);
  triggers nunca chamam procedures nem modificam `matricula`; funções de
  trigger (`fn_calcular_media`) são puras (sem SQL). `fn_situacao`/`fn_frequencia`
  são só para consulta (views/testes), nunca usadas dentro dos triggers.
- **Auditoria (RN08)**: `trg_auditoria_nota` (AFTER UPDATE) insere **uma linha
  por campo alterado** (`n1`,`n2`,`exame`,`faltas`, comparação null-safe
  `<=>`); `usuario` = `login` do `usuario` via `NEW.id_usuario`, com fallback
  para `USER()` quando `NULL`.
- **Vagas (RN05) em 2 camadas**: `trg_valida_vagas` (BEFORE INSERT, última
  barreira, conta `matricula` × `vagas`) + checagem antecipada em
  `sp_matricular_aluno` (mensagem amigável). Condição de corrida sob
  concorrência é conhecida e aceita no escopo (sem `SELECT FOR UPDATE`).
- **Pré-requisito (RN06)**: só `situacao='Aprovado'` habilita; `Em exame`,
  `Reprovado*` e `Cursando` não habilitam. Verificação por `NOT EXISTS`
  (todos os requisitos precisam estar aprovados).
- **Fechamento (sp_fechar_semestre)**: exige `perfil='Coordenador'` (`SIGNAL`
  caso contrário), usa `CURSOR` + `START TRANSACTION/COMMIT` com
  `EXIT HANDLER ... ROLLBACK; RESIGNAL`; cada `UPDATE` re-dispara o trigger
  de recálculo.
- **Carga inicial respeita RN05/RN06**: turma 5 lotada exatamente 3/3;
  turmas 3/4 só recebem alunos já `Aprovado` na base (t1/t2 em `2025.2` →
  t3/t4 em `2026.1`). Cobertura das 35 matrículas: 18 Aprovado, 5 Em exame,
  5 Rep.Nota, 4 Rep.Falta (m10/m18/m25/m32, todos com média ≥ 9 em algum
  caso), 3 Cursando. `fn_cr_aluno` = média ponderada por `carga_horaria`
  só de `Aprovado` (`NULL` se nenhum).
- **Validação**: revisão estática rigorosa de sintaxe MySQL 8.0
  (`DELIMITER //`, `SIGNAL SQLSTATE '45000'`, `DECLARE ... HANDLER`,
  `SHA2()`, `DEFAULT (CURDATE())`, `CREATE OR REPLACE VIEW`); sem servidor
  disponível no ambiente, sem teste de execução real.
