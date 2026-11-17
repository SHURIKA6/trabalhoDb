# Como rodar o SGA do zero (banco → login)

Guia para qualquer computador com Python e MySQL 8.0.

## 1. Pré-requisitos

- **Python 3.10+** com Tkinter (vem junto na instalação padrão do Windows;
  no Linux: `sudo apt install python3 python3-venv python3-tk`)
- **MySQL 8.0+** rodando (MySQL Installer no Windows, `mysql-server` no Linux)
- Arquivos do projeto (`trabalhoDb/`)

## 2. Iniciar o MySQL

- **Windows:** abra `Services` e confirme que o serviço `MySQL80` está em execução.
  (O MySQL Installer / Workbench já deixam isso pronto.)
- **Linux:** `sudo systemctl start mysql` (ou `mysqld`, conforme a distro).

## 3. Criar o banco `sga_fbi` (a ordem importa)

### Opção A — MySQL Workbench

1. Conecte-se com o `root`.
2. Abra e execute (`Ctrl+Shift+Enter`) cada arquivo **nesta ordem**:
   1. `sql/01_schema.sql` — apaga e recria o banco do zero
   2. `sql/02_objetos.sql` — funções, views, procedures, triggers
   3. `sql/03_dados.sql` — carga inicial (usuários, cursos, alunos, matrículas)
   4. `sql/05_sp_apoio.sql` — procedures de apoio ao app (sempre por último)
3. O `sql/04_testes.sql` **não** entra na sequência: execute **por blocos**
   no Workbench (ver `sql/README.md` — os `CALL` de erro dos testes 2–5 ficam
   comentados de propósito; rode cada um isoladamente para ver o `SIGNAL`).

### Opção B — terminal

```bash
cd trabalhoDb
mysql -u root -p < sql/01_schema.sql
mysql -u root -p < sql/02_objetos.sql
mysql -u root -p < sql/03_dados.sql
mysql -u root -p < sql/05_sp_apoio.sql
```
.venv/bin/python app/main.py
## 4. Verificar se o banco está certo

```sql
SHOW TABLES;                                  -- 9 tabelas
SHOW FULL TABLES WHERE Table_type = 'VIEW';   -- 5 views
CALL sp_LoginUsuario('coord1', SHA2('senha123', 256));  -- deve retornar 1 linha
```

Esperado: tabelas `aluno`, `curso`, `disciplina`, `log_nota`, `matricula`,
`pre_requisito`, `professor`, `turma`, `usuario`; views `vw_alunos`,
`vw_boletim`, `vw_desempenho_turma`, `vw_log_nota`, `vw_turmas_lotacao`.

## 5. Preparar o app Python (uma vez só)

```bash
cd trabalhoDb
python -m venv .venv
# Windows:
.venv\Scripts\pip install -r requirements.txt
# Linux/macOS:
.venv/bin/pip install -r requirements.txt
```

Copie o arquivo de configuração e ajuste usuário/senha do **seu** MySQL:

```bash
# Windows:  copy .env.example .env
# Linux:    cp .env.example .env
```

Conteúdo do `.env` (exemplo com `root`; troque pela sua senha):

```
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha_do_mysql
MYSQL_DB=sga_fbi
```

> Prefira criar um usuário só para o app em vez de usar o `root`:
>
> ```sql
> CREATE USER IF NOT EXISTS 'sga_app'@'localhost' IDENTIFIED BY 'troque_aqui';
> GRANT ALL PRIVILEGES ON sga_fbi.* TO 'sga_app'@'localhost';
> FLUSH PRIVILEGES;
> ```
>
> e use `MYSQL_USER=sga_app` / `MYSQL_PASSWORD=troque_aqui` no `.env`.

## 6. Rodar o sistema

```bash
cd trabalhoDb
# Windows:
.venv\Scripts\python app/main.py
# Linux/macOS:
.venv/bin/python app/main.py
```

Abre a janela **SGA — Faculdade do Bug Infinito** na tela de login.

> Use sempre o Python do `.venv`: o Python do sistema **não** tem
> `mysql-connector-python` nem `python-dotenv`, então o app nem abre por ele.

Teste de permissões (sem banco, opcional):

```bash
# Windows: .venv\Scripts\python app/test_permissoes.py
# Linux:   .venv/bin/python app/test_permissoes.py
# esperado: RESULTADO: PASS
```

## 7. Logins

Senhas em texto puro existem só aqui e em `sql/03_dados.sql`
(no banco ficam como `SHA2(senha, 256)`):

| login | senha    | perfil      | nome             |
|-------|----------|-------------|------------------|
| coord1 | senha123 | Coordenador | Ana Coordenadora |
| coord2 | coord123 | Coordenador | Bruno Chefia     |
| sec1   | sec123   | Secretario  | Carla Secretaria |
| sec2   | sec123   | Secretario  | Diego Atendente  |
| sec3   | sec123   | Secretario  | Elisa Balcão     |

Permissões na GUI: **Secretario** vê Alunos, Matrículas e relatórios simples
(Boletim, Histórico, Lotação). **Coordenador** vê tudo + Notas/Exame,
Desempenho, Faturamento, Fechar Semestre e Auditoria.

## 8. Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| `Não foi possível conectar ao MySQL...` ao logar | MySQL parado ou host/porta errados | inicie o serviço MySQL (passo 2) e confira `MYSQL_HOST`/`MYSQL_PORT` no `.env` (padrão: `127.0.0.1`/`3306`) |
| `Acesso ao banco negado` | usuário/senha errados no `.env` | confira `MYSQL_USER`/`MYSQL_PASSWORD`; teste o mesmo login no Workbench |
| `ModuleNotFoundError: No module named 'mysql'` | rodou com o Python do sistema | use o Python do `.venv` (passo 6) |
| `Unknown database 'sga_fbi'` | pulou o passo 3 | execute os scripts SQL na ordem indicada |
| Login `sec1`/`senha123` inválido | senha incorreta | secretário usa `sec123` (tabela do passo 7) |
