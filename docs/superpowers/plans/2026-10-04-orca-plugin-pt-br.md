# orca-plugin-pt-br Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transformar o fork `stablyai/orca-portuguese` num pacote pt-BR comunitário com pipeline de dicionários por lane, glossário verificado e contribuição paralela via Linear + Orca.

**Architecture:** Fonte da verdade = `tools/dict/<lane>.json` (pares EN→pt-BR, um arquivo por namespace para paralelismo sem conflito). `extract.py` baixa o `en.json` da tag `v$(ORCA_VERSION)` + whitelist da zona protegida; `build.py` mergeia dicts → `locales/pt-BR.json` (gerado) com validações; `GLOSSARY.md` + `tools/glossary.json` tornam terminologia verificável (warnings no build).

**Tech Stack:** Python 3 stdlib puro (sem deps), `gh` CLI, JSON. Orca 1.4.220 instalado (`/Applications/Orca.app`), CLI `orca` + Linear (time `BUF`).

**Spec:** `docs/superpowers/specs/2026-10-04-orca-plugin-pt-br-design.md`

**Referência de port:** `https://raw.githubusercontent.com/imgusev/orca-plugin-ru/main/tools/{extract.py,build.py}` (MIT — copiar e traduzir mensagens; lógica intacta; attribution no LICENSE).

## Global Constraints

- `ORCA_VERSION=1.4.220`, `COMPAT=1.4.169`, manifest `version=1.4.220`, `engines.orca=">=1.4.169"`.
- Limites do validador da Orca: ≤20.000 entradas, profundidade ≤16, valor ≤8.192 chars.
- Plurais pt-BR: só `_one`/`_other` (regra i18next `pt`); `dict/plurals.json` seed vazio.
- `locales/pt-BR.json` é GERADO — nunca editado à mão. Fonte da verdade: `tools/dict/*.json`.
- Zona protegida `auto.components.settings.plugin*` fora de `allowed-chrome.txt` é cortada pelo build; nunca traduzir.
- Placeholders `{{...}}` preservados byte a byte; sufixo plural EN (`label{{value1}}`) é REMOVIDO na tradução.
- Glossário: warnings não bloqueiam build; pares órfãos (EN ausente do catálogo) BLOQUEIAM.
- Issues Linear: time `BUF`, prefixo `[orca-ptbr]`, ~1,5s entre criações.
- Commits frequentes, mensagens em pt-BR, CHANGELOG atualizado a cada entrega.

---

### Task 1: Base do repo (manifesto, versões, licença)

**Files:**
- Modify: `orca-plugin.json`
- Create: `ORCA_VERSION`, `COMPAT`, `.gitignore`, `LICENSE`

**Interfaces:**
- Produces: `ORCA_VERSION` (1 linha, `1.4.220`) e `COMPAT` (`1.4.169`) — lidos por `extract.py`/`build.py` nas Tasks 2–3.

- [ ] **Step 1: Sobrescrever `orca-plugin.json`**

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
  "contributes": { "languagePacks": [{ "locale": "pt-BR", "path": "locales/pt-BR.json" }] },
  "capabilities": []
}
```

- [ ] **Step 2: Arquivos de versão, gitignore e licença**

`ORCA_VERSION` → `1.4.220\n` · `COMPAT` → `1.4.169\n`

`.gitignore`:
```
__pycache__/
tools/en-all.json
```

`LICENSE` → MIT, copyright `2026 Danil0ws e contribuidores orca-plugin-pt-br`, com linha extra: `Os textos em inglês do catálogo pertencem a Stably AI (Orca, MIT) e são usados sob a mesma licença. Ferramentas derivadas de imgusev/orca-plugin-ru (MIT).`

- [ ] **Step 3: Verificar**

Run: `python3 -c "import json; m=json.load(open('orca-plugin.json')); assert m['version']=='1.4.220' and m['engines']['orca']=='>=1.4.169' and m['contributes']['languagePacks'][0]['path']=='locales/pt-BR.json'; print('manifest ok')"`
Expected: `manifest ok`

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "chore: manifesto comunitário (id orca-plugin-pt-br, v1.4.220, engines >=1.4.169, MIT)"
```

---

### Task 2: `tools/extract.py` (port do orca-plugin-ru)

**Files:**
- Create: `tools/extract.py`
- Outputs (derivados, gitignored): `tools/en-all.json`, `tools/allowed-chrome.txt`, `tools/plural-candidates.txt`, `ORCA_VERSION`

**Interfaces:**
- Produces: `tools/en-all.json` = plano `{chave_i18n: texto_EN}` (fonte de tudo); `tools/allowed-chrome.txt` (1 caminho por linha, zona protegida permitida); `tools/plural-candidates.txt`.

- [ ] **Step 1: Copiar fonte**

```bash
curl -sL https://raw.githubusercontent.com/imgusev/orca-plugin-ru/main/tools/extract.py -o tools/extract.py
```

- [ ] **Step 2: Traduzir TODAS as strings de docstring/prints/erros para pt-BR; lógica intocada**

