#!/usr/bin/env python3
"""Monta locales/pt-BR.json a partir dos dicionários dict/*.json.

Dicionário é JSON plano "texto inglês" → "tradução". O catálogo é montado
sobre o en-all.json (mapa "chave → texto inglês", ver extract.py): a cada
chave cujo texto foi achado nos dicionários atribui-se a tradução. O resto
continua em inglês — o i18next cai no fallback do defaultValue do código.

Imprime o que falta traduzir — é isso que se acrescenta em dict/*.json
novos (um arquivo por lane, ver lanes.json, para contribuição em paralelo).

Regras de bloqueio (exit != 0): placeholder divergente, par órfão (texto
inglês fora do catálogo da tag), valor > 8.192, profundidade > 16,
> 20.000 entradas. Avisos de glossário NÃO bloqueiam.
"""
import glob
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ESCAPE_RE = re.compile(r"\\x([0-9a-fA-F]{2})|\\u([0-9a-fA-F]{4})")
PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")
# Placeholder grudado no fim de palavra — sufixo de plural do inglês:
# "{{value0}} label{{value1}}" insere "s". Em português o número se
# expressa de outra forma, então no sufixo a tradução OMETE o placeholder,
# e isso não é divergência, é o esperado. Duas letras no lookbehind
# cortam "Orca v{{value0}}" e ":L{{value0}}", onde antes do placeholder
# há versão ou número de linha, não fim de palavra.
PLURAL_SUFFIX_RE = re.compile(r"(?<=[A-Za-z]{2})(\{\{[^}]+\}\})(?![A-Za-z0-9_])")

# Zona protegida da Orca: o pacote de idioma não pode trocar os textos
# sobre confiança em plugins. Chave assim no catálogo → o validador
# rejeita O PACOTE INTEIRO ("catalog cannot replace protected security copy")
# e o plugin morre com "The plugin stopped after an activation or worker error".
PROTECTED_ROOT = "auto.components.settings."

# Formas de plural do pt-BR (regra i18next `pt`): one/other.
PLURAL_FORMS = ("one", "other")

# Limite rígido do validador por valor. Estourar rejeita O PACOTE INTEIRO
# ("translation at <path> exceeds 8192 characters"). Só blocos CSS de
# vitrine chegam perto — neles não há o que traduzir.
MAX_VALUE_LENGTH = 8192

try:
    ALLOWED_CHROME = set(open(os.path.join(HERE, "allowed-chrome.txt")).read().split())
except FileNotFoundError:
    ALLOWED_CHROME = set()

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


def load_glossary() -> tuple[list, dict]:
    """Espelho de GLOSSARY.md: termos que ficam em inglês + renderizações proibidas."""
    try:
        data = json.load(open(os.path.join(HERE, "glossary.json")))
    except FileNotFoundError:
        return [], {}
    return data.get("verbatim", []), data.get("banned", {})


def protected(key: str) -> bool:
    if not key.startswith(PROTECTED_ROOT) or key in ALLOWED_CHROME:
        return False
    return key[len(PROTECTED_ROOT):].lower().startswith("plugin")


def decode_js(value: str) -> str:
    """Strings estão no bundle como literal JS — abrimos \\xNN e \\uNNNN."""
    return ESCAPE_RE.sub(
        lambda m: chr(int(m.group(1) or m.group(2), 16)),
        value.replace("\\'", "'"),
    )


def nest(flat: dict) -> dict:
    """Chave auto.components.x.y → objetos aninhados: ponto na chave é proibido pelo validador."""
    root: dict = {}
    for dotted, text in flat.items():
        node = root
        parts = dotted.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = text
    return root


def depth(node: dict, level: int = 1) -> int:
    return max([depth(v, level + 1) for v in node.values() if isinstance(v, dict)] + [level])


