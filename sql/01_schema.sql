-- ============================================================================
-- SGA-FBI | sql/01_schema.sql
-- Database: sga_fbi | MySQL 8.0+ / Workbench compatível
-- Engine: InnoDB | Charset: utf8mb4
-- Ordem de execução: 1º (depois: 02_objetos.sql, 03_dados.sql, 04_testes.sql)
-- ============================================================================

DROP DATABASE IF EXISTS sga_fbi;
CREATE DATABASE sga_fbi
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE sga_fbi;

-- ----------------------------------------------------------------------------
-- 1. usuario
-- ----------------------------------------------------------------------------
CREATE TABLE usuario (
  id_usuario  INT AUTO_INCREMENT PRIMARY KEY,
  nome        VARCHAR(100) NOT NULL,
  cpf         CHAR(14) UNIQUE,
  email       VARCHAR(100) UNIQUE,
  login       VARCHAR(50) UNIQUE NOT NULL,
  senha_hash  CHAR(64) NOT NULL,
  perfil      ENUM('Secretario','Coordenador') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 2. curso
-- ----------------------------------------------------------------------------
CREATE TABLE curso (
  id_curso             INT AUTO_INCREMENT PRIMARY KEY,
  nome                 VARCHAR(100) NOT NULL,
  carga_horaria_total  INT,
  turno                ENUM('Matutino','Vespertino','Noturno')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 3. disciplina
-- ----------------------------------------------------------------------------
CREATE TABLE disciplina (
  id_disciplina  INT AUTO_INCREMENT PRIMARY KEY,
  id_curso       INT NOT NULL,
  nome           VARCHAR(100) NOT NULL,
  carga_horaria  INT NOT NULL,
  periodo        INT,
  CONSTRAINT fk_disciplina_curso FOREIGN KEY (id_curso)
    REFERENCES curso (id_curso)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_disciplina_ch CHECK (carga_horaria > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE INDEX idx_disciplina_curso ON disciplina (id_curso);

-- ----------------------------------------------------------------------------
-- 4. professor
-- ----------------------------------------------------------------------------
CREATE TABLE professor (
  id_professor   INT AUTO_INCREMENT PRIMARY KEY,
  nome           VARCHAR(100),
  cpf            VARCHAR(14) UNIQUE,
  email          VARCHAR(100) UNIQUE,
  titulacao      VARCHAR(50),
  data_admissao  DATE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 5. aluno
-- ----------------------------------------------------------------------------
CREATE TABLE aluno (
  id_aluno        INT AUTO_INCREMENT PRIMARY KEY,
  ra              VARCHAR(20) UNIQUE NOT NULL,
  nome            VARCHAR(100) NOT NULL,
  cpf             VARCHAR(14) UNIQUE,
  email           VARCHAR(100),
  data_nascimento DATE,
  id_curso        INT,
  status          ENUM('Ativo','Trancado','Formado') NOT NULL DEFAULT 'Ativo',
  CONSTRAINT fk_aluno_curso FOREIGN KEY (id_curso)
    REFERENCES curso (id_curso)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE INDEX idx_aluno_curso ON aluno (id_curso);
CREATE INDEX idx_aluno_status ON aluno (status);

-- ----------------------------------------------------------------------------
-- 6. turma
-- ----------------------------------------------------------------------------
CREATE TABLE turma (
  id_turma      INT AUTO_INCREMENT PRIMARY KEY,
  id_disciplina INT NOT NULL,
  id_professor  INT,
  semestre      VARCHAR(10) NOT NULL,
  vagas         INT NOT NULL,
  total_aulas   INT NOT NULL DEFAULT 60,
  CONSTRAINT fk_turma_disciplina FOREIGN KEY (id_disciplina)
    REFERENCES disciplina (id_disciplina)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_turma_professor FOREIGN KEY (id_professor)
    REFERENCES professor (id_professor)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT chk_turma_vagas CHECK (vagas > 0),
  CONSTRAINT chk_turma_total_aulas CHECK (total_aulas > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE INDEX idx_turma_disciplina ON turma (id_disciplina);
CREATE INDEX idx_turma_professor ON turma (id_professor);
CREATE INDEX idx_turma_semestre ON turma (semestre);

-- ----------------------------------------------------------------------------
-- 7. matricula
-- ----------------------------------------------------------------------------
CREATE TABLE matricula (
  id_matricula   INT AUTO_INCREMENT PRIMARY KEY,
  id_aluno       INT NOT NULL,
  id_turma       INT NOT NULL,
  data_matricula DATE NOT NULL DEFAULT (CURDATE()),
  n1             DECIMAL(4,2) NULL,
  n2             DECIMAL(4,2) NULL,
  exame          DECIMAL(4,2) NULL,
  faltas         INT NOT NULL DEFAULT 0,
  media_final    DECIMAL(4,2) NULL,
  situacao       VARCHAR(30) NOT NULL DEFAULT 'Cursando',
  id_usuario     INT NULL,
  CONSTRAINT fk_matricula_aluno FOREIGN KEY (id_aluno)
    REFERENCES aluno (id_aluno)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_matricula_turma FOREIGN KEY (id_turma)
    REFERENCES turma (id_turma)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_matricula_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuario (id_usuario)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT uq_matricula_aluno_turma UNIQUE (id_aluno, id_turma),
  CONSTRAINT chk_matricula_n1 CHECK (n1 IS NULL OR (n1 >= 0 AND n1 <= 10)),
  CONSTRAINT chk_matricula_n2 CHECK (n2 IS NULL OR (n2 >= 0 AND n2 <= 10)),
  CONSTRAINT chk_matricula_exame CHECK (exame IS NULL OR (exame >= 0 AND exame <= 10)),
  CONSTRAINT chk_matricula_faltas CHECK (faltas >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE INDEX idx_matricula_aluno ON matricula (id_aluno);
CREATE INDEX idx_matricula_turma ON matricula (id_turma);
CREATE INDEX idx_matricula_situacao ON matricula (situacao);

-- ----------------------------------------------------------------------------
-- 8. pre_requisito (PK composta)
-- ----------------------------------------------------------------------------
CREATE TABLE pre_requisito (
  id_disciplina            INT NOT NULL,
  id_disciplina_requisito  INT NOT NULL,
  PRIMARY KEY (id_disciplina, id_disciplina_requisito),
  CONSTRAINT fk_pr_disciplina FOREIGN KEY (id_disciplina)
    REFERENCES disciplina (id_disciplina)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_pr_requisito FOREIGN KEY (id_disciplina_requisito)
    REFERENCES disciplina (id_disciplina)
    ON DELETE CASCADE ON UPDATE CASCADE
  -- NOTA: regra id_disciplina <> id_disciplina_requisito enforced via trigger
  -- trg_valida_pr_diferente em 02_objetos.sql (MySQL aceita CHECK, MariaDB 1901 não).
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 9. log_nota (auditoria RN08)
-- ----------------------------------------------------------------------------
CREATE TABLE log_nota (
  id_log       INT AUTO_INCREMENT PRIMARY KEY,
  id_matricula INT NOT NULL,
  campo        VARCHAR(20),
  valor_antigo VARCHAR(20),
  valor_novo   VARCHAR(20),
  usuario      VARCHAR(100),
  data_hora    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_log_matricula FOREIGN KEY (id_matricula)
    REFERENCES matricula (id_matricula)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE INDEX idx_log_matricula ON log_nota (id_matricula);
CREATE INDEX idx_log_data ON log_nota (data_hora);
