-- ============================================================================
-- SGA-FBI | sql/04_testes.sql
-- 9 testes de aceitação do edital (resultado esperado em comentário)
-- MySQL não tem TRY/CATCH de script: casos de erro esperado (SIGNAL) ficam
-- COMENTADOS para não abortar o script + SELECT de verificação ativo.
-- Para reproduzir o erro, descomente a linha indicada e execute separadamente.
-- Ordem: executar APÓS 03_dados.sql
-- ============================================================================
USE sga_fbi;

-- ============================================================================
-- TESTE 1 — Login com senha errada retorna vazio (0 linhas)
-- ESPERADO: result set vazio (login não autentica, sem erro).
-- ============================================================================
CALL sp_LoginUsuario('coord1', SHA2('senha_errada', 256));
-- Verificação positiva (controle): deve retornar 1 linha
CALL sp_LoginUsuario('coord1', SHA2('senha123', 256));

-- ============================================================================
-- TESTE 2 — Matrícula em turma LOTADA deve falhar (RN05)
-- Turma 5 tem vagas=3 e 3 matriculados (33,34,35) => lotada.
-- ESPERADO ao descomentar: ERROR 1644 (45000) 'Turma lotada...'.
-- ============================================================================
SELECT * FROM vw_turmas_lotacao WHERE id_turma = 5;
-- DESCOMENTE para ver o erro (aborta o script neste ponto):
-- CALL sp_matricular_aluno(13, 5, 3);

-- ============================================================================
-- TESTE 3 — Matrícula SEM pré-requisito deve falhar (RN06)
-- Aluno 2 foi 'Em exame' em Algoritmos (t1), logo NÃO tem 'Aprovado' no
-- requisito da disciplina 2 (Estrutura de Dados, turma 3).
-- ESPERADO ao descomentar: ERROR 1644 (45000) 'Pré-requisito não cumprido...'.
-- ============================================================================
SELECT m.id_matricula, m.situacao FROM matricula m JOIN turma t ON t.id_turma = m.id_turma
 WHERE m.id_aluno = 2 AND t.id_disciplina = 1;
-- DESCOMENTE para ver o erro:
-- CALL sp_matricular_aluno(2, 3, 3);

-- ============================================================================
-- TESTE 4 — Aluno TRANCADO/FORMADO não pode se matricular (RN09)
-- Aluno 18 = Trancado, aluno 20 = Formado.
-- ESPERADO ao descomentar: ERROR 1644 (45000) 'Matrícula bloqueada... (RN09)'.
-- ============================================================================
SELECT id_aluno, nome, status FROM aluno WHERE id_aluno IN (18, 20);
-- DESCOMENTE para ver o erro (uma por vez):
-- CALL sp_matricular_aluno(18, 5, 3);
-- CALL sp_matricular_aluno(20, 5, 3);

-- ============================================================================
-- TESTE 5 — Nota fora do intervalo 0–10 viola CHECK (RN07)
-- ESPERADO ao descomentar: ERROR 3819 'Check constraint violated'
-- (chk_matricula_n1). Nenhuma linha é alterada.
-- ============================================================================
SELECT id_matricula, n1, n2 FROM matricula WHERE id_matricula = 1;
-- DESCOMENTE para ver o erro:
-- CALL sp_lancar_notas(1, 11.00, 8.00, 0, 3);

-- ============================================================================
-- TESTE 6 — Fluxo de exame: Cursando -> Em exame -> (exame) -> Aprovado
-- Usa m24 (aluno 10 / turma 3), que parte de Cursando (n1/n2 NULL).
-- Bloco RESET garante reexecução idempotente. ESPERADO:
--   após sp_lancar_notas(24, 5, 6): media 5.50, situacao 'Em exame';
--   após sp_lancar_exame(24, 6): media_final 5.75, situacao 'Aprovado'
--   (parcial 5.50 + exame 6.00)/2 = 5.75 >= 5.
-- ============================================================================
UPDATE matricula SET n1 = NULL, n2 = NULL, exame = NULL, faltas = 0, id_usuario = 3
 WHERE id_matricula = 24;
