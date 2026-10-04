# Spec: orca-plugin-pt-br — fork comunitário pt-BR do orca-portuguese

Data: 2026-10-04 · Status: aprovada pelo usuário (design B) · Próximo: writing-plans

## 1. Objetivo

Fork comunitário de `stablyai/orca-portuguese` (pacote oficial pt-BR do Orca ADE)
com três acréscimos que o upstream não tem:

1. **Pipeline de tradução** em `tools/` portado do `imgusev/orca-plugin-ru` (MIT):
   extração do catálogo inglês por tag, build do catálogo a partir de dicionários,
   validação automática (placeholders, zona protegida, cobertura).
2. **Terminologia como contrato**: `GLOSSARY.md` + `UNTRANSLATED.md`, com lista
   explícita de termos que **não** se traduzem (worktree, branch, commit, merge,
   PR/MR, tooling, comandos CLI, paths, placeholders) e warnings no build para
   desvios.
3. **Contribuição paralela**: o catálogo é montado a partir de
   `tools/dict/<lane>.json` (pares `en → pt-BR`, um arquivo por namespace), para
   que vários agentes/humanos trabalhem ao mesmo tempo em arquivos disjuntos,
   orquestrados por issues no Linear e worktrees do Orca.

Repo: fork `github.com/Danil0ws/orca-plugin-pt-br` (fork de `stablyai/orca-portuguese`,
relação de fork preservada), local `~/Dev/orca-plugin-pt-br`.

## 2. Não-escopo (fase 1)

- `tools/release.py` completo (publicação automática, PR de marketplace) — fase 2,
  quando houver ritmo de release; fase 1 publica tag manualmente.
- Plurais com 4 formas (russo) — pt-BR usa só `_one`/`_other` (regra i18next `pt`).
- Alterar o upstream `stablyai/orca-portuguese` (contribuições de volta via PR
  normal, quando aplicável).
- Estatística de instalações / site institucional.

## 3. Manifesto (`orca-plugin.json`)

```json
{
  "manifestVersion": 1,
  "id": "orca-plugin-pt-br",
  "publisher": "Danil0ws",
  "name": "Português do Brasil (comunitário)",
  "version": "1.4.220",
  "description": "Pacote de idioma pt-BR para o Orca, mantido pela comunidade.",
  "repository": "https://github.com/Danil0ws/orca-plugin-pt-br",
  "author": { "name": "Comunidade Orca pt-BR" },
  "engines": { "orca": ">=1.4.169" },
  "pluginApi": 1,
  "contributes": { "languagePacks": [{ "locale": "pt-BR", "path": "locales/pt-BR.json" }] }
}
```

Decisões:

- **`version` espelha `ORCA_VERSION`** (regra do orca-plugin-ru: card do plugin já
  mostra para qual versão da Orca o catálogo foi feito; semver estrito, tag
  `v1.4.220`; upstream `v1.0.0` fica para trás sem conflito).
- **`engines >=1.4.169`** (não `>=1.4.0` do upstream): antes de 1.4.169 toda a zona
  `settings.plugin*` é protegida e UMA chave proibida derruba o catálogo inteiro
  (erro `catalog cannot replace protected security copy`, plugin morre em silêncio).
  Puxar `en.json` + `allowed-chrome.txt` pela **interseção** entre COMPAT e a versão
  instalada evita a classe inteira de bug.
- **`id`/`publisher` mudam** → instalação separada do pacote oficial (efeito
  colateral aceito na aprovação).

## 4. Estrutura do repo

```
orca-plugin.json        manifesto (acima)
ORCA_VERSION            1.4.220   (versão da Orca da qual o en.json foi extraído)
COMPAT                  1.4.169   (menor versão suportada; engines espelha)
LICENSE                 MIT (ver §9 risco)
GLOSSARY.md             glossário EN × pt-BR + lista de não-traduzíveis
UNTRANSLATED.md         toda string que permanece em inglês, com justificativa
CHANGELOG.md            pt-BR
README.md               instalação (Git URL #v1.4.220), contribuição, estrutura
CONTRIBUTING.md         como escolher lane, formato do dict, gate do build
locales/pt-BR.json      catálogo GERADO (não editar à mão)
tools/
  extract.py            puxa en.json da tag v$(ORCA_VERSION) em stablyai/orca;
                        gera en-all.json; recalcula allowed-chrome.txt pela
                        interseção COMPAT × versão instalada (via app.asar se houver)
  build.py              merge dicts → locales/pt-BR.json + validações (§6)
  dict/*.json           FONTES DA VERDADE: pares "en text" → "pt-BR text" por lane
  dict/by-key.json      overrides por chave i18n (quando o par en→pt não basta)
  test_build.py         smoke test com asserts (fixtures mínimas)
docs/superpowers/specs/ esta spec e futuras
```

