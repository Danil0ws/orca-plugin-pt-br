# Glossário EN × pt-BR — orca-plugin-pt-br

Contrato de terminologia. Mudança aqui = PR dedicado + revisão humana.
`tools/build.py` lê o espelho em `tools/glossary.json` e emite **AVISOS**
(não bloqueiam o build) para desvios.

Base: o uso real do catálogo upstream (12,5 mil strings) — decisão nova só
entra aqui depois de ver como o upstream já tratou o termo.

## Mantidos em inglês (não traduzir)

| Termo | Por quê |
|---|---|
| worktree | `git worktree` — é o nome do comando; "árvore de trabalho" não existe |
| branch, commit, rebase, checkout | termos git consagrados (GitHub/GitLab pt-BR os mantêm) |
| tooling | não há equivalente natural; "ferramentar/ferramentamento" não é usado |
| runtime | sem tradução consagrada, igual ao upstream |
| terminal, diff | vocabulário da UI técnica, igual ao upstream |
| prompt, skill, workspace | upstream mantém em inglês (verificado no catálogo) |
| PR / MR | siglas; "pull request" por extenso quando couber |
| Orca, Linear, Jira, GitHub, GitLab, Bitbucket, Codex, Antigravity | nomes próprios |
| comandos CLI, paths, placeholders `{{...}}`, atalhos | literais — traduzir quebraria |

## Traduzidos (decididos)

| English | pt-BR | Nota |
|---|---|---|
| session | sessão | não "seanço/plateia" |
| agent | agente | upstream: "Agente" |
| issue | tarefa/issue | GitHub, GitLab, Linear, Jira — manter como upstream |

## Verbos e casos mistos (atenção, mas não é erro automático)

| Termo | Regra |
|---|---|
| merge | **verbo** "mesclar/mergear" traduzido; **botão** "Merge" fica em inglês. Upstream tem os dois — padronizar por PR, o build não avisa. |
| push / pull | como verbo ("Enviar", "Buscar") traduzido; como rótulo de botão fica EM. |
| staged / unstaged | rótulos já vêm traduzidos ("Alterações Preparadas"); em frase pode ficar "staged". |
| token | "token/tokens" — plural em pt-BR é "tokens"; não é desvio. |
| HEAD (ref) | mantido; "head branch" (GitLab) = "branch de origem". |
| terminal | singular mantido em inglês; **plural "terminais" é o padrão do upstream** (56 casos) — não é desvio. |
| runtime | sentidos mistos: ambiente → upstream usa "Ambientes de Execução"; duração → "Tempo de uso". Não é verbatim. |
| prompt | **prompt (LLM)** mantido; **permission prompt** = "alerta/aviso de permissão" (diálogo do macOS). |

## Regras gerais

- Registro informal de "você"; sem CAPS; aspas retas.
- Placeholders `{{...}}` byte a byte; sufixo plural EN (`label{{value1}}`) é REMOVIDO.
- String mantida em inglês sem constar aqui → justificar em `UNTRANSLATED.md`.