Substituições obrigatórias (linhas de referência do original RU):
- Docstring do topo → `"""Constrói o mapa 'chave i18next → texto inglês' para a Orca instalada. ..."""` resumindo os 2 fontes (catálogo da tag `v$(ORCA_VERSION)` + casamento com `app.asar`), regra "catálogo da tag é a fonte principal", saídas `en-all.json` (derivado) e `allowed-chrome.txt` (interseção `COMPAT` × versão instalada).
- `sys.exit("нужен gh CLI...")` → `"necessário gh CLI: brew install gh && gh auth login"`
- `sys.exit(f"не удалось получить...")` → `f"não foi possível obter {path} na tag {ref}:\n{err.stderr.strip()}"`
- Prints: `каталог релиза v{version}: {len(catalog)} ключей` → `catálogo da tag v{version}: {len(catalog)} chaves`; `защищённая зона: ...` → `zona protegida:        {len(allowed)} caminhos permitidos (interseção v{floor} … v{version})`; `формы числа: ...` → `formas de plural:       {len(candidates)} chaves recebem count`; `добавлено из app.asar: ...` → `adicionados do app.asar: {len(extra)} (fora do catálogo da tag)`; `всего {len(pairs)} ключей → {out}` → `total {len(pairs)} chaves → {out}`; `версия Orca: ...` → `versão da Orca: {version} → ORCA_VERSION`.
- Mensagens de erro de `orca_version`/`compat_floor` → pt-BR (`"não foi possível ler a versão do Info.plist junto ao asar"`, etc.).
- Comentários dos regex `PAIR`/`COUNT_CALL`/`fetch_file` → pt-BR (mesmo conteúdo traduzido).

NÃO alterar: `CATALOG_PATH`, `CHROME_PATH`, `REPO`, `CHROME_RE`, `PAIR`, `COUNT_CALL`, `DEFAULT_ASAR`, funções `flatten/scan_asar/scan_plural_candidates/fetch_*`, fluxo do `main()`.

- [ ] **Step 3: Rodar contra a Orca real**

Run: `python3 tools/extract.py`
Expected: sai 0; imprime `catálogo da tag v1.4.220: 15007 chaves`, `zona protegida: N caminhos permitidos (interseção v1.4.169 … v1.4.220)`, `total ≥15007 chaves → tools/en-all.json`; `ORCA_VERSION` reescrito = `1.4.220`.

- [ ] **Step 4: Verificar saídas**

Run: `python3 -c "import json; d=json.load(open('tools/en-all.json')); assert len(d)>=15000; a=open('tools/allowed-chrome.txt').read().split(); assert a and all(x.startswith('auto.components.settings.') for x in a); print(len(d),'chaves;',len(a),'permitidas')"`
Expected: `15007 chaves; N permitidas`

- [ ] **Step 5: Commit**

```bash
git add tools/extract.py && git commit -m "feat(tools): extract.py — catálogo da tag + zona protegida por interseção COMPAT×instalada"
```

---

### Task 3: `tools/lanes.json` + `tools/build.py` (port com validações novas)

**Files:**
- Test first: `tools/test_build.py` (failing)
- Create: `tools/lanes.json`, `tools/build.py`

**Interfaces:**
- Consumes: `tools/en-all.json` (Task 2), `tools/allowed-chrome.txt` (Task 2).
- Produces: `locales/pt-BR.json` (ninhado, gerado); exit≠0 em placeholder quebrado/pares órfãos/valor>8192; warnings de glossário (exit 0); flag `--pending <lane>`.

- [ ] **Step 1: `tools/lanes.json`** (ordem importa: primeiro prefixo que casar vence; catch-all no fim)

```json
[
  { "name": "chrome", "prefixes": ["app.", "sidebar.", "menu.", "tray.", "common.", "notifications."] },
  { "name": "settings", "prefixes": ["settings.", "auto.components.settings."] },
  { "name": "integrations", "prefixes": ["githubChecks.", "checksPanel.", "auto.components.github", "auto.components.GitHub", "auto.components.PullRequestPage.", "auto.components.gitlab", "auto.components.GitLab", "auto.components.linear", "auto.components.Linear", "auto.components.jira", "auto.components.Jira"] },
  { "name": "editor", "prefixes": ["editor.", "sourceControl.", "quickOpen.", "worktreeJumpPalette.", "auto.components.editor.", "auto.components.diff."] },
  { "name": "terminal-sessions", "prefixes": ["terminal.", "fileExplorer.", "sessionSearch.", "sessionHistory.", "auto.components.terminal", "auto.components.Terminal", "auto.components.cmd."] },
  { "name": "layout-right", "prefixes": ["auto.components.right.", "auto.components.rightSidebar.", "auto.components.status.", "auto.components.tab."] },
  { "name": "layout-sidebar", "prefixes": ["auto.components.sidebar.", "auto.components.new.", "auto.components.shared.", "auto.components.floating.", "auto.components.contextual."] },
  { "name": "feature", "prefixes": ["featureTips.", "agentsSidebarIntro.", "auto.components.feature.", "auto.components.onboarding.", "auto.components.Landing.", "auto.components.FirstLaunchBanner."] },
  { "name": "skills-tasks", "prefixes": ["auto.components.skills.", "auto.components.automations.", "auto.components.TaskPage.", "auto.components.task", "auto.components.agent."] },
  { "name": "workspace", "prefixes": ["sparsePreset.", "auto.components.workspace.", "auto.components.worktree", "auto.components.sparse", "auto.components.NewWorkspace", "auto.components.ComposerParentWorktreePicker."] },
  { "name": "browser", "prefixes": ["browser.", "auto.components.browser", "auto.components.Browser", "auto.components.emulator."] },
  { "name": "mobile", "prefixes": ["auto.components.mobile.", "auto.components.native", "auto.components.dictation.", "auto.components.pet."] },
  { "name": "runtime-lib", "prefixes": ["auto.lib.", "auto.hooks.", "auto.store.", "auto.web.", "auto.App.", "auto.runtime.", "auto.main.", "auto.i18n.", "auto.ssh."] },
  { "name": "dashboard", "prefixes": ["dashboard", "runtimeRpc.", "auto.components.dashboard."] },
  { "name": "system", "prefixes": [""] }
]
```