## 5. Lanes (dicionários) — base do paralelismo

Regra: **1 lane = 1 arquivo `dict/*.json` = 1 issue = 1 worktree/agente**.
Teto de ~60KB de texto EN por lane; namespace maior que o teto é dividido no
próximo nível de segmento. Lane é só agrupamento de chaves — o merge final é
determinístico e ordenado, então ordem dos arquivos não importa.

Divisão inicial (medida sobre `en.json` da tag v1.4.220, 15.007 chaves):

| lane | namespaces (caminho i18n) | ≈bytes EN |
|---|---|---|
| chrome | app, sidebar, menu, tray, common, notifications, githubChecks | ~4k |
| settings-a … settings-k | auto.components.settings (248KB → dividido pelo 2º nível; inclui zona protegida `settings.plugin*`, cortada pelo build) | ~248k |
| layout-right | auto.components.right, rightSidebar, status, tab | ~76k (→ 2 lanes se >teto) |
| layout-sidebar | auto.components.sidebar, new, shared, floating, contextual | ~60k |
| feature | auto.components.feature, onboarding, Landing, agentsSidebarIntro | ~55k |
| skills-tasks | auto.components.skills, automations, TaskPage, task, agent | ~85k (→ 2) |
| editor | editor, diff, sourceControl, quickOpen, checksPanel, worktreeJumpPalette | ~4k |
| terminal-sessions | terminal, Terminal, TerminalSearch, fileExplorer, sessionSearch, sessionHistory | ~9k |
| integrations | github*, GitHubItemDialog, PullRequestPage, gitlab*, linear*, Linear*, jira*, Jira*, checksPanel | ~45k |
| workspace | workspace, worktree, sparse*, NewWorkspace*, ComposerParentWorktreePicker | ~12k |
| browser | browser, BrowserPane, browser-pane, emulator | ~14k |
| mobile | mobile, native, nativeChat, native*, dictation, pet | ~11k |
| runtime-lib | auto.lib, auto.hooks, auto.store, auto.web, auto.App, auto.runtime, auto.main, auto.i18n, auto.ssh | ~40k |
| system | rendererRecovery, crash, error, featureTips, dashboard*, runtimeRpc, aiVault, resto não classificado | ~8k |

A lista é **gerada** (`extract.py` reporta bytes por namespace) e ajustada na
implementação; a regra de teto é o contrato, não a tabela.

Seed: pares extraídos do `locales/pt-BR.json` atual (12.524 chaves) distribuídos
nas lanes. Chaves do pt sem correspondência em `en` (obsoletas) saem num relatório
e não entram nas lanes. Chaves `en` sem tradução (≈2.483+) ficam listadas por
lane como pendência inicial — é o backlog que vira issues.

## 6. `build.py` — validações (gate de merge)

Exit code ≠ 0 em qualquer falha:

1. **Estrutura**: dicts são pares string→string; placeholders `{{...}}` do EN
   presentes no pt-BR, byte a byte (exceto sufixo plural EN `label{{value1}}`,
   que deve ser REMOVIDO, não copiado — build distingue os dois casos).
2. **Zona protegida**: remove automaticamente chaves `auto.components.settings.plugin*`
   fora de `allowed-chrome.txt` (interseção de versões). Nunca as inclui.
3. **Escopo**: chave pt-BR que não existe no `en.json` da tag → erro (evita lixo
   acumulado); EN sem tradução → reporta cobertura, não falha.
4. **Glossário** (warning, não falha): tradução contém termo da lista banida
   (ex.: traduziu "worktree"), ou EN da lista keep-English ≠ pt-BR idêntico.
5. **Limites do validador da Orca**: ≤20.000 entras, profundidade ≤16, valor
   ≤8.192 chars, sem chaves perigosas.
6. **Saída**: `locales/pt-BR.json` (sort estável) + impressão de cobertura
   `X/Y (Z%)` e pendências por lane.

