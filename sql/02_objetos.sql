-- ============================================================================
-- SGA-FBI | sql/02_objetos.sql
-- Funções, Views, Procedures e Triggers (RN01-RN09)
-- Ordem: executar APÓS 01_schema.sql
-- MySQL 8.0+ | Workbench: abrir arquivo e executar (Ctrl+Shift+Enter)
-- ============================================================================
USE sga_fbi;

-- ============================================================================
-- 1) FUNCTIONS
-- ============================================================================

DELIMITER //

-- fn_calcular_media(n1,n2,exame): pura, sem acesso a tabelas
-- Se n1 ou n2 NULL => NULL; se exame NULL => (n1+n2)/2; senão ((n1+n2)/2+exame)/2
DROP FUNCTION IF EXISTS fn_calcular_media //
CREATE FUNCTION fn_calcular_media(
  p_n1 DECIMAL(4,2),
  p_n2 DECIMAL(4,2),
  p_exame DECIMAL(4,2)
) RETURNS DECIMAL(4,2)
DETERMINISTIC
BEGIN
  IF p_n1 IS NULL OR p_n2 IS NULL THEN
    RETURN NULL;
  END IF;
  IF p_exame IS NULL THEN
    RETURN ROUND((p_n1 + p_n2) / 2, 2);
  ELSE
    RETURN ROUND(((p_n1 + p_n2) / 2 + p_exame) / 2, 2);
  END IF;
END //

-- fn_frequencia(p_id_matricula): (total_aulas - faltas)/total_aulas*100
DROP FUNCTION IF EXISTS fn_frequencia //
CREATE FUNCTION fn_frequencia(p_id_matricula INT)
RETURNS DECIMAL(5,2)
DETERMINISTIC READS SQL DATA
BEGIN
  DECLARE v_faltas INT DEFAULT NULL;
  DECLARE v_total  INT DEFAULT NULL;
  SELECT m.faltas, t.total_aulas INTO v_faltas, v_total
    FROM matricula m
    JOIN turma t ON t.id_turma = m.id_turma
   WHERE m.id_matricula = p_id_matricula;
  IF v_total IS NULL OR v_total = 0 THEN
    RETURN NULL;
  END IF;
  IF v_faltas IS NULL THEN
    SET v_faltas = 0;
  END IF;
  RETURN ROUND((v_total - v_faltas) / v_total * 100, 2);
END //

-- fn_situacao(p_id_matricula): RN02+RN03+RN04
-- NULL em N1/N2 => 'Cursando'; freq<75 => 'Reprovado por Falta' (prioridade);
-- exame NULL: >=7 Aprovado, >=4 Em exame, senão Reprovado por Nota;
-- exame NOT NULL: media_final>=5 Aprovado senão Reprovado por Nota.
DROP FUNCTION IF EXISTS fn_situacao //
CREATE FUNCTION fn_situacao(p_id_matricula INT)
RETURNS VARCHAR(30)
DETERMINISTIC READS SQL DATA
BEGIN
  DECLARE v_n1 DECIMAL(4,2);
  DECLARE v_n2 DECIMAL(4,2);
  DECLARE v_exame DECIMAL(4,2);
  DECLARE v_faltas INT;
  DECLARE v_total INT;
  DECLARE v_freq DECIMAL(5,2);
  DECLARE v_media DECIMAL(4,2);

  SELECT m.n1, m.n2, m.exame, m.faltas, t.total_aulas
    INTO v_n1, v_n2, v_exame, v_faltas, v_total
    FROM matricula m
    JOIN turma t ON t.id_turma = m.id_turma
   WHERE m.id_matricula = p_id_matricula;

  IF v_n1 IS NULL OR v_n2 IS NULL THEN
    RETURN 'Cursando';
  END IF;
  IF v_total IS NULL OR v_total = 0 THEN
    RETURN 'Cursando';
  END IF;
  IF v_faltas IS NULL THEN
    SET v_faltas = 0;
  END IF;
  SET v_freq = (v_total - v_faltas) / v_total * 100;

  IF v_freq < 75 THEN
    RETURN 'Reprovado por Falta';
  END IF;

  IF v_exame IS NULL THEN
    SET v_media = (v_n1 + v_n2) / 2;
    IF v_media >= 7 THEN
      RETURN 'Aprovado';
    ELSEIF v_media >= 4 THEN
      RETURN 'Em exame';
    ELSE
      RETURN 'Reprovado por Nota';
    END IF;
  ELSE
    SET v_media = ((v_n1 + v_n2) / 2 + v_exame) / 2;
    IF v_media >= 5 THEN
      RETURN 'Aprovado';
    ELSE
      RETURN 'Reprovado por Nota';
    END IF;
  END IF;
