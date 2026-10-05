# Changelog

## 1.0.0 — 2026-10-05

- Primeira versão pública do plugin comunitário, alinhada ao
  `version` do `orca-plugin.json`.
- Tag `1.0.0` (e `v1.0.0`) apontando para o conteúdo real do pack:
  antes a tag `v1.0.0` era o stub do fork (2 arquivos, 863 B).
- Instalação pinada: `https://github.com/Danil0ws/orca-plugin-pt-br.git#1.0.0`.

## 1.4.220 — 2026-10-04

- Fork comunitário do stablyai/orca-portuguese: novo id `orca-plugin-pt-br`,
  `engines >=1.4.169` (zona protegida só é segura a partir da 1.4.169).
- Pipeline por lanes: `extract.py` (catálogo da tag + zona protegida por
  interseção COMPAT×instalada), `build.py` (validações, glossário,
  `--pending <lane>`), `test_build.py` (9 regressões).
- Seed dos dicionários a partir do catálogo upstream: 12.685/15.007 (84%),
  12.148 traduções migradas idênticas, 375 chaves obsoletas descartadas,
  1 bug de placeholder corrigido (`screenshotsHint`).
- `GLOSSARY.md` + `tools/glossary.json` (14 avisos ativos = backlog de
  terminologia) + `UNTRANSLATED.md`.
- README e CONTRIBUTING da versão comunitária; LICENSE (MIT).
