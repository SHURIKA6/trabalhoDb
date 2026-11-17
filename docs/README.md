# Documentação — como gerar o PDF do relatório

Fonte oficial: `docs/relatorio.md` (completo, em português).
Versão de leitura/impressão: `docs/relatorio.html`.
Roteiro da apresentação: `slides/apresentacao.md` + deck `slides/apresentacao.html`.

## Opção 1 — VSCode (recomendada)

1. Abra `docs/relatorio.md`.
2. `Ctrl+Shift+V` para o preview (o bloco Mermaid exige a extensão
   *Markdown Preview Mermaid Support*).
3. Nos `...` do preview: **Print to PDF** (ou instale a extensão
   *Markdown PDF* e use *Export to PDF*).

## Opção 2 — Typora

1. Abra `docs/relatorio.md`.
2. *File > Export > PDF* (margens: 2 cm; fonte: 11–12 pt; incluir sumário).

## Opção 3 — Pandoc + LaTeX

```bash
pandoc docs/relatorio.md -o docs/relatorio.pdf \
  --pdf-engine=xelatex -V lang=pt-BR --toc --number-sections
```

Sem LaTeX instalado, gere HTML e imprima pelo navegador:

```bash
pandoc docs/relatorio.md -o docs/relatorio.html --standalone --toc -V lang=pt-BR
```

## Opção 4 — Navegador (sem instalar nada)

1. Abra `docs/relatorio.html` no navegador.
2. *Imprimir > Salvar como PDF* (ativar "gráficos de fundo" para manter cores
   das tabelas).

## Checklist pré-entrega

- [x] Substituir `Nome 1..4` por nomes em `docs/relatorio.md`,
      `docs/divisao_trabalho.md` e `slides/apresentacao.md` (prof. Francisco
      Sanches Banhos Filho; matrícula de Danieli preenchida — faltam as dos
      demais integrantes).
- [ ] Capturar os 8 prints em `app/screenshots/` (roteiro em
      `app/screenshots/README.md`).
- [ ] Executar `sql/01_schema.sql` → `02_objetos.sql` → `03_dados.sql` →
      `05_sp_apoio.sql` → `04_testes.sql` (por blocos) e conferir 9/9 testes.
- [ ] Regenerar `docs/relatorio.html` (está desatualizado após revisão de 16/11)
      e gerar `docs/relatorio.pdf` por uma das opções acima.
