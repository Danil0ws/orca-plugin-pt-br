# Contribuindo com o orca-plugin-pt-br

## Requisitos

- Python 3 (stdlib apenas, sem dependências)
- `gh` autenticado (`gh auth login`) — usado pelo `extract.py`
- Orca instalada (para extrair a versão e testar o pacote)

## Fluxo (1 PR = 1 lane)

1. **Escolha uma lane** — cada lane é um arquivo `tools/dict/<lane>.json`
   (lista em `tools/lanes.json`). Lane = namespace da UI = escopo de 1 PR.
   Issues com prefixo `[orca-ptbr]` no Linear já trazem contagem por lane.

2. **Veja o que falta na sua lane:**

   ```bash
   python3 tools/build.py --pending <lane>
   ```

   (uma linha por pendência: `chave<TAB>texto em inglês`)

3. **Traduza** em `tools/dict/<lane>.json` — par `"English": "português"`,
   `indent=1`, JSON válido. Regras:

   - **GLOSSARY.md é contrato.** Termos em inglês listados ali não mudam
     (`worktree`, `branch`, `commit`, `tooling`...). Em caso de dúvida:
     veja o que o catálogo upstream já usa e abra PR no GLOSSARY.md.
   - Placeholders `{{...}}` **byte a byte**. Sufixo de plural do inglês
     (`label{{value1}}`) é **removido**, nunca copiado.
   - Mesmo texto inglês em duas chaves = mesma tradução. Contexto diferente?
     exceção em `tools/dict/by-key.json` (`chave → tradução`) justificada no PR.
   - Registro informal de "você", sem CAPS, aspas retas.

4. **Valide (gate):**

   ```bash
   python3 tools/test_build.py && python3 tools/build.py
   ```

   Ambos em verde. O build **bloqueia**: placeholder divergente, par órfão
   (EN fora do catálogo), valor > 8.192, profundidade > 16. **Avisa** (não
   bloqueia): desvio de glossário.

5. **Nunca edite** `locales/pt-BR.json` (gerado) nem `tools/en-all.json`
   (derivado). Edição neles é revertida no próximo build.

## A cada release da Orca

```bash
python3 tools/extract.py     # novo en.json pela tag + allowed-chrome.txt
python3 tools/build.py       # relatório de adds/removes/pendências
```

Depois: traduzir as novidades, atualizar `ORCA_VERSION`, `version` no
manifesto, CHANGELOG e tag `v<versão>`.

## Propor termo novo

PR alterando `GLOSSARY.md` **e** `tools/glossary.json` (o build passa a
avisar desvios do termo). Revisão humana obrigatória.