Regra de teto: se o relatório do build mostrar alguma lane com >60KB de EN pendente, dividir aquela lane em `lanes.json` no próximo nível de segmento (o nome da lane = nome do dict `tools/dict/<lane>.json`).

- [ ] **Step 2: Teste falhando** — `tools/test_build.py` (código completo abaixo; usa subprocess + fixtures em tmpdir)

```python
#!/usr/bin/env python3
"""Testes do build: fixtures mínimas em tmpdir, subprocess. Rode: python3 tools/test_build.py"""
import json, os, pathlib, shutil, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build.py"

EN_ALL = {
    "auto.components.settings.save": "Save changes",
    "auto.components.settings.pluginBlocked": "This plugin is blocked",
    "menu.commit": "Commit {{count}} files",
    "editor.label": "{{value0}} label{{value1}}",
    "menu.worktree": "Open worktree",
    "menu.old": "Legacy string",
}
LANES = [{"name": "s", "prefixes": ["auto.components.settings."]},
         {"name": "m", "prefixes": ["menu."]},
         {"name": "e", "prefixes": ["editor."]},
         {"name": "z", "prefixes": [""]}]

def scaffold(d: pathlib.Path, dicts: dict, allowed="", glossary=None, by_key=None):
    t = d / "tools"; (t / "dict").mkdir(parents=True); (d / "locales").mkdir()
    (t / "build.py").write_text(BUILD.read_text())
    json.dump(EN_ALL, open(t / "en-all.json", "w"), ensure_ascii=False)
    json.dump(LANES, open(t / "lanes.json", "w"))
    (t / "allowed-chrome.txt").write_text(allowed)
    for name, pairs in dicts.items():
        json.dump(pairs, open(t / "dict" / name, "w"), ensure_ascii=False)
    if glossary is not None:
        json.dump(glossary, open(t / "glossary.json", "w"), ensure_ascii=False)
    if by_key is not None:
        json.dump(by_key, open(t / "dict" / "by-key.json", "w"), ensure_ascii=False)

def run(d: pathlib.Path, *args):
    return subprocess.run([sys.executable, str(d / "tools" / "build.py"), *args],
                          capture_output=True, text=True)

def case(name, dicts, **kw):
    d = pathlib.Path(tempfile.mkdtemp()) / name
    d.mkdir()
    scaffold(d, dicts, **kw)
    return d, run(d)

# 1. build feliz
d, r = case("ok", {"s.json": {"Save changes": "Salvar alterações"}})
assert r.returncode == 0, r.stdout + r.stderr
cat = json.load(open(d / "locales" / "pt-BR.json"))
assert cat["auto"]["components"]["settings"]["save"] == "Salvar alterações", cat

# 2. placeholder quebrado → falha
d, r = case("ph", {"m.json": {"Commit {{count}} files": "Commitir arquivos"}})
assert r.returncode != 0 and "plac" in (r.stdout + r.stderr), r.stdout + r.stderr

# 3. zona protegida fora da whitelist → cortada, exit 0
d, r = case("prot", {"s.json": {"Save changes": "X", "This plugin is blocked": "Este plugin está bloqueado"}})
assert r.returncode == 0, r.stderr
cat = json.load(open(d / "locales" / "pt-BR.json"))
assert "pluginBlocked" not in json.dumps(cat)
# 3b. na whitelist → passa
d, r = case("prot-ok", {"s.json": {"This plugin is blocked": "Bloqueado"}},
            allowed="auto.components.settings.pluginBlocked\n")
assert r.returncode == 0 and "Bloqueado" in open(d / "locales" / "pt-BR.json").read()

# 4. par órfão (EN fora do catálogo) → falha
d, r = case("stale", {"m.json": {"Not in catalog": "x"}})
assert r.returncode != 0 and "órf" in (r.stdout + r.stderr), r.stdout + r.stderr

# 5. glossário: termo verbatim sumiu → warning, exit 0
d, r = case("gl", {"m.json": {"Open worktree": "Abrir árvore de trabalho"}},
            glossary={"verbatim": ["worktree"], "banned": {"worktree": ["árvore de trabalho"]}})
assert r.returncode == 0, r.stderr
assert "GLOSSÁRIO" in r.stdout, r.stdout

# 6. by-key null → fica em inglês (chave ausente do catálogo gerado)
d, r = case("null", {"m.json": {"Open worktree": "Abrir worktree"}},
            by_key={"menu.worktree": None})
assert r.returncode == 0, r.stderr
cat = json.load(open(d / "locales" / "pt-BR.json"))
assert cat.get("menu", {}).get("worktree") is None, cat

# 7. sufixo plural EN: removido é ok, mantido falha/avisa
d, r = case("suf", {"e.json": {"{{value0}} label{{value1}}": "{{value0}} etiqueta"}})
assert r.returncode == 0, r.stdout + r.stderr

# 8. flag --pending por lane
d, r = case("pend", {"m.json": {}}, )
r = run(d, "--pending", "m")
assert r.returncode == 0 and "menu.commit" in r.stdout, r.stdout

print("test_build: 9 casos OK")
```

