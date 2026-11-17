-- ============================================================================
-- SGA-FBI | sql/03_dados.sql
-- Massa de dados inicial (IDs fixos p/ reprodutibilidade dos testes)
-- Ordem: executar APÓS 02_objetos.sql
-- Logins/senhas: ver cabeçalho + sql/README.md
--   coord1 / senha123 (Coordenador) | coord2 / coord123 (Coordenador)
--   sec1   / sec123   (Secretario)  | sec2   / sec123
--   sec3   / sec123
-- ============================================================================
USE sga_fbi;

-- ----------------------------------------------------------------------------
-- usuarios (5): 2 Coordenadores + 3 Secretários
-- senha_hash = SHA2(<senha>, 256) — hash SHA-256 em hex (64 chars)
-- ----------------------------------------------------------------------------
INSERT INTO usuario (id_usuario, nome, cpf, email, login, senha_hash, perfil) VALUES
(1, 'Ana Coordenadora', '111.111.111-11', 'ana.coord@sga.edu',   'coord1', SHA2('senha123', 256), 'Coordenador'),
(2, 'Bruno Chefia',     '222.222.222-22', 'bruno.coord@sga.edu', 'coord2', SHA2('coord123', 256), 'Coordenador'),
(3, 'Carla Secretaria',  '333.333.333-33', 'carla.sec@sga.edu',  'sec1',   SHA2('sec123', 256),   'Secretario'),
(4, 'Diego Atendente',   '444.444.444-44', 'diego.sec@sga.edu',  'sec2',   SHA2('sec123', 256),   'Secretario'),
(5, 'Elisa Balcao',      '555.555.555-55', 'elisa.sec@sga.edu',  'sec3',   SHA2('sec123', 256),   'Secretario');

-- ----------------------------------------------------------------------------
-- cursos (3)
-- ----------------------------------------------------------------------------
INSERT INTO curso (id_curso, nome, carga_horaria_total, turno) VALUES
(1, 'Engenharia de Software', 3200, 'Noturno'),
(2, 'Administração',          2800, 'Matutino'),
(3, 'Ciência de Dados',       3000, 'Vespertino');

-- ----------------------------------------------------------------------------
-- disciplinas (6) — encadeadas por pré-requisito
-- ----------------------------------------------------------------------------
INSERT INTO disciplina (id_disciplina, id_curso, nome, carga_horaria, periodo) VALUES
(1, 1, 'Algoritmos',                 80, 1),
(2, 1, 'Estrutura de Dados',         80, 2),
(3, 1, 'Cálculo I',                  80, 1),
(4, 1, 'Cálculo II',                 80, 2),
(5, 1, 'Banco de Dados',             80, 3),
(6, 2, 'Introdução à Administração', 60, 1);

-- pré-requisitos: Estrutura<-Algoritmos, Cálculo II<-Cálculo I, BD<-Estrutura
INSERT INTO pre_requisito (id_disciplina, id_disciplina_requisito) VALUES
(2, 1),
(4, 3),
(5, 2);

-- ----------------------------------------------------------------------------
-- professores (5)
-- ----------------------------------------------------------------------------
INSERT INTO professor (id_professor, nome, cpf, email, titulacao, data_admissao) VALUES
(1, 'Carlos Silva',  '901.901.901-91', 'carlos.silva@sga.edu',  'Doutor',       '2015-02-01'),
(2, 'Maria Souza',   '902.902.902-92', 'maria.souza@sga.edu',   'Mestre',       '2018-03-15'),
(3, 'João Pereira',  '903.903.903-93', 'joao.pereira@sga.edu',  'Mestre',       '2020-08-01'),
(4, 'Paula Lima',    '904.904.904-94', 'paula.lima@sga.edu',    'Doutora',      '2019-01-10'),
(5, 'Rafael Costa',  '905.905.905-95', 'rafael.costa@sga.edu',  'Especialista', '2022-07-01');

