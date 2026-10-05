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

# 7. sufixo plural EN: removido é ok
d, r = case("suf", {"e.json": {"{{value0}} label{{value1}}": "{{value0}} etiqueta"}})
assert r.returncode == 0, r.stdout + r.stderr

# 8. flag --pending por lane
d, r = case("pend", {"m.json": {}})
r = run(d, "--pending", "m")
assert r.returncode == 0 and "menu.commit" in r.stdout, r.stdout

print("test_build: 9 casos OK")