- [ ] **Step 3: Rodar — deve FALHAR** (`build.py` ainda não existe)

Run: `python3 tools/test_build.py`
Expected: `FileNotFoundError: .../build.py` (RED)

- [ ] **Step 4: Portar `build.py`**

```bash
curl -sL https://raw.githubusercontent.com/imgusev/orca-plugin-ru/main/tools/build.py -o tools/build.py
```

Aplicar EXATAMENTE estas mudanças (tudo mais permanece igual ao RU):

1. Docstring/prints/erros → pt-BR (mesmos números do relatório do RU, termos: "dicionários", "traduzido", "protegido pelo Orca", "sem tradução", "divergências de placeholder", "escrito: ...").
2. `out = os.path.join(ROOT, "locales", "ru.json")` → `"pt-BR.json"`.
3. `PLURAL_FORMS = ("one", "few", "many", "other")` → `PLURAL_FORMS = ("one", "other")` (plural pt-BR i18next).
4. Tornar `by-key.json` e `plurals.json` OPCIONAIS (o RU abre direto; os testes nem sempre os criam):

```python
    try:
        by_key = {k: v for k, v in json.load(open(by_key_path)).items() if not k.startswith("_")}
    except FileNotFoundError:
        by_key = {}
    try:
        plurals = {k: v for k, v in json.load(open(plurals_path)).items() if not k.startswith("_")}
    except FileNotFoundError:
        plurals = {}
```

5. Subir no topo, junto ao `PROTECTED_ROOT`:

```python
# Lanes: tools/lanes.json (ordem = prioridade; "" casa com tudo)
try:
    LANES = [(l["name"], l["prefixes"]) for l in json.load(open(os.path.join(HERE, "lanes.json")))]
except FileNotFoundError:
    LANES = []

def lane_of(key: str) -> str:
    for name, prefixes in LANES:
        if any(key.startswith(p) for p in prefixes):
            return name
    return "system"
```

6. Trocar o laço de merge por versão que guarda CHAVE (para lane/pendências), mantendo a semântica RU:

```python
    ru: dict[str, str] = {}
    print("dicionários:")
    for path in sorted(glob.glob(os.path.join(HERE, "dict", "*.json"))):
        if os.path.basename(path) in ("by-key.json", "plurals.json"):
            continue
        entries = json.load(open(path))
        ru.update(entries)
        print(f"  {os.path.basename(path):24} {len(entries):5}")
    print(f"  {'by-key.json':24} {len(by_key):5} (overrides por chave)")

    translated, skipped, overridden, oversized = {}, [], 0, []
    missing_keys: dict[str, str] = {}   # chave → EN, para --pending
    for key, raw in source.items():
        english = decode_js(raw)
        if len(english) > MAX_VALUE_LENGTH:
            oversized.append(key)
            continue
        if key in by_key:
            overridden += 1
            if by_key[key] is not None:
                translated[key] = by_key[key]
            continue
        if english not in ru:
            missing_keys[key] = english
        elif protected(key):
            skipped.append(key)
        else:
            translated[key] = ru[english]
```

7. Logo após o laço (e antes dos plurais), flag de pendências + pares órfãos + glossário:

```python
    # pares órfãos: EN que não existe mais no catálogo da tag — bloqueiam o build
    source_texts = {decode_js(v) for v in source.values()}
    stale = sorted(t for t in ru if t and t not in source_texts)
    stale_keys = sorted(k for k in by_key if k not in source)
    if stale or stale_keys:
        raise SystemExit(
            "pares órfãos (EN/chave ausente do catálogo) — remova do dict:\n  "
            + "\n  ".join((stale + stale_keys)[:20])
        )

    if len(sys.argv) > 2 and sys.argv[1] == "--pending":
        lane = sys.argv[2]
        for key in sorted(missing_keys):
            if lane_of(key) == lane:
                print(f"{key}\t{missing_keys[key]}")
        raise SystemExit(0)
```

(Importar `sys` — o RU não importa.)

8. Glossário (warnings nunca bloqueiam) — função nova + chamada após montar `translated`:

```python
def load_glossary() -> tuple[list, dict]:
    try:
        data = json.load(open(os.path.join(HERE, "glossary.json")))
    except FileNotFoundError:
        return [], {}
    return data.get("verbatim", []), data.get("banned", {})
```

```python
    verbatim, banned = load_glossary()
    glossary_warnings = []
    for key, value in translated.items():
        if key not in source:
            continue
        english = decode_js(source[key])
        for term in verbatim:
            if (re.search(rf"\b{re.escape(term)}\b", english, re.I)
                    and not re.search(rf"\b{re.escape(term)}\b", value, re.I)):
                glossary_warnings.append(f"{key}: termo {term!r} sumiu — en: {english!r} → pt: {value!r}")
        for term, wrongs in banned.items():
            if any(w in value.lower() for w in wrongs):
                glossary_warnings.append(f"{key}: renderização proibida de {term!r}: {value!r}")
```

9. No relatório final (prints do RU) adicionar:

```python
    from collections import Counter
    pend = Counter(lane_of(k) for k in missing_keys)
    pend_bytes = Counter()
    for k in missing_keys:
        pend_bytes[lane_of(k)] += len(missing_keys[k])
    print("pendências por lane:   " + " · ".join(f"{k}={v}" for k, v in sorted(pend.items(), key=lambda x: -x[1])))
    print("bytes EN pendentes/lane (teto 60k p/ dividir lane): "
          + " · ".join(f"{k}={v}" for k, v in sorted(pend_bytes.items(), key=lambda x: -x[1])))
    if glossary_warnings:
        print(f"\nAVISOS DE GLOSSÁRIO ({len(glossary_warnings)} — não bloqueiam):")
        for w in glossary_warnings[:30]:
            print(f"  {w}")
```

