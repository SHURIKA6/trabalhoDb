# SGA — Faculdade do Bug Infinito (Interface Tkinter)

Aplicação desktop em **Python 3.10+ + Tkinter (stdlib)** + `mysql-connector-python`.
Toda comunicação com o MySQL é feita **exclusivamente** via `CALL sp_*` e
`SELECT * FROM vw_*` (ver `app/db.py`). Não há query livre nem acesso direto
a tabelas pelo app.

## Estrutura

```
trabalhoDb/
├── app/
│   ├── main.py            # ponto de entrada (`python app/main.py`)
│   ├── config.py          # lê MYSQL_* do .env
│   ├── db.py              # ÚNICO acesso ao banco: call_procedure + select_view
│   ├── auth.py            # SHA-256 + CALL sp_LoginUsuario
│   ├── permissoes.py      # regras Coordenador x Secretario (+ teste)
│   ├── ui_login.py        # tela 1 — login
│   ├── ui_main.py         # tela 2 — menu com controle de perfil
│   ├── ui_theme.py        # tema visual central (cores/fontes/estilos ttk)
│   ├── ui_alunos.py       # tela 3 — CRUD alunos (sp_criar/editar/excluir/listar)
│   ├── ui_matriculas.py   # tela 4 — lotação (vw) + sp_matricular_aluno
│   ├── ui_notas.py        # tela 5 — só Coordenador (sp_lancar_notas/exame)
│   ├── ui_relatorios.py   # tela 6 — boletim/histórico/lotação/desempenho/
│   │                      #   faturamento/fechar semestre/log (coords p/ sensíveis)
│   └── test_permissoes.py # teste de perfil sem banco
├── sql/
│   └── 05_sp_apoio.sql    # SPs complementares (CRUD aluno, listas, log)
├── requirements.txt
├── .env.example
└── screenshots/           # prints das telas (ver pasta)
```

O banco (`sga_fbi`, tabelas, views `vw_boletim`, `vw_turmas_lotacao`,
`vw_desempenho_turma` e procedures `sp_LoginUsuario`, `sp_matricular_aluno`,
`sp_lancar_notas`, `sp_lancar_exame`, `sp_historico_aluno`,
`sp_fechar_semestre`) é criado por outro agente em `sql/01..04`.

## Instalação

```bash
pip install -r requirements.txt
cp .env.example .env   # edite usuario/senha
```

## Criação do banco (ordem)

```bash
mysql -u root -p < sql/01_schema.sql
mysql -u root -p < sql/02_objetos.sql
mysql -u root -p < sql/03_dados.sql
mysql -u root -p < sql/05_sp_apoio.sql
# sql/04_testes.sql: execute por blocos no Workbench (ver sql/README.md)
```

## Execução

```bash
python app/main.py
# ou, dentro de app/:  python main.py
```

## Teste de permissões (sem banco)

```bash
python app/test_permissoes.py
# esperado: RESULTADO: PASS
```

## Logins de teste

Documentado a partir de `sql/03_dados.sql` (senhas gravadas como
`SHA2('senha123', 256)` = `hashlib.sha256(b"senha123").hexdigest()`):

| login   | senha   | perfil      |
|---------|---------|-------------|
| coord1  | senha123| Coordenador |
| sec1    | senha123| Secretario  |

Se `03_dados.sql` usar outros logins, use os de lá — o app chama
`sp_LoginUsuario(login, sha256_hex)` e funciona com qualquer usuário da tabela.

## Permissões na GUI

- **Secretario:** Alunos, Matrículas, Relatórios (Boletim, Histórico, Lotação).
  Não vê botões de Notas, Desempenho, Faturamento, Fechar Semestre, Auditoria.
- **Coordenador:** tudo + lançar notas/exame, desempenho, faturamento por curso,
  fechar semestre (`sp_fechar_semestre`), auditoria (`sp_listar_log`).

## Conformidade com o edital

- Sem PHP; sem `SELECT/INSERT/UPDATE/DELETE` em tabelas pelo app.
- `app/db.py` expõe só `call_procedure("sp_*")` e `select_view("vw_*")`,
  com validação por regex e erro amigável para `SIGNAL 1644 / SQLSTATE 45000`
  (turma lotada, sem pré-requisito, aluno trancado, exame indevido).
- Cadastros de aluno usam `sp_criar_aluno`, `sp_editar_aluno`,
  `sp_excluir_aluno`, `sp_listar_alunos` (este arquivo complementar) —
  nenhuma escrita direta.

## Screenshots

Veja `screenshots/README.md` — rode o app e anexe os prints das 7 telas.
