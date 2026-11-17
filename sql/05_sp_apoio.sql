-- =====================================================================
-- 05_sp_apoio.sql — Procedures/views COMPLEMENTARES (mantem conformidade)
-- Banco: sga_fbi
-- Motivo: o edital lista apenas SPs academicas (login, matricula, notas,
-- exame, historico, fechar semestre). Os cadastros de Aluno e as leituras
-- de apoio tambem precisam existir SEM quebrar a regra
-- "toda comunicacao via CALL sp_* ou SELECT vw_*".
-- Este arquivo cria exclusivamente sp_* e vw_* (nenhum acesso direto
-- a tabela pelo app). Rode APOS 01_schema.sql, 02_objetos.sql, 03_dados.sql.
-- Ordem sugerida: 01_schema, 02_objetos, 03_dados, 04_testes, 05_sp_apoio.
--
-- Schema real (01_schema.sql):
--   aluno(id_aluno PK AI, ra VARCHAR(20) UNIQUE NOT NULL, nome, cpf UNIQUE,
--         email, data_nascimento DATE, id_curso FK, status ENUM)
--   turma(id_turma PK AI, id_disciplina FK, id_professor FK, semestre,
--         vagas INT, total_aulas INT)
--   log_nota(id_log PK AI, id_matricula FK, campo VARCHAR(20),
--            valor_antigo VARCHAR(20), valor_novo VARCHAR(20),
--            usuario VARCHAR(100), data_hora DATETIME)
-- =====================================================================
USE sga_fbi;

-- ---- Views de apoio (leitura via SELECT vw_*) --------------------------
CREATE OR REPLACE VIEW vw_alunos AS
SELECT a.id_aluno AS id_aluno,
       a.ra       AS ra,
       a.nome     AS nome,
       a.cpf      AS cpf,
       a.email    AS email,
       a.data_nascimento AS data_nascimento,
       a.id_curso AS id_curso,
       c.nome     AS curso,
       a.status   AS status
FROM aluno a
LEFT JOIN curso c ON c.id_curso = a.id_curso;

CREATE OR REPLACE VIEW vw_log_nota AS
SELECT l.id_log        AS id_log,
       l.data_hora     AS `data`,
       l.data_hora     AS data_hora,
       l.id_matricula  AS id_matricula,
       l.campo         AS campo,
       l.campo         AS campo_alterado,
       l.valor_antigo  AS valor_antigo,
       l.valor_novo    AS valor_novo,
       l.usuario       AS usuario
FROM log_nota l;

DELIMITER $$

-- ---- Alunos ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_listar_alunos$$
CREATE PROCEDURE sp_listar_alunos()
BEGIN
  SELECT * FROM vw_alunos ORDER BY nome;
END$$

DROP PROCEDURE IF EXISTS sp_criar_aluno$$
CREATE PROCEDURE sp_criar_aluno(
  IN p_nome VARCHAR(100), IN p_cpf VARCHAR(14),
  IN p_email VARCHAR(100), IN p_id_curso INT)
BEGIN
  DECLARE v_ra VARCHAR(20);
  IF p_nome IS NULL OR TRIM(p_nome) = '' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Nome do aluno e obrigatorio.';
  END IF;
  IF p_id_curso IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Curso do aluno e obrigatorio.';
  END IF;
  -- RA gerado a partir do timestamp (UNIQUE NOT NULL exigido pelo schema).
  -- Para controle total do RA, use sp_criar_aluno_com_ra abaixo.
  SET v_ra = DATE_FORMAT(NOW(), '2026%m%d%H%i%S');
  INSERT INTO aluno (ra, nome, cpf, email, id_curso, status)
  VALUES (v_ra, TRIM(p_nome), NULLIF(TRIM(p_cpf), ''), NULLIF(TRIM(p_email), ''), p_id_curso, 'Ativo');
  SELECT LAST_INSERT_ID() AS id_aluno, v_ra AS ra;
END$$

DROP PROCEDURE IF EXISTS sp_criar_aluno_com_ra$$
CREATE PROCEDURE sp_criar_aluno_com_ra(
  IN p_ra VARCHAR(20), IN p_nome VARCHAR(100), IN p_cpf VARCHAR(14),
  IN p_email VARCHAR(100), IN p_data_nascimento DATE, IN p_id_curso INT)
BEGIN
  IF p_ra IS NULL OR TRIM(p_ra) = '' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'RA do aluno e obrigatorio.';
  END IF;
  IF p_nome IS NULL OR TRIM(p_nome) = '' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Nome do aluno e obrigatorio.';
  END IF;
  INSERT INTO aluno (ra, nome, cpf, email, data_nascimento, id_curso, status)
  VALUES (TRIM(p_ra), TRIM(p_nome), NULLIF(TRIM(p_cpf), ''),
          NULLIF(TRIM(p_email), ''), p_data_nascimento, p_id_curso, 'Ativo');
  SELECT LAST_INSERT_ID() AS id_aluno;
END$$

DROP PROCEDURE IF EXISTS sp_editar_aluno$$
CREATE PROCEDURE sp_editar_aluno(
  IN p_id_aluno INT, IN p_nome VARCHAR(100), IN p_email VARCHAR(100))
BEGIN
  IF NOT EXISTS (SELECT 1 FROM aluno WHERE id_aluno = p_id_aluno) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Aluno nao encontrado.';
  END IF;
  UPDATE aluno SET nome = TRIM(p_nome), email = NULLIF(TRIM(p_email), '')
  WHERE id_aluno = p_id_aluno;
END$$

DROP PROCEDURE IF EXISTS sp_excluir_aluno$$
CREATE PROCEDURE sp_excluir_aluno(IN p_id_aluno INT)
BEGIN
  IF EXISTS (SELECT 1 FROM matricula WHERE id_aluno = p_id_aluno) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Aluno possui matriculas e nao pode ser excluido.';
  END IF;
  DELETE FROM aluno WHERE id_aluno = p_id_aluno;
END$$

-- ---- Listas de apoio para combos ---------------------------------------
DROP PROCEDURE IF EXISTS sp_listar_cursos$$
CREATE PROCEDURE sp_listar_cursos()
BEGIN
  SELECT id_curso, nome FROM curso ORDER BY nome;
END$$

DROP PROCEDURE IF EXISTS sp_listar_turmas$$
CREATE PROCEDURE sp_listar_turmas()
BEGIN
  SELECT * FROM vw_turmas_lotacao;
END$$

-- ---- Auditoria ----------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_listar_log$$
CREATE PROCEDURE sp_listar_log()
BEGIN
  SELECT * FROM vw_log_nota ORDER BY `data` DESC LIMIT 500;
END$$

DELIMITER ;
