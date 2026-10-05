# Changelog

## 1.0.3 — 2026-10-05

- **Lane `system` zerada** (a última): 539 pares novos → dict 536 → 1075.
  - `sem tradução: 0` · `pendências por lane:` vazio · cobertura
    **14.825/15.007 (98%)**.
  - Gate: `test_build.py` 10 casos OK · divergências de placeholder: 0 ·
    avisos de glossário: 0 · `sufixos de plural: 26 descartados · 0
    mantidos`.
  - `precheck_pairs.py` nos 539 pares novos: cobertura, placeholders,
    glossário, colisões entre lanes e formato do dict — 0 problemas.
- `UNTRANSLATED.md`: dívidas abertas e avisos conhecidos encerrados.
- `version` 1.0.2 → 1.0.3; `locales/pt-BR.json` regenerado; instalação
  pinada em `#1.0.3`.

## 1.0.2 — 2026-10-05

- **Backlog de terminologia zerado**: 36 pares corrigidos em 12 dicionários.
  - 14 avisos de glossário → 0: termos `workspace`, `commit` e `worktree`
    que a tradução descartava (ex.: "área de trabalho", "commitar") e 2
    valores trocados em `by-key.json` (`Go to Worktree` ↔
    `Workspace unavailable`).
  - Sufixo de plural inglês removido de 25 chaves (aparecia como
    `etiquetas: 3s`): `sufixos de plural: 26 descartados · 0 mantidos`.
  - Gate: `test_build.py` 10 casos OK · divergências de placeholder: 0 ·
    avisos de glossário: 0.
- `version` 1.0.1 → 1.0.2; `locales/pt-BR.json` regenerado; instalação
  pinada em `#1.0.2`.
- Pendências restantes: `system=553` (539 textos), cobertura 95%.

## 1.0.1 — 2026-10-05

- **Manifesto corrigido** (a 1.0.0 era recusada pela Orca):
  - `publisher`: `Danil0ws` → `danil0ws`. O schema exige kebab-case
    (`^[a-z0-9]+(?:-[a-z0-9]+)*$`) — o erro era
    `publisher: must be kebab-case (a-z, 0-9, dashes) and not a reserved name`.
  - `id`: `orca-plugin-pt-br` → `pt-br`. Identidade com prefixo `orca-` é
    reservada à stablyai: instalando por Git de outro dono a Orca recusa com
    `reserved plugin identity … must resolve to the stablyai organization`
    (mesma regra do `noobitoo.russian`). Chave instalada: **`danil0ws.pt-br`**.
- `version` 1.0.0 → 1.0.1; instalação pinada em `#1.0.1`.
- `tools/test_build.py`: 10º caso valida o manifesto no gate (kebab-case de
  `id`/`publisher`, prefixo reservado, locale) para não regredir.
- Catálogo inalterado: `locales/pt-BR.json` passa no
  `validatePluginLanguagePackCatalog` da Orca 1.4.220.

## 1.0.0 — 2026-10-05

- Primeira versão pública do plugin comunitário, alinhada ao
  `version` do `orca-plugin.json`.
- Tag `1.0.0` (e `v1.0.0`) apontando para o conteúdo real do pack:
  antes a tag `v1.0.0` era o stub do fork (2 arquivos, 863 B).
- Instalação pinada: `https://github.com/Danil0ws/orca-plugin-pt-br.git#1.0.0`.
- Lane `runtime-lib` zerada: 66 pares novos (macOS/permissões, cookies do
  navegador, arquivos soltos/arrastados, `auto.store.*`) → cobertura
  **14272/15007 (95%)**, `sem tradução: 539`, pendências só em `system=553`.
  Placeholders: 0 divergências · avisos de glossário inalterados (14).

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