## 7. Glossário (formato)

`GLOSSARY.md`:

| English | pt-BR | Nota |
|---|---|---|
| worktree | worktree | `git worktree` — não traduzir |
| branch / commit / merge | idem | termos git consagrados |
| pull request / PR / MR | pull request / PR / MR | alinhar com GitHub pt-BR |
| tooling | tooling | sem equivalente natural |
| ... | ... | ... |

- Coluna *Nota* obrigatória para decisões de "não traduzir".
- Toda string mantida em inglês aparece em `UNTRANSLATED.md` com motivo
  (literal de comando / protegida / termo consagrado / CSS / ambígua).
- Mudança de termo = PR que altera GLOSSARY.md + passa por revisão humana.

Seed inicial da lista keep-English: `worktree`, `branch`, `commit`, `merge`,
`rebase`, `stash`, `checkout`, `push`, `pull`, `tooling`, `runtime`, `prompt`,
`token`, `skill`*, `agent`*, `workspace`*, `session`*, `terminal`, `diff`,
`staged`, `unstaged`, `HEAD`, `hash`, `path`, nomes de produto (Orca, Linear,
Jira, GitHub, GitLab, Bitbucket, Codex, Antigravity), comandos CLI e placeholders.
(* = decisão registrada na coluna Nota, pode ser traduzida se a nota justificar;
a lista completa é fechada na implementação com o glossário upstream do RU como
referência de consistência entre pacotes de idioma.)*

## 8. Orquestração Linear + Orca (dividir para conquistar)

1. Repo registrado: `orca repo add --path ~/Dev/orca-plugin-pt-br`.
2. Issues no time **BUF** (único workspace Linear disponível) com prefixo
   **`[orca-ptbr]`** — 1 por lane + tooling + docs + glossário. Dedup via
   `orca linear search "[orca-ptbr]"` antes de criar. Descrição cita a lane, o
   dicionário alvo e o gate (`python3 tools/build.py`).
3. Dispatch paralelo, um worktree por issue pronta:
   `orca worktree create --repo orca-plugin-pt-br:<path> --name <lane> --base-branch main --agent <claude|codex> --prompt <bloco TAREFA/CONTEXTO/FRONTEIRAS/REGRAS/ENTREGA>`.
   CONTEXTO é load-bearing: aponta `GLOSSARY.md`, `tools/dict/<lane>.json`,
   `en-all.json` e proíbe editar `locales/pt-BR.json` (gerado).
4. Gate único antes de merge: `python3 tools/build.py` verde + revisão do diff
   do glossário. Verificação por read-back: `orca linear list` contando issues
   por prefixo, não por relatório de filho.
5. Fase 1 concluída quando: cobertura do seed = 100% das chaves do upstream
   migradas, build verde, tag `v1.4.220` publicada.

## 9. Erros, limites e riscos

- **Upstream sem LICENSE** → traduções sem licença aberta. Ação: LICENSE MIT no
  fork (cobre tooling/docs; as traduções derivadas são de boa-fé do fork) + PR no
  upstream pedindo LICENSE. Se o upstream recusar, revisar a postura antes de
  divulgar.
- **Chave desconhecida derruba o catálogo inteiro** → build só emite chaves
  presentes no `en.json` da tag (§6.3) e `engines >= COMPAT` (§3).
- **Orca muda chaves todo release** → `extract.py` na CI/humano a cada release:
  relatório de adds/removes/changes; versão nova = novo `ORCA_VERSION` + tag.
- **Conflito entre lanes** → impossível por construção (arquivos disjuntos);
  conflito só em arquivos gerados/comuns — esses são resolvidos pelo build, não à mão.
- **Rate limit do Linear** em criação em massa → criar issues com ~1.5s de intervalo.

## 10. Testes

- `tools/test_build.py` (smoke, asserts): placeholder quebrado falha; chave da
  zona protegida é cortada; chave óbsoleta falha; warning de glossário aparece;
  saída ordenada e limites da Orca respeitados.
- `python3 tools/build.py` contra o catálogo real é o teste de integração.
- Instalação real: caminho local em Settings → Plugins → Development → Add path,
  idioma pt-BR em Settings → Appearance → Language (validação manual na entrega).

## 11. Fora de escopo explícito

Marketplace index, site, estatística, release.py (fase 2), sincronização
automática com glossários de outros pacotes de idioma do Orca.