END //

-- fn_cr_aluno(p_id_aluno): média ponderada por carga_horaria (só Aprovados)
-- Sem matrícula aprovada => NULL. Opcional (usada em relatórios).
DROP FUNCTION IF EXISTS fn_cr_aluno //
CREATE FUNCTION fn_cr_aluno(p_id_aluno INT)
RETURNS DECIMAL(4,2)
DETERMINISTIC READS SQL DATA
BEGIN
  DECLARE v_cr DECIMAL(4,2) DEFAULT NULL;
  SELECT ROUND(SUM(m.media_final * d.carga_horaria) / SUM(d.carga_horaria), 2)
    INTO v_cr
    FROM matricula m
    JOIN turma t ON t.id_turma = m.id_turma
    JOIN disciplina d ON d.id_disciplina = t.id_disciplina
   WHERE m.id_aluno = p_id_aluno
     AND m.situacao = 'Aprovado'
     AND m.media_final IS NOT NULL;
  RETURN v_cr;
END //

DELIMITER ;

-- ============================================================================
-- 2) VIEWS
-- ============================================================================

-- vw_boletim: um registro por matrícula com dados de aluno/disciplina/turma
CREATE OR REPLACE VIEW vw_boletim AS
SELECT
  m.id_matricula,
  m.id_aluno,
  a.ra,
  a.nome              AS aluno,
  a.status            AS status_aluno,
  d.id_disciplina,
  d.nome              AS disciplina,
  d.carga_horaria,
  t.id_turma,
  t.semestre,
  p.nome              AS professor,
  m.n1,
  m.n2,
  m.exame,
  m.media_final,
  m.faltas,
  m.situacao
FROM matricula m
JOIN aluno a       ON a.id_aluno = m.id_aluno
JOIN turma t       ON t.id_turma = m.id_turma
JOIN disciplina d  ON d.id_disciplina = t.id_disciplina
LEFT JOIN professor p ON p.id_professor = t.id_professor;

-- vw_turmas_lotacao: vagas totais, matriculados, restantes, % ocupação
CREATE OR REPLACE VIEW vw_turmas_lotacao AS
SELECT
  t.id_turma,
  d.nome  AS disciplina,
  pr.nome AS professor,
  t.semestre,
  t.vagas AS vagas_totais,
  COUNT(m.id_matricula) AS matriculados,
  (t.vagas - COUNT(m.id_matricula)) AS vagas_restantes,
  ROUND(COUNT(m.id_matricula) / t.vagas * 100, 2) AS pct_ocupacao
FROM turma t
JOIN disciplina d  ON d.id_disciplina = t.id_disciplina
LEFT JOIN professor pr ON pr.id_professor = t.id_professor
LEFT JOIN matricula m  ON m.id_turma = t.id_turma
GROUP BY t.id_turma, d.nome, pr.nome, t.semestre, t.vagas;

-- vw_desempenho_turma: agregado por turma (médias e percentuais)
CREATE OR REPLACE VIEW vw_desempenho_turma AS
SELECT
  t.id_turma,
  d.nome     AS disciplina,
  t.semestre,
  COUNT(m.id_matricula) AS total_alunos,
  ROUND(AVG(m.media_final), 2) AS media_global,
  MAX(m.media_final) AS maior_nota,
  MIN(m.media_final) AS menor_nota,
  ROUND(SUM(CASE WHEN m.situacao = 'Aprovado' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(m.id_matricula), 0) * 100, 2) AS pct_aprovados,
  ROUND(SUM(CASE WHEN m.situacao LIKE 'Reprovado%' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(m.id_matricula), 0) * 100, 2) AS pct_reprovados