-- ----------------------------------------------------------------------------
-- alunos (20): 17 Ativos + 2 Trancados + 1 Formado
-- ----------------------------------------------------------------------------
INSERT INTO aluno (id_aluno, ra, nome, cpf, email, data_nascimento, id_curso, status) VALUES
( 1, '20260001', 'Rafael Almeida',  '101.101.101-10', 'rafael.almeida@aluno.sga.edu',  '2004-01-15', 1, 'Ativo'),
( 2, '20260002', 'Juliana Santos',  '102.102.102-10', 'juliana.santos@aluno.sga.edu',  '2003-05-20', 1, 'Ativo'),
( 3, '20260003', 'Pedro Henrique',  '103.103.103-10', 'pedro.henrique@aluno.sga.edu',  '2005-02-11', 1, 'Ativo'),
( 4, '20260004', 'Mariana Oliveira','104.104.104-10', 'mariana.oliveira@aluno.sga.edu','2004-07-30', 1, 'Ativo'),
( 5, '20260005', 'Lucas Ferreira',  '105.105.105-10', 'lucas.ferreira@aluno.sga.edu',  '2003-11-02', 1, 'Ativo'),
( 6, '20260006', 'Beatriz Rocha',   '106.106.106-10', 'beatriz.rocha@aluno.sga.edu',   '2005-04-18', 1, 'Ativo'),
( 7, '20260007', 'Thiago Martins',  '107.107.107-10', 'thiago.martins@aluno.sga.edu',  '2004-09-25', 1, 'Ativo'),
( 8, '20260008', 'Camila Barbosa',  '108.108.108-10', 'camila.barbosa@aluno.sga.edu',  '2003-12-08', 1, 'Ativo'),
( 9, '20260009', 'Felipe Cardoso',  '109.109.109-10', 'felipe.cardoso@aluno.sga.edu',  '2004-03-14', 1, 'Ativo'),
(10, '20260010', 'Larissa Dias',    '110.110.110-10', 'larissa.dias@aluno.sga.edu',    '2005-06-22', 1, 'Ativo'),
(11, '20260011', 'Gustavo Moreira', '111.111.112-11', 'gustavo.moreira@aluno.sga.edu', '2004-08-19', 1, 'Ativo'),
(12, '20260012', 'Renata Castro',   '112.112.112-11', 'renata.castro@aluno.sga.edu',   '2003-10-05', 1, 'Ativo'),
(13, '20260013', 'André Pinto',     '113.113.113-11', 'andre.pinto@aluno.sga.edu',     '2005-01-27', 1, 'Ativo'),
(14, '20260014', 'Patrícia Gomes',  '114.114.114-11', 'patricia.gomes@aluno.sga.edu',  '2004-04-09', 1, 'Ativo'),
(15, '20260015', 'Vinícius Teixeira','115.115.115-11','vinicius.teixeira@aluno.sga.edu','2003-08-16',1, 'Ativo'),
(16, '20260016', 'Daniela Ribeiro', '116.116.116-11', 'daniela.ribeiro@aluno.sga.edu', '2004-06-03', 2, 'Ativo'),
(17, '20260017', 'Eduardo Fonseca', '117.117.117-11', 'eduardo.fonseca@aluno.sga.edu', '2005-09-12', 2, 'Ativo'),
(18, '20260018', 'Fernanda Lima',   '118.118.118-11', 'fernanda.lima@aluno.sga.edu',   '2004-02-28', 1, 'Trancado'),
(19, '20260019', 'Bruno Carvalho',  '119.119.119-11', 'bruno.carvalho@aluno.sga.edu',  '2003-07-07', 2, 'Trancado'),
(20, '20260020', 'Aline Souza',     '120.120.120-11', 'aline.souza@aluno.sga.edu',     '2002-05-30', 1, 'Formado');

-- ----------------------------------------------------------------------------
-- turmas (5): t5 lotada de propósito (vagas=3) para teste RN05
-- t1/t2 em 2025.2 (base); t3/t4 em 2026.1 (exigem pré-requisito); t5 sem pré-req
-- ----------------------------------------------------------------------------
INSERT INTO turma (id_turma, id_disciplina, id_professor, semestre, vagas, total_aulas) VALUES
(1, 1, 1, '2025.2', 15, 60),   -- Algoritmos      | Carlos
(2, 3, 2, '2025.2', 15, 60),   -- Cálculo I       | Maria
(3, 2, 1, '2026.1', 12, 60),   -- Estrutura Dados | Carlos (req Algoritmos)
(4, 4, 2, '2026.1', 12, 60),   -- Cálculo II      | Maria  (req Cálculo I)
(5, 6, 3, '2026.1',  3, 40);   -- Intro Adm       | João   (sem pré-req, LOTADA)

-- ----------------------------------------------------------------------------
-- matriculas (35): cobrem Aprovado / Em exame / Rep.Nota / Rep.Falta / Cursando
-- media_final e situacao abaixo conferem com triggers/funções (RN01-RN04).
-- O BEFORE INSERT recalcula os mesmos valores (idempotente).
-- ----------------------------------------------------------------------------

-- Turma 1 — Algoritmos 2025.2 (10): 7 Apr (1 via exame) + 1 Exame + 1 RepNota + 1 RepFalta
INSERT INTO matricula (id_matricula, id_aluno, id_turma, data_matricula, n1, n2, exame, faltas, media_final, situacao, id_usuario) VALUES
( 1,  1, 1, '2025-08-01',  8.50,  7.50, NULL,  5,  8.00, 'Aprovado',            3),
( 2,  4, 1, '2025-08-01',  9.00,  9.50, NULL,  2,  9.25, 'Aprovado',            3),
( 3,  5, 1, '2025-08-01',  7.00,  7.00, NULL,  0,  7.00, 'Aprovado',            3),
( 4,  6, 1, '2025-08-01',  5.50,  6.50,  7.00, 6,  6.50, 'Aprovado',            3),
( 5, 10, 1, '2025-08-01',  8.00,  8.00, NULL,  2,  8.00, 'Aprovado',            3),
( 6, 11, 1, '2025-08-01',  7.20,  7.80, NULL,  3,  7.50, 'Aprovado',            3),
( 7, 15, 1, '2025-08-01',  7.00,  8.00, NULL,  1,  7.50, 'Aprovado',            3),
( 8,  2, 1, '2025-08-01',  6.00,  5.00, NULL,  4,  5.50, 'Em exame',            3),
( 9,  3, 1, '2025-08-01',  3.00,  2.50, NULL,  2,  2.75, 'Reprovado por Nota',  3),
(10,  8, 1, '2025-08-01',  9.00,  9.00, NULL, 16,  9.00, 'Reprovado por Falta', 3);