def main() -> None:
    source_path = os.path.join(HERE, "en-all.json")
    if not os.path.exists(source_path):
        raise SystemExit("sem en-all.json — primeiro rode: python3 extract.py")
    source = json.load(open(source_path))

    # overrides por chave: o mesmo texto inglês em lugares diferentes quer
    # coisas diferentes — "Cursor" no catálogo de agentes é editor, não cursor
    by_key_path = os.path.join(HERE, "dict", "by-key.json")
    try:
        by_key = {k: v for k, v in json.load(open(by_key_path)).items() if not k.startswith("_")}
    except FileNotFoundError:
        by_key = {}

    plurals_path = os.path.join(HERE, "dict", "plurals.json")
    try:
        plurals = {k: v for k, v in json.load(open(plurals_path)).items() if not k.startswith("_")}
    except FileNotFoundError:
        plurals = {}
    try:
        candidates = set(open(os.path.join(HERE, "plural-candidates.txt")).read().split())
    except FileNotFoundError:
        candidates = set()

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
            # null = "deixar em inglês": o i18next usa o defaultValue
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

    # formas de plural em pt-BR: o i18next acrescenta o sufixo à chave quando
    # o app passa count, então _one/_other chegam à tela mesmo sem existir no
    # catálogo inglês. Chave sem count nunca pede sufixo — é erro.
    plural_added, plural_stray, plural_broken = 0, [], []
    for base, forms in plurals.items():
        if base not in source:
            raise SystemExit(f"formas de plural para chave inexistente: {base}")
        if candidates and base not in candidates:
            plural_stray.append(base)
        english = decode_js(source[base])
        want = sorted(PLACEHOLDER_RE.findall(english))
        for form, value in forms.items():
            if form not in PLURAL_FORMS:
                raise SystemExit(f"forma de plural desconhecida {form!r} na chave {base}")
            if sorted(PLACEHOLDER_RE.findall(value)) != want:
                plural_broken.append(f"{base}_{form}")
            translated[f"{base}_{form}"] = value
            plural_added += 1

    if plural_broken:
        raise SystemExit(
            "placeholders das formas de plural não batem com o original: " + ", ".join(plural_broken[:5])
        )

    # placeholders precisam bater, senão a tela mostra vazio no lugar do valor —
    # exceto o sufixo de plural do inglês, que em português se joga fora
    broken, dropped_suffix = [], []
    for key, value in translated.items():
        if key not in source:
            continue  # forma de plural: sem original próprio, checada acima
        english = decode_js(source[key])
        want = sorted(PLACEHOLDER_RE.findall(english))
        got = sorted(PLACEHOLDER_RE.findall(value))
        if want == got:
            continue
        suffixes = set(PLURAL_SUFFIX_RE.findall(english))
        if suffixes and sorted(p for p in want if p not in suffixes) == got:
            dropped_suffix.append(key)
        else:
            broken.append(key)

    # sufixo deixado na tradução desenha "etiquetas: 3s" na tela
    kept_suffix = [
        key for key, value in translated.items()
        if key in source
        and set(PLURAL_SUFFIX_RE.findall(decode_js(source[key]))) & set(PLACEHOLDER_RE.findall(value))
    ]

    too_long = [k for k, v in translated.items() if len(v) > MAX_VALUE_LENGTH]
    if too_long:
        raise SystemExit(f"tradução além de {MAX_VALUE_LENGTH} caracteres rejeitaria o pacote: {too_long[:3]}")

    # glossário: warnings apenas — decisão humana, não trava o build
    verbatim, banned = load_glossary()
    glossary_warnings = []
    for key, value in translated.items():
        if key not in source:
            continue
        english = decode_js(source[key])
        for term in verbatim:
            # s?: plural em inglês/português ("workspaces") não é desvio
            pat = rf"\b{re.escape(term)}(?:s|es)?\b"
            if (re.search(pat, english, re.I)
                    and not re.search(pat, value, re.I)):
                glossary_warnings.append(f"{key}: termo {term!r} sumiu — en: {english!r} → pt: {value!r}")
        for term, wrongs in banned.items():
            if any(w in value.lower() for w in wrongs):
                glossary_warnings.append(f"{key}: renderização proibida de {term!r}: {value!r}")

    catalog = nest(translated)

    try:
        version = open(os.path.join(ROOT, "ORCA_VERSION")).read().strip()
    except FileNotFoundError:
        version = "desconhecida"

    total = len(source)
    # formas de plural não entram no denominador: não existem chave própria no catálogo
    from_catalog = sum(1 for key in translated if key in source)
    missing_texts = sorted(set(missing_keys.values()))
    pend = Counter(lane_of(k) for k in missing_keys)
    pend_bytes = Counter()
    for k in missing_keys:
        pend_bytes[lane_of(k)] += len(missing_keys[k])

    print(f"\nversão da Orca:          {version}")
    print(f"total de chaves:         {total}")
    print(f"traduzido:               {from_catalog} ({from_catalog * 100 // total}%)")
    print(f"protegido pelo Orca:     {len(skipped)} (ficam em inglês — é normal)")
    print(f"overrides por chave:     {overridden} (contexto importa mais que o dicionário)")
    print(f"acima de 8192:           {len(oversized)} (blocos CSS, rejeitariam o pacote)")
    print(f"sem tradução:            {len(missing_texts)}")
    print(f"divergências de placeholder: {len(broken)}")
    print(f"sufixos de plural:       {len(dropped_suffix)} descartados · {len(kept_suffix)} mantidos (deve ser 0)")
    print(f"formas de plural:        {plural_added} registros para {len(plurals)} chaves "
          f"(candidatas sem forma: {len(candidates - set(plurals)) if candidates else 0})")
    print("pendências por lane:     " + " · ".join(f"{k}={v}" for k, v in sorted(pend.items(), key=lambda x: -x[1])))
    print("bytes EN pendentes/lane (teto 60k p/ dividir lane): "
          + " · ".join(f"{k}={v}" for k, v in sorted(pend_bytes.items(), key=lambda x: -x[1])))
    print(f"profundidade:            {depth(catalog)}/16 · entradas {len(translated)}/20000")

    if plural_stray:
        print(f"\nFORMAS DE PLURAL EM CHAVES SEM count ({len(plural_stray)}) — o i18next não as pede:")
        for key in plural_stray[:10]:
            print(f"  {key}")

    if kept_suffix:
        print(f"\nSUFIXO DE PLURAL INGLÊS NA TRADUÇÃO ({len(kept_suffix)}) — sairia \"etiquetas: 3s\":")
        for key in kept_suffix[:20]:
            print(f"  en: {decode_js(source[key])!r}\n  pt: {translated[key]!r}")

    if broken:
        print("\nDIVERGÊNCIAS DE PLACEHOLDER (a tradução perde o valor):")
        for key in broken[:20]:
            print(f"  {key}\n    en: {decode_js(source[key])!r}\n    pt: {translated[key]!r}")

    if missing_texts:
        print(f"\nSEM TRADUÇÃO ({len(missing_texts)}) — acrescente em tools/dict/*.json:")
        for text in missing_texts[:40]:
            print(f"  {text!r}")

    if glossary_warnings:
        print(f"\nAVISOS DE GLOSSÁRIO ({len(glossary_warnings)} — não bloqueiam):")
        for w in glossary_warnings[:30]:
            print(f"  {w}")

    if depth(catalog) > 16:
        raise SystemExit(f"profundidade {depth(catalog)} > 16 rejeitaria o pacote")
    if len(translated) > 20000:
        raise SystemExit(f"{len(translated)} entradas > 20000 rejeitariam o pacote")
    if broken:
        raise SystemExit(f"{len(broken)} divergências de placeholder bloqueiam o build (relatório acima)")

    out = os.path.join(ROOT, "locales", "pt-BR.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(catalog, open(out, "w"), ensure_ascii=False, indent=1)
    print(f"\nescrito: {out}")


main()