FROM turma t
JOIN disciplina d ON d.id_disciplina = t.id_disciplina
LEFT JOIN matricula m ON m.id_turma = t.id_turma
GROUP BY t.id_turma, d.nome, t.semestre;

-- ============================================================================
-- 3) PROCEDURES
-- ============================================================================

DELIMITER //

-- sp_LoginUsuario: autenticação simples por login + senha_hash (SHA2-256 hex)
DROP PROCEDURE IF EXISTS sp_LoginUsuario //
CREATE PROCEDURE sp_LoginUsuario(
  IN p_login VARCHAR(50),
  IN p_senha_hash CHAR(64)
)
BEGIN
  SELECT id_usuario, nome, email, perfil
    FROM usuario
   WHERE login = p_login
     AND senha_hash = p_senha_hash;
END //

-- sp_matricular_aluno: valida RN09 (status), RN05 (vagas), RN06 (pré-requisito)
DROP PROCEDURE IF EXISTS sp_matricular_aluno //
CREATE PROCEDURE sp_matricular_aluno(
  IN p_id_aluno INT,
  IN p_id_turma INT,
  IN p_id_usuario INT
)
BEGIN
  DECLARE v_status VARCHAR(20) DEFAULT NULL;
  DECLARE v_vagas INT DEFAULT NULL;
  DECLARE v_count INT DEFAULT 0;
  DECLARE v_id_disciplina INT DEFAULT NULL;
  DECLARE v_missing INT DEFAULT 0;
  DECLARE v_dup INT DEFAULT 0;
  DECLARE v_aluno_existe INT DEFAULT 0;
  DECLARE v_turma_existe INT DEFAULT 0;

  SELECT COUNT(*) INTO v_aluno_existe FROM aluno WHERE id_aluno = p_id_aluno;
  IF v_aluno_existe = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Aluno não encontrado.';
  END IF;

  SELECT COUNT(*) INTO v_turma_existe FROM turma WHERE id_turma = p_id_turma;
  IF v_turma_existe = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Turma não encontrada.';
  END IF;

  -- RN09: Trancado/Formado bloqueia
  SELECT status INTO v_status FROM aluno WHERE id_aluno = p_id_aluno;
  IF v_status <> 'Ativo' THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Matrícula bloqueada: aluno com status Trancado/Formado (RN09).';
  END IF;

  -- Duplicada (UNIQUE id_aluno,id_turma)
  SELECT COUNT(*) INTO v_dup FROM matricula
   WHERE id_aluno = p_id_aluno AND id_turma = p_id_turma;
  IF v_dup > 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Aluno já matriculado nesta turma.';
  END IF;

  -- RN05: vagas
  SELECT vagas, id_disciplina INTO v_vagas, v_id_disciplina
    FROM turma WHERE id_turma = p_id_turma;
  SELECT COUNT(*) INTO v_count FROM matricula WHERE id_turma = p_id_turma;
  IF v_count >= v_vagas THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Turma lotada: sem vagas disponíveis (RN05).';
  END IF;

  -- RN06: pré-requisito — exige 'Aprovado' em TODOS os requisitos
  SELECT COUNT(*) INTO v_missing
    FROM pre_requisito pr
   WHERE pr.id_disciplina = v_id_disciplina
     AND NOT EXISTS (
       SELECT 1
         FROM matricula m
         JOIN turma t2 ON t2.id_turma = m.id_turma
        WHERE m.id_aluno = p_id_aluno
          AND t2.id_disciplina = pr.id_disciplina_requisito
          AND m.situacao = 'Aprovado'
     );
  IF v_missing > 0 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Pré-requisito não cumprido: aluno sem aprovação nas disciplinas exigidas (RN06).';
  END IF;

  INSERT INTO matricula (id_aluno, id_turma, id_usuario)
  VALUES (p_id_aluno, p_id_turma, p_id_usuario);
END //