SELECT id_matricula, n1, n2, exame, media_final, situacao FROM matricula WHERE id_matricula = 24;

CALL sp_lancar_notas(24, 5.00, 6.00, 2, 3);
-- ESPERADO: n1=5.00 n2=6.00 media_final=5.50 situacao='Em exame'
SELECT id_matricula, n1, n2, exame, media_final, situacao FROM matricula WHERE id_matricula = 24;

CALL sp_lancar_exame(24, 6.00, 3);
-- ESPERADO: exame=6.00 media_final=5.75 situacao='Aprovado'
SELECT id_matricula, n1, n2, exame, media_final, situacao FROM matricula WHERE id_matricula = 24;

-- Controles negativos do fluxo (devem falhar se descomentados):
-- a) exame em quem NÃO está 'Em exame' (m1 = Aprovado):
-- CALL sp_lancar_exame(1, 8.00, 3);  -- ESPERADO: ERROR 1644 'só pode ser lançado...'
-- b) Secretário tentando fechar semestre (ver Teste extra em 02 — só Coordenador):
-- CALL sp_fechar_semestre('2026.1', 3); -- ESPERADO: ERROR 1644 'Apenas Coordenador...'

-- ============================================================================
-- TESTE 7 — Frequência < 75% => 'Reprovado por Falta' mesmo com média 9 (RN04)
-- m10: n1=9 n2=9 (média 9.00) + 16 faltas em 60 aulas = 73.33% freq.
-- m25: n1=9 n2=9 + 18 faltas = 70.00%. m32: 9.50/9.00 + 17 faltas = 71.67%.
-- ESPERADO: as 3 linhas abaixo com situacao='Reprovado por Falta' e media>=9.
-- ============================================================================
SELECT m.id_matricula, a.nome AS aluno, d.nome AS disciplina,
       m.n1, m.n2, m.media_final, m.faltas, t.total_aulas,
       fn_frequencia(m.id_matricula) AS frequencia,
       fn_situacao(m.id_matricula)   AS situacao_fn,
       m.situacao
  FROM matricula m
  JOIN turma t ON t.id_turma = m.id_turma
  JOIN disciplina d ON d.id_disciplina = t.id_disciplina
  JOIN aluno a ON a.id_aluno = m.id_aluno
 WHERE m.id_matricula IN (10, 25, 32);

-- ============================================================================
-- TESTE 8 — Auditoria: alterações de nota geram linhas em log_nota (RN08)
-- O Teste 6 alterou n1/n2/faltas e depois exame de m24 => >= 4 linhas de log.
-- ESPERADO: SELECT abaixo retorna linhas com campo/antigo/novo/usuario/data_hora.
-- ============================================================================
SELECT id_log, id_matricula, campo, valor_antigo, valor_novo, usuario, data_hora
  FROM log_nota
 WHERE id_matricula = 24
 ORDER BY id_log DESC;
-- Visão geral da auditoria:
SELECT COUNT(*) AS total_logs, COUNT(DISTINCT id_matricula) AS matriculas_auditadas FROM log_nota;

-- ============================================================================
-- TESTE 9 — Views de relatório (boletim, lotação, desempenho)
-- ESPERADO: 3 result sets não vazios; conferências:
--  vw_turmas_lotacao: turma 5 com 3/3 (100%); turmas 1-4 com vagas_restantes > 0.
--  vw_desempenho_turma: pct_aprovados/pct_reprovados entre 0 e 100.
-- ============================================================================
-- 9a) Boletim (amostra do aluno 1 + contagem total = 35 matrículas)
SELECT COUNT(*) AS total_boletim FROM vw_boletim;
SELECT * FROM vw_boletim WHERE id_aluno = 1 ORDER BY semestre, disciplina;

-- 9b) Lotação das turmas
SELECT * FROM vw_turmas_lotacao ORDER BY id_turma;

-- 9c) Desempenho por turma
SELECT * FROM vw_desempenho_turma ORDER BY id_turma;

-- 9d) Extras úteis (CR do aluno 1 e histórico via procedure)
SELECT fn_cr_aluno(1) AS cr_aluno_1;
CALL sp_historico_aluno(1);