E no fim, se `broken` (placeholders) não vazio, o RU já aborta/relata — manter comportamento RU: `broken` relata no fim mas o RU NÃO aborta por ele... **mudança**: para o gate da spec, abortar:

```python
    if broken:
        raise SystemExit(f"{len(broken)} divergências de placeholder bloqueiam o build (ver relatório acima)")
```

Limites do validador da Orca (spec §6.5) — adicionar logo antes do dump:

```python
    if depth(catalog) > 16:
        raise SystemExit(f"profundidade {depth(catalog)} > 16 rejeitaria o pacote")
    if len(translated) > 20000:
        raise SystemExit(f"{len(translated)} entradas > 20000 rejeitariam o pacote")
```

Ordem final do `main()`: checagens → relatório de diagnóstico (todos os prints, inclusive
`broken`, `kept_suffix`, pendências e glossário) → `if broken: raise SystemExit(...)` →
`json.dump(catalog)` → print `escrito: ...`. Ou seja: mover o dump para o FINAL, depois do
relatório e do abort — build vermelho não reescreve o catálogo.

- [ ] **Step 5: RED → GREEN**

Run: `python3 tools/test_build.py`
Expected: `test_build: 9 casos OK`. Qualquer assert falhando → corrigir `tools/build.py` (o teste é o contrato) e rodar de novo.

- [ ] **Step 6: Commit**

```bash
git add tools/build.py tools/lanes.json tools/test_build.py && git commit -m "feat(tools): build.py — merge por lane, zona protegida, órfãos, glossário e --pending"
```

---

### Task 4: Seed dos dicionários a partir do catálogo upstream

**Files:**
- Create (derivados, commitados): `tools/dict/<lane>.json` (≈15 arquivos), `tools/dict/by-key.json`, `tools/dict/plurals.json`
- Regenerate: `locales/pt-BR.json` (passa a ser gerado)
- Scratch (NÃO commitar): script de seed no diretório de scratch do agente

**Interfaces:**
- Consumes: `tools/en-all.json`, `tools/lanes.json`, `locales/pt-BR.json` atual (upstream, chave→pt-BR aninhado).
- Produze: dicionários prontos; cobertura ~83%; relatório de órfãos upstream descartados.

- [ ] **Step 1: Rodar seed (script no scratch, py stdlib)**

Script no scratch (`python3 seed.py`, saída impressa) — cópia literal:

```python
#!/usr/bin/env python3
# Seed: catalogo upstream (chave->pt) -> tools/dict/<lane>.json (EN->pt) + by-key.json
import collections, json, pathlib, subprocess

REPO = pathlib.Path("/Users/danilo/Dev/orca-plugin-pt-br")

def flat(o, p="", out=None):
    out = {} if out is None else out
    for k, v in o.items():
        if isinstance(v, dict):
            flat(v, p + k + ".", out)
        else:
            out[p + k] = v
    return out

en = flat(json.load(open(REPO / "tools/en-all.json")))
pt = flat(json.loads(subprocess.run(
    ["git", "-C", str(REPO), "show", "HEAD:locales/pt-BR.json"],
    capture_output=True, text=True, check=True).stdout))
lanes = [(l["name"], l["prefixes"]) for l in json.load(open(REPO / "tools/lanes.json"))]

def lane_of(key):
    for name, prefixes in lanes:
        if any(key.startswith(p) for p in prefixes):
            return name
    return "system"

stale = sorted(k for k in pt if k not in en)
print(f"orfao upstream descartado: {len(stale)}")
for k in stale[:20]:
    print("  ", k)

votes = collections.defaultdict(collections.Counter)   # EN -> {pt: n}
lane_of_en = {}
for k, v in pt.items():
    if k not in en or not isinstance(v, str) or not v:
        continue
    votes[en[k]][v] += 1
    lane_of_en.setdefault(en[k], lane_of(k))

pairs, conflicted = collections.defaultdict(dict), []
for e, c in votes.items():
    generic = c.most_common(1)[0][0]
    pairs[lane_of_en[e]][e] = generic
    if len(c) > 1:
        conflicted.append((e, dict(c)))

by_key = {}
for k, v in pt.items():
    if k not in en or not isinstance(v, str) or not v:
        continue
    e = en[k]
    if v != pairs[lane_of_en[e]][e]:
        by_key[k] = v

(REPO / "tools" / "dict").mkdir(exist_ok=True)
for lane, d in sorted(pairs.items()):
    json.dump(dict(sorted(d.items())), open(REPO / "tools" / "dict" / f"{lane}.json", "w"),
              ensure_ascii=False, indent=1)
    print(f"{lane:22} {len(d):5} pares")
json.dump(dict(sorted(by_key.items())),
          open(REPO / "tools" / "dict" / "by-key.json", "w"), ensure_ascii=False, indent=1)
json.dump({"_comment": "Formas pt-BR (_one/_other) para chaves com count; ver plural-candidates.txt"},
          open(REPO / "tools" / "dict" / "plurals.json", "w"), ensure_ascii=False, indent=1)
print(f"by-key: {len(by_key)} overrides | conflitos EN: {len(conflicted)} | orfaos: {len(stale)}")
```