-- sp_lancar_notas: atualiza N1/N2/faltas (trigger recalcula media/situacao)
DROP PROCEDURE IF EXISTS sp_lancar_notas //
CREATE PROCEDURE sp_lancar_notas(
  IN p_id_matricula INT,
  IN p_n1 DECIMAL(4,2),
  IN p_n2 DECIMAL(4,2),
  IN p_faltas INT,
  IN p_id_usuario INT
)
BEGIN
  DECLARE v_existe INT DEFAULT 0;
  SELECT COUNT(*) INTO v_existe FROM matricula WHERE id_matricula = p_id_matricula;
  IF v_existe = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Matrícula não encontrada.';
  END IF;
  UPDATE matricula
     SET n1 = p_n1,
         n2 = p_n2,
         faltas = p_faltas,
         id_usuario = p_id_usuario
   WHERE id_matricula = p_id_matricula;
END //

-- sp_lancar_exame: só permite se situacao = 'Em exame'
DROP PROCEDURE IF EXISTS sp_lancar_exame //
CREATE PROCEDURE sp_lancar_exame(
  IN p_id_matricula INT,
  IN p_exame DECIMAL(4,2),
  IN p_id_usuario INT
)
BEGIN
  DECLARE v_sit VARCHAR(30) DEFAULT NULL;
  DECLARE v_existe INT DEFAULT 0;
  SELECT COUNT(*) INTO v_existe FROM matricula WHERE id_matricula = p_id_matricula;
  IF v_existe = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Matrícula não encontrada.';
  END IF;
  SELECT situacao INTO v_sit FROM matricula WHERE id_matricula = p_id_matricula;
  IF v_sit <> 'Em exame' THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Exame só pode ser lançado para matrícula em exame.';
  END IF;
  UPDATE matricula
     SET exame = p_exame,
         id_usuario = p_id_usuario
   WHERE id_matricula = p_id_matricula;
END //

-- sp_historico_aluno: boletim completo ordenado por semestre
DROP PROCEDURE IF EXISTS sp_historico_aluno //
CREATE PROCEDURE sp_historico_aluno(IN p_id_aluno INT)
BEGIN
  SELECT
    t.semestre,
    d.nome AS disciplina,
    d.carga_horaria,
    m.n1, m.n2, m.exame, m.media_final, m.faltas, m.situacao
  FROM matricula m
  JOIN turma t      ON t.id_turma = m.id_turma
  JOIN disciplina d ON d.id_disciplina = t.id_disciplina
  WHERE m.id_aluno = p_id_aluno
  ORDER BY t.semestre, d.nome;
END //

-- sp_fechar_semestre: CURSOR + TRANSACTION, só Coordenador
DROP PROCEDURE IF EXISTS sp_fechar_semestre //
CREATE PROCEDURE sp_fechar_semestre(
  IN p_semestre VARCHAR(10),
  IN p_id_usuario INT
)
BEGIN
  DECLARE v_perfil VARCHAR(20) DEFAULT NULL;
  DECLARE v_done INT DEFAULT 0;
  DECLARE v_id_mat INT DEFAULT NULL;
  DECLARE c_mat CURSOR FOR
    SELECT m.id_matricula
      FROM matricula m
      JOIN turma t ON t.id_turma = m.id_turma
     WHERE t.semestre = p_semestre;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  SELECT perfil INTO v_perfil FROM usuario WHERE id_usuario = p_id_usuario;
  IF v_perfil IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Usuário operador não encontrado.';
  END IF;
  IF v_perfil <> 'Coordenador' THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Apenas Coordenador pode fechar o semestre.';
  END IF;

  START TRANSACTION;
  OPEN c_mat;
  loop_mat: LOOP
    FETCH c_mat INTO v_id_mat;
    IF v_done = 1 THEN
      LEAVE loop_mat;
    END IF;
    -- O UPDATE dispara trg_atualiza_situacao, que recalcula
    -- media_final/situacao a partir de NEW + total_aulas.
    UPDATE matricula SET id_usuario = p_id_usuario
     WHERE id_matricula = v_id_mat;
  END LOOP;
  CLOSE c_mat;
  COMMIT;
END //

DELIMITER ;

-- ============================================================================
-- 4) TRIGGERS
-- ============================================================================