-- Turma 2 — Cálculo I 2025.2 (9): 6 Apr (1 via exame) + 1 Exame + 1 RepNota + 1 RepFalta
INSERT INTO matricula (id_matricula, id_aluno, id_turma, data_matricula, n1, n2, exame, faltas, media_final, situacao, id_usuario) VALUES
(11,  1, 2, '2025-08-01',  7.50,  8.00, NULL,  3,  7.75, 'Aprovado',            3),
(12,  4, 2, '2025-08-01',  8.00,  9.00, NULL,  1,  8.50, 'Aprovado',            3),
(13,  5, 2, '2025-08-01',  4.50,  5.50,  6.00, 2,  5.50, 'Aprovado',            3),
(14, 11, 2, '2025-08-01',  7.00,  7.50, NULL,  4,  7.25, 'Aprovado',            3),
(15, 14, 2, '2025-08-01', 10.00, 10.00, NULL,  0, 10.00, 'Aprovado',            3),
(16, 15, 2, '2025-08-01',  6.50,  7.50, NULL,  2,  7.00, 'Aprovado',            3),
(17,  6, 2, '2025-08-01',  2.00,  3.00, NULL,  0,  2.50, 'Reprovado por Nota',  3),
(18,  7, 2, '2025-08-01',  9.50,  8.50, NULL, 20,  9.00, 'Reprovado por Falta', 3),
(19, 12, 2, '2025-08-01',  5.00,  4.00, NULL,  2,  4.50, 'Em exame',            3);

-- Turma 3 — Estrutura de Dados 2026.1 (7, req Algoritmos): todos tinham Apr em t1
INSERT INTO matricula (id_matricula, id_aluno, id_turma, data_matricula, n1, n2, exame, faltas, media_final, situacao, id_usuario) VALUES
(20,  1, 3, '2026-02-10',  8.00,  7.50, NULL,  2,  7.75, 'Aprovado',            3),
(21,  4, 3, '2026-02-10',  6.00,  5.50, NULL,  3,  5.75, 'Em exame',            3),
(22,  5, 3, '2026-02-10',  4.00,  3.00, NULL,  1,  3.50, 'Reprovado por Nota',  3),
(23,  6, 3, '2026-02-10',  5.00,  5.50,  6.00, 6,  5.63, 'Aprovado',            3),
(24, 10, 3, '2026-02-10',  NULL,  NULL,  NULL, 0,  NULL, 'Cursando',            3),
(25, 11, 3, '2026-02-10',  9.00,  9.00, NULL, 18,  9.00, 'Reprovado por Falta', 3),
(26, 15, 3, '2026-02-10',  7.00,  7.00, NULL,  0,  7.00, 'Aprovado',            3);

-- Turma 4 — Cálculo II 2026.1 (6, req Cálculo I): todos tinham Apr em t2
INSERT INTO matricula (id_matricula, id_aluno, id_turma, data_matricula, n1, n2, exame, faltas, media_final, situacao, id_usuario) VALUES
(27,  1, 4, '2026-02-10',  7.00,  8.00, NULL,  2,  7.50, 'Aprovado',            3),
(28,  4, 4, '2026-02-10',  5.50,  4.50, NULL,  2,  5.00, 'Em exame',            3),
(29,  5, 4, '2026-02-10',  3.00,  2.00, NULL,  0,  2.50, 'Reprovado por Nota',  3),
(30, 11, 4, '2026-02-10',  5.00,  6.00,  4.00, 1,  4.75, 'Reprovado por Nota',  3),
(31, 14, 4, '2026-02-10',  NULL,  NULL,  NULL, 0,  NULL, 'Cursando',            3),
(32, 15, 4, '2026-02-10',  9.50,  9.00, NULL, 17,  9.25, 'Reprovado por Falta', 3);

-- Turma 5 — Intro Adm 2026.1 (3/3 vagas = LOTADA, sem pré-requisito)
INSERT INTO matricula (id_matricula, id_aluno, id_turma, data_matricula, n1, n2, exame, faltas, media_final, situacao, id_usuario) VALUES
(33, 16, 5, '2026-02-10',  8.00,  8.00, NULL,  1,  8.00, 'Aprovado',  3),
(34, 17, 5, '2026-02-10',  6.00,  6.00, NULL,  0,  6.00, 'Em exame',  3),
(35, 12, 5, '2026-02-10',  NULL,  NULL,  NULL,  0,  NULL, 'Cursando',  3);