Esperado: `orfao upstream descartado` = só chaves removidas upstream; `conflitos EN` = poucos (os que forem para by-key); pares somando ≈12.5xx.

- [ ] **Step 2: Build verde contra dados reais**

Run: `python3 tools/build.py`
Expected: exit 0; imprime `traduzido: ~124xx (~83%)`, `sem tradução: ~25xx`, `pendências por lane: ...`, `divergências de placeholder: 0`, `escrito: .../locales/pt-BR.json`.

- [ ] **Step 3: Verificar migração 100% (spec §8.5)**

Run: `python3 -c "
import json
def flat(o,p='',out=None):
    out={} if out is None else out
    for k,v in o.items():
        flat(v,p+k+'.',out) if isinstance(v,dict) else out.__setitem__(p+k,v)
    return out
up=flat(json.load(open('locales/pt-BR.json')))  # já regenerado — comparar com git
" ; git diff --stat locales/pt-BR.json`
Expected: nenhum valor upstream perdido — conferir com `git show HEAD:locales/pt-BR.json` antes do build (salvar cópia `cp locales/pt-BR.json /tmp/upstream-pt.json` no Step 1) e comparar: toda chave upstream com tradução que sobreviveu ao filtro de órfãos tem valor idêntico ou foi movida para `by-key.json`. Script de comparação imprime `perdidos: 0`.

- [ ] **Step 4: Commit**

```bash
git add tools/dict locales/pt-BR.json && git commit -m "feat: seed dos dicionários por lane a partir do catálogo upstream (12.5xx strings)"
```

---

### Task 5: Glossário (`GLOSSARY.md`, `tools/glossary.json`, `UNTRANSLATED.md`)

**Files:**
- Create: `GLOSSARY.md`, `tools/glossary.json`, `UNTRANSLATED.md`

**Interfaces:**
- Consumes: `tools/build.py` (lê `glossary.json` → warnings), catálogo upstream (decisões já praticadas).

- [ ] **Step 1: Derivar decisões do catálogo existente** (não inventar)

Run: `python3 -c "
import json
def flat(o,p='',out=None):
    out={} if out is None else out
    for k,v in o.items():
        flat(v,p+k+'.',out) if isinstance(v,dict) else out.__setitem__(p+k,v)
    return out
en=flat(json.load(open('tools/en-all.json'))); import subprocess
pt=json.loads(subprocess.run(['git','show','HEAD:locales/pt-BR.json'],capture_output=True,text=True).stdout)
pt=flat(pt)
for t in ['workspace','session','skill','agent','prompt','tooling','runtime','terminal','diff','stash','checkout']:
    hits=[(k,en[k],pt[k]) for k in pt if k in en and en[k].lower()==t][:3]
    print(t, hits)"
`
Expected: lista de uso real — com ela fechar a coluna *pt-BR* de `GLOSSARY.md` (ex.: se upstream já traduz `workspace`, manter traduzido; se mantém, manter).

- [ ] **Step 2: `GLOSSARY.md`**

```markdown
# Glossário EN × pt-BR — orca-plugin-pt-br

Contrato de terminologia. Mudança aqui = PR dedicado + revisão humana.
`tools/build.py` lê o espelho em `tools/glossary.json` e emite AVISOS
(não bloqueiam o build) para desvios.

## Mantidos em inglês (não traduzir)

| Termo | Por quê |
|---|---|
| worktree | `git worktree` — é o nome do comando |
| branch, commit, merge, rebase, stash, checkout, push, pull, HEAD | termos git consagrados (GitHub/GitLab pt-BR os mantêm) |
| tooling | não há equivalente natural; "ferramentar/ferramentamento" não é usado |
| diff, staged, unstaged | UI de revisão segue o vocabulário git |
| prompt, token | termos técnicos consagrados em pt-BR de dev |
| PR / MR | siglas; "pull request" por extenso quando couber |
| Orca, Linear, Jira, GitHub, GitLab, Bitbucket, Codex, Antigravity | nomes próprios |
| comandos CLI, paths, placeholders `{{...}}`, atalhos | literais — traduzir quebraria |

## Decisões por analogia com o catálogo upstream

| English | pt-BR | Nota |
|---|---|---|
| (preenchido no Step 1 a partir do uso real no catálogo) | | |

## Regras gerais

- Registro informal de "você"; sem caps; aspas retas; placeholders byte a byte.
- String mantida em inglês sem constar aqui → justificar em `UNTRANSLATED.md`.
```

- [ ] **Step 3: `tools/glossary.json`** (espelho verificável; `banned` = renderizações proibidas)

```json
{
  "_comment": "Espelho de GLOSSARY.md — verificado por tools/build.py (warnings)",
  "verbatim": ["worktree", "branch", "commit", "merge", "rebase", "stash", "checkout", "push", "pull", "HEAD", "tooling", "diff", "prompt", "token"],
  "banned": {
    "worktree": ["árvore de trabalho", "arvore de trabalho"],
    "tooling": ["ferramentar", "ferramentamento", "ferramentário"],
    "stash": ["esconderijo"],
    "commit": ["submeter alterações"]
  }
}
```

(ajustar `verbatim` com o resultado do Step 1 — se upstream traduz `session`/`workspace`, NÃO entrar em `verbatim`.)

- [ ] **Step 4: `UNTRANSLATED.md`**