DELIMITER //

-- trg_valida_pr_diferente: impede auto-requisito (MySQL usaria CHECK, MariaDB 1901 rejeita).
-- Vale para INSERT e UPDATE em pre_requisito.
DROP TRIGGER IF EXISTS trg_valida_pr_diferente_ins //
CREATE TRIGGER trg_valida_pr_diferente_ins
BEFORE INSERT ON pre_requisito
FOR EACH ROW
BEGIN
  IF NEW.id_disciplina = NEW.id_disciplina_requisito THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Pre-requisito invalido: disciplina nao pode exigir ela mesma.';
  END IF;
END //

DROP TRIGGER IF EXISTS trg_valida_pr_diferente_upd //
CREATE TRIGGER trg_valida_pr_diferente_upd
BEFORE UPDATE ON pre_requisito
FOR EACH ROW
BEGIN
  IF NEW.id_disciplina = NEW.id_disciplina_requisito THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Pre-requisito invalido: disciplina nao pode exigir ela mesma.';
  END IF;
END //

-- trg_valida_vagas: BEFORE INSERT — impede overbooking (RN05)
DROP TRIGGER IF EXISTS trg_valida_vagas //
CREATE TRIGGER trg_valida_vagas
BEFORE INSERT ON matricula
FOR EACH ROW
BEGIN
  DECLARE v_vagas INT DEFAULT NULL;
  DECLARE v_count INT DEFAULT 0;
  SELECT vagas INTO v_vagas FROM turma WHERE id_turma = NEW.id_turma;
  IF v_vagas IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Turma não encontrada (trg_valida_vagas).';
  END IF;
  SELECT COUNT(*) INTO v_count FROM matricula WHERE id_turma = NEW.id_turma;
  IF v_count >= v_vagas THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Turma lotada: sem vagas disponíveis (RN05).';
  END IF;
END //

-- trg_atualiza_situacao: BEFORE UPDATE — recalcula media_final/situacao (RN01-RN04)
-- Lógica inline com NEW + total_aulas (não chama fn_situacao, que leria a linha antiga).
DROP TRIGGER IF EXISTS trg_atualiza_situacao //
CREATE TRIGGER trg_atualiza_situacao
BEFORE UPDATE ON matricula
FOR EACH ROW
BEGIN
  DECLARE v_total INT DEFAULT NULL;
  DECLARE v_freq DECIMAL(5,2) DEFAULT NULL;
  DECLARE v_faltas INT DEFAULT 0;
  SELECT total_aulas INTO v_total FROM turma WHERE id_turma = NEW.id_turma;

  -- RN01 / RN03 (base): media via função pura (sem acesso a tabelas)
  SET NEW.media_final = fn_calcular_media(NEW.n1, NEW.n2, NEW.exame);

  IF NEW.n1 IS NULL OR NEW.n2 IS NULL THEN
    SET NEW.situacao = 'Cursando';
  ELSE
    SET v_faltas = COALESCE(NEW.faltas, 0);
    IF v_total IS NULL OR v_total = 0 THEN
      SET NEW.situacao = 'Cursando';
    ELSE
      SET v_freq = (v_total - v_faltas) / v_total * 100;
      -- RN04 tem prioridade sobre a nota
      IF v_freq < 75 THEN
        SET NEW.situacao = 'Reprovado por Falta';
      ELSEIF NEW.exame IS NULL THEN
        -- RN02
        IF (NEW.n1 + NEW.n2) / 2 >= 7 THEN
          SET NEW.situacao = 'Aprovado';
        ELSEIF (NEW.n1 + NEW.n2) / 2 >= 4 THEN
          SET NEW.situacao = 'Em exame';
        ELSE
          SET NEW.situacao = 'Reprovado por Nota';
        END IF;
      ELSE
        -- RN03
        IF (((NEW.n1 + NEW.n2) / 2 + NEW.exame) / 2) >= 5 THEN
          SET NEW.situacao = 'Aprovado';
        ELSE
          SET NEW.situacao = 'Reprovado por Nota';
        END IF;
      END IF;
    END IF;
  END IF;
END //