```markdown
# Por que ficou em inglês

Gerado/curado junto ao build. Categorias:

1. **Zona protegida** (`auto.components.settings.plugin*` fora de
   `allowed-chrome.txt`) — o validador da Orca rejeita o pacote inteiro;
   textos sobre confiança em plugins não podem ser substituídos.
2. **Literais** — comandos CLI, paths, placeholders, atalhos de teclado,
   nomes de produto. Ver GLOSSARY.md.
3. **>8.192 caracteres** — blocos CSS de vitrine; o validador rejeitaria o pacote.
4. **Termos consagrados** — ver GLOSSARY.md.

Lista atualizada: `python3 tools/build.py` imprime `sem tradução` e
`--pending <lane>` lista as pendências por lane (aí sim são DÍVIDAS, não
decisões).
```

- [ ] **Step 5: Build com warnings + commit**

Run: `python3 tools/build.py 2>&1 | grep -A5 GLOSSÁRIO | head -10; echo exit=$?`
Expected: build exit 0; se houver desvios no catálogo seed aparecem avisos (limpar os reais traduzindo o dict; falso positivo → ajustar lista).

```bash
git add GLOSSARY.md tools/glossary.json UNTRANSLATED.md tools/dict && git commit -m "docs: glossário como contrato + espelho verificado pelo build"
```

---

### Task 6: Documentação da comunidade (README, CONTRIBUTING, CHANGELOG)

**Files:**
- Modify: `README.md` (substituir o do upstream)
- Create: `CONTRIBUTING.md`, `CHANGELOG.md`

- [ ] **Step 1: `README.md`** — conteúdo obrigatório (pt-BR + resumo EN):

```markdown
# orca-plugin-pt-br — Português do Brasil para o Orca (comunitário)

Pacote de idioma pt-BR para [Orca](https://github.com/stablyai/orca) (Stably ADE),
fork comunitário do [stablyai/orca-portuguese](https://github.com/stablyai/orca-portuguese)
com pipeline de contribuição paralela. _Community pt-BR language pack for the
Orca agent IDE — MIT._

Funciona com o mecanismo nativo `contributes.languagePacks`: nada é patcheado
na aplicação; chaves desconhecidas caem em inglês (fallback i18next).

**Compatível com Orca ≥ 1.4.169 · catálogo extraído da tag v1.4.220 · veja ORCA_VERSION.**

## Instalação

**1) Git URL** (Settings → Plugins → Install plugin → Git URL — `#ref` é obrigatório):
`https://github.com/Danil0ws/orca-plugin-pt-br.git#v1.4.220`

**2) Desenvolvimento local:** `git clone <repo> ~/orca-plugin-pt-br` →
Settings → Plugins → Development → Add path → selecionar o caminho.
Depois: Settings → Appearance → Language → **pt-BR**.

## Estrutura