-- trg_atualiza_situacao_ins: BEFORE INSERT — mesma regra para carga inicial
-- (mantém consistência quando o INSERT já traz n1/n2; idêntica ao BEFORE UPDATE)
DROP TRIGGER IF EXISTS trg_atualiza_situacao_ins //
CREATE TRIGGER trg_atualiza_situacao_ins
BEFORE INSERT ON matricula
FOR EACH ROW
BEGIN
  DECLARE v_total INT DEFAULT NULL;
  DECLARE v_freq DECIMAL(5,2) DEFAULT NULL;
  DECLARE v_faltas INT DEFAULT 0;
  SELECT total_aulas INTO v_total FROM turma WHERE id_turma = NEW.id_turma;

  SET NEW.media_final = fn_calcular_media(NEW.n1, NEW.n2, NEW.exame);

  IF NEW.n1 IS NULL OR NEW.n2 IS NULL THEN
    SET NEW.situacao = 'Cursando';
  ELSE
    SET v_faltas = COALESCE(NEW.faltas, 0);
    IF v_total IS NULL OR v_total = 0 THEN
      SET NEW.situacao = 'Cursando';
    ELSE
      SET v_freq = (v_total - v_faltas) / v_total * 100;
      IF v_freq < 75 THEN
        SET NEW.situacao = 'Reprovado por Falta';
      ELSEIF NEW.exame IS NULL THEN
        IF (NEW.n1 + NEW.n2) / 2 >= 7 THEN
          SET NEW.situacao = 'Aprovado';
        ELSEIF (NEW.n1 + NEW.n2) / 2 >= 4 THEN
          SET NEW.situacao = 'Em exame';
        ELSE
          SET NEW.situacao = 'Reprovado por Nota';
        END IF;
      ELSE
        IF (((NEW.n1 + NEW.n2) / 2 + NEW.exame) / 2) >= 5 THEN
          SET NEW.situacao = 'Aprovado';
        ELSE
          SET NEW.situacao = 'Reprovado por Nota';
        END IF;
      END IF;
    END IF;
  END IF;
END //

-- trg_auditoria_nota: AFTER UPDATE — RN08, um INSERT por campo alterado
DROP TRIGGER IF EXISTS trg_auditoria_nota //
CREATE TRIGGER trg_auditoria_nota
AFTER UPDATE ON matricula
FOR EACH ROW
BEGIN
  DECLARE v_usuario VARCHAR(100) DEFAULT NULL;
  IF NEW.id_usuario IS NOT NULL THEN
    SELECT login INTO v_usuario FROM usuario WHERE id_usuario = NEW.id_usuario;
  END IF;
  IF v_usuario IS NULL THEN
    SET v_usuario = USER();
  END IF;

  IF NOT (OLD.n1 <=> NEW.n1) THEN
    INSERT INTO log_nota (id_matricula, campo, valor_antigo, valor_novo, usuario)
    VALUES (NEW.id_matricula, 'n1', CAST(OLD.n1 AS CHAR), CAST(NEW.n1 AS CHAR), v_usuario);
  END IF;
  IF NOT (OLD.n2 <=> NEW.n2) THEN
    INSERT INTO log_nota (id_matricula, campo, valor_antigo, valor_novo, usuario)
    VALUES (NEW.id_matricula, 'n2', CAST(OLD.n2 AS CHAR), CAST(NEW.n2 AS CHAR), v_usuario);
  END IF;
  IF NOT (OLD.exame <=> NEW.exame) THEN
    INSERT INTO log_nota (id_matricula, campo, valor_antigo, valor_novo, usuario)
    VALUES (NEW.id_matricula, 'exame', CAST(OLD.exame AS CHAR), CAST(NEW.exame AS CHAR), v_usuario);
  END IF;
  IF NOT (OLD.faltas <=> NEW.faltas) THEN
    INSERT INTO log_nota (id_matricula, campo, valor_antigo, valor_novo, usuario)
    VALUES (NEW.id_matricula, 'faltas', CAST(OLD.faltas AS CHAR), CAST(NEW.faltas AS CHAR), v_usuario);
  END IF;
END //

DELIMITER ;