(lanes.json · dict/*.json · build.py · en-all.json derivado · locales/pt-BR.json GERADO)

## Contribuir

Veja CONTRIBUTING.md — resumo: pegue uma lane, rode `python3 tools/build.py --pending <lane>`,
traduza em `tools/dict/<lane>.json` seguindo GLOSSARY.md, build verde, PR.

## Licença

MIT. Originais em inglês © Stably AI (Orca, MIT); tooling derivado de
imgusev/orca-plugin-ru (MIT).
```

- [ ] **Step 2: `CONTRIBUTING.md`**

Conteúdo obrigatório: pré-requisitos (`gh` logado, Python 3, Orca instalada); ciclo `python3 tools/extract.py` (a cada release da Orca) → `python3 tools/build.py` → editar só `tools/dict/<lane>.json` (1 PR = 1 lane); regras do glossário (tabela e warning); proibição de editar `locales/pt-BR.json`/`en-all.json`; formato do par (`"English text": "Texto em português"`, JSON válido, `indent=1`); como propor termo novo (PR no GLOSSARY.md); gate: `python3 tools/test_build.py` + `python3 tools/build.py` verdes.

- [ ] **Step 3: `CHANGELOG.md`**

```markdown
# Changelog

## 1.4.220 — 2026-10-04
- Fork comunitário do stablyai/orca-portuguese: id `orca-plugin-pt-br`, engines >=1.4.169.
- Pipeline por lanes: extract.py (catálogo da tag + zona protegida por interseção), build.py (validações, glossário, --pending), test_build.py.
- Seed dos dicts a partir do catálogo upstream (12.5xx strings).
- GLOSSARY.md + UNTRANSLATED.md; README/CONTRIBUTING novos.
```

- [ ] **Step 4: Commit**

```bash
git add README.md CONTRIBUTING.md CHANGELOG.md && git commit -m "docs: README/CONTRIBUTING/CHANGELOG da versão comunitária"
```

---

### Task 7: Registro no Orca + verificação de instalação local

**Files:** nenhum arquivo novo.

- [ ] **Step 1: Registrar repo**

Run: `orca repo add --path /Users/danilo/Dev/orca-plugin-pt-br && orca repo list | grep orca-plugin-pt-br`
Expected: aparece na lista.

- [ ] **Step 2: Tentar habilitar via CLI e checar comando de plugin**

Run: `orca --help 2>&1 | grep -iE "plugin|language"; orca plugins --help 2>&1 | head -20`
Expected: se houver comando de instalar plugin por caminho → usar e depois `orca open` para selecionar o idioma; se não houver → **passo manual documentado**: instruir o usuário (Settings → Plugins → Development → Add path `/Users/danilo/Dev/orca-plugin-pt-br` → Appearance → Language → pt-BR) e confirmar com ele que a UI está em português antes do Task 10.

---

### Task 8: Kickoff Linear (issues `[orca-ptbr]`)

**Files:** nenhum (estado externo).

- [ ] **Step 1: Dedup**

Run: `orca linear search "[orca-ptbr]" --workspace all --limit 50 --json`
Expected: vazio (senão, listar o que já existe e pular).

- [ ] **Step 2: Gerar corpo das issues a partir das pendências reais**

Run: `python3 tools/build.py > /tmp/build-report.txt; grep "pendências por lane" /tmp/build-report.txt`
Para cada lane com pendências > 0, escrever corpo em scratch: lane, dict alvo `tools/dict/<lane>.json`, contagem, comando de verificação (`python3 tools/build.py --pending <lane>` e `python3 tools/build.py`), regras (GLOSSARY.md; não editar locales/; placeholders byte a byte).

- [ ] **Step 3: Criar issues (1 por lane + tooling + docs + glossário)**

```bash
orca linear save-issue --team BUF --title "[orca-ptbr] traduzir lane <lane> (<N> pendências)" \
  --priority medium --body-file /tmp/issue-<lane>.md --json
# tooling/docs/glossário: --priority low (entregues nesta sessão → fechar com comentário)
```
Pausa ~1,5s entre chamadas. `tooling`, `docs` e `glossário` são criadas e FECHADAS ao final do Task 10 com comentário de entrega.

- [ ] **Step 4: Verificar por read-back**

Run: `orca linear list --filter open --team BUF --limit 250 --json | python3 -c "import json,sys; d=json.load(sys.stdin); ids=[i['identifier'] for i in d['issues'] if '[orca-ptbr]' in i['title']]; print(len(ids), ids)"`
Expected: contagem = nº de lanes com pendências + 3 (tooling/docs/glossário).

---

### Task 9: Dispatch paralelo — worktrees do Orca por lane

**Files:** branches `trad-<lane>` no repo.

- [ ] **Step 1: checar sintaxe**

Run: `orca worktree create --help`
Expected: confirmar forma de `--repo` (nome registrado) e `--agent` disponível (`claude`/`codex`).

- [ ] **Step 2: um worktree por lane (paralelo, `--activate`)**

Template de prompt (5 blocos, CONTEXTO load-bearing):

```
TAREFA: traduzir as pendências da lane <lane> — adicionar pares EN→pt-BR em tools/dict/<lane>.json.
CONTEXTO: repo orca-plugin-pt-br. Pendências: rode `python3 tools/build.py --pending <lane>`.
Regras e termos: GLOSSARY.md + tools/glossary.json (o build avisa desvios).
Forma do arquivo: pares "English": "português", indent=1, JSON válido, sort ao salvar.
FRONTEIRAS: NÃO editar locales/pt-BR.json (gerado), tools/en-all.json, outros tools/dict/*.json, GLOSSARY.md.
REGRAS: placeholders {{...}} byte a byte (sufixo plural EN tipo label{{value1}}: REMOVER);
termos em inglês da lista keep-english permanecem iguais; registro informal de "você";
mesmo EN em duas chaves = mesmo pt-BR (ou exception em by-key.json com justificativa no PR).
ENTREGA: `python3 tools/test_build.py` e `python3 tools/build.py` verdes, commit na branch
"trad-<lane>" com mensagem "i18n(pt-BR): lane <lane> — <N> strings", relatório final com
contagem traduzida/restante.
```

```bash
orca worktree create --repo orca-plugin-pt-br --name trad-<lane> --base-branch main \
  --agent claude --prompt "<template preenchido>" --activate
```

- [ ] **Step 3: acompanhar e fazer merge com gate**

Por worktree concluído: `git diff main...trad-<lane> --stat` → checkout main → `git merge trad-<lane>` → **gate**: `python3 tools/test_build.py && python3 tools/build.py` (exit 0 + sem AVISOS DE GLOSSÁRIO novos) → `git push`. Falla de gate → `steer`/reabrir worktree com o erro exato.

- [ ] **Step 4: verificação por read-back**

Run: `git branch --list 'trad-*'; python3 tools/build.py | grep -E "traduzido|pendências por lane"`
Expected: cobertura subiu; pendências = 0 nas lanes entregues.

---

### Task 10: Entrega final (tag, issues, changelog, push)

- [ ] **Step 1: build final + instalação**

Run: `python3 tools/test_build.py && python3 tools/build.py`
Expected: 9 casos OK, exit 0, pendências restantes documentadas (as que ficaram por decisão viram linha em UNTRANSLATED.md; dívidas viram issue aberta).

- [ ] **Step 2: CHANGELOG + tag + push**

Atualizar `CHANGELOG.md` com a cobertura final; commit; `git tag v1.4.220 && git push origin main --tags`.
Se o upstream mudar no meio: repetir Task 2 (extract da nova tag) antes de fechar.

- [ ] **Step 3: fechar issues**

Issues `tooling`/`docs`/`glossário` → `orca linear save-issue <id> --state Done` (ou comentário + transição) com resumo do que entregou; lanes entregues → Done com contagem; lanes com saldo → manter aberta com comentário `python3 tools/build.py --pending <lane>`.

- [ ] **Step 4: relatório final**

Imprimir: cobertura `X/15007 (Y%)`, lanes entregues vs abertas, caminho local do repo, comando de instalação, URLs (repo, issues).
