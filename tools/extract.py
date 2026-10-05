#!/usr/bin/env python3
"""Constrói o mapa "chave i18next → texto inglês" para a Orca instalada.

Duas fontes, e a ordem importa:

1. `src/renderer/src/i18n/locales/en.json` do repositório da Orca — buscado
   pela tag da versão instalada (`ORCA_VERSION`), nunca de `main`.
   Chave adicionada em `main` mas ainda não lançada quebra o pacote de idioma
   de todo mundo: o validador da release não a conhece e rejeita o catálogo
   inteiro. Catálogo da release: 15007 chaves para 1.4.220.

2. Varredura do `app.asar` — rede de segurança: acrescenta chaves que não
   estão no catálogo da tag (no passado, termos de busca das configurações
   declarados via `translateSearchKeyword`; desde o PR stablyai/orca#18040
   vêm pelo catálogo e o acréscimo é zero). Catálogo da tag é a fonte
   principal: o regex do asar só acha chaves com prefixo `auto.` e deixa
   de fora ~1850 chaves.

Resultado: en-all.json ao lado do script (derivado, no .gitignore) e
ORCA_VERSION na raiz. Também é reconstruído o allowed-chrome.txt — lista
branca da zona protegida, comum a todo o intervalo suportado (limite
inferior = arquivo COMPAT).
"""
import base64
import json
import os
import plistlib
import re
import subprocess
import sys

DEFAULT_ASAR = "/Applications/Orca.app/Contents/Resources/app.asar"
CATALOG_PATH = "src/renderer/src/i18n/locales/en.json"
CHROME_PATH = "src/shared/plugins/plugin-translatable-chrome.ts"
REPO = "stablyai/orca"
CHROME_RE = re.compile(r"'(auto\.components\.settings\.[A-Za-z0-9_.]+)'")
# Aspas duplas ou crase: desde 1.4.195 o bundle é minificado com mais força,
# parte das chamadas foi para literais de template e o nome da função virou
# alias de uma letra.
PAIR = re.compile(r'(["`])(auto\.[A-Za-z0-9_.]{3,90})\1\s*,\s*(["`])((?:[^"`\\]|\\.){1,300})\3')
# Chamada translate(chave, defaultValue, { count }) — só nessas chaves o
# i18next insere o sufixo de plural pelas regras do idioma, e as formas
# _one/_other do nosso catálogo valem.
COUNT_CALL = re.compile(r'\b\w+\(("`)([A-Za-z0-9_.\-]+)\1\s*,\s*(["`])(?:[^"`\\]|\\.){0,300}\3\s*,\s*\{\s*count')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def orca_version(asar: str) -> str | None:
    """A versão vem do Info.plist do mesmo bundle — catálogo e versão não podem se separar."""
    plist = os.path.join(os.path.dirname(asar), os.pardir, "Info.plist")
    try:
        with open(plist, "rb") as f:
            return plistlib.load(f).get("CFBundleShortVersionString")
    except (OSError, plistlib.InvalidFileException):
        return None


def fetch_file(path: str, version: str) -> bytes:
    """Busca o arquivo da tag via gh — o python3 do macOS de sistema não tem raízes de certificado."""
    ref = f"v{version}"
    try:
        raw = subprocess.run(
            ["gh", "api", f"repos/{REPO}/contents/{path}?ref={ref}", "--jq", ".content"],
            capture_output=True, text=True, check=True, timeout=120,
        ).stdout
    except FileNotFoundError:
        sys.exit("necessário gh CLI: brew install gh && gh auth login")
    except subprocess.CalledProcessError as err:
        sys.exit(f"não foi possível obter {path} na tag {ref}:\n{err.stderr.strip()}")
    return base64.b64decode(raw)


def fetch_catalog(version: str) -> dict:
    return json.loads(fetch_file(CATALOG_PATH, version))


def fetch_allowed_chrome(version: str) -> set[str]:
    """Caminhos da zona protegida que ESTA versão permite traduzir."""
    return set(CHROME_RE.findall(fetch_file(CHROME_PATH, version).decode("utf-8")))


def compat_floor() -> str:
    """Menor versão da Orca em que o pacote precisa funcionar (arquivo COMPAT)."""
    with open(os.path.join(ROOT, "COMPAT")) as f:
        return f.read().strip()


def flatten(node: dict, prefix: str = "") -> dict:
    """O en.json é aninhado; nós trabalhamos com chaves planas por ponto."""
    out = {}
    for key, value in node.items():
        if isinstance(value, dict):
            out.update(flatten(value, f"{prefix}{key}."))
        else:
            out[f"{prefix}{key}"] = value
    return out


def scan_asar(asar: str) -> dict:
    """O texto inglês está no bundle como defaultValue: translate("auto.<chave>", "English")."""
    raw = open(asar, "rb").read().decode("utf-8", "ignore")
    pairs: dict[str, str] = {}
    for _, key, _, value in PAIR.findall(raw):
        # valor é literal JS: aspas e barras estão escapadas
        value = value.replace('\\"', '"').replace("\\\\", "\\").replace("\\n", "\n")
        # a mesma chave pode aparecer em vários bundles (renderer/web) —
        # fica a variante mais longa, ela é mais completa
        if key not in pairs or len(value) > len(pairs[key]):
            pairs[key] = value
    return pairs


def scan_plural_candidates(asar: str) -> set[str]:
    """Chaves que recebem count sem levar o sufixo de plural embutido na chave.

    Nelas o i18next acrescenta o sufixo sozinho — pelas regras do idioma
    corrente. O pt-BR pede só _one/_other, que existem no inglês também, mas
    a lista serve para o build validar formas acrescentadas por nós.
    """
    raw = open(asar, "rb").read().decode("utf-8", "ignore")
    keys = {key for _, key, _ in COUNT_CALL.findall(raw)}
    return {k for k in keys if not re.search(r"_(one|few|many|other)$", k)}


def main() -> None:
    asar = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ASAR
    if not os.path.exists(asar):
        sys.exit(f"não encontrado {asar}\nespecifique o caminho: python3 extract.py /path/to/app.asar")

    version = orca_version(asar)
    if not version:
        sys.exit("não foi possível ler a versão do Info.plist junto ao asar")

    catalog = flatten(fetch_catalog(version))
    print(f"catálogo da tag v{version}: {len(catalog)} chaves")

    # A lista branca da zona protegida é a INTERSEÇÃO da versão mínima
    # suportada e da instalada. Caminho permitido na Orca nova mas ainda
    # protegido na velha rejeitaria o catálogo inteiro para quem não
    # atualizou — e a atualização do pacote chega antes da do aplicativo.
    floor = compat_floor()
    allowed = fetch_allowed_chrome(floor)
    if floor != version:
        allowed &= fetch_allowed_chrome(version)
    chrome_path = os.path.join(HERE, "allowed-chrome.txt")
    open(chrome_path, "w").write("\n".join(sorted(allowed)) + "\n")
    print(f"zona protegida:       {len(allowed)} caminhos permitidos "
          f"(interseção v{floor} … v{version})")

    candidates = scan_plural_candidates(asar)
    cand_path = os.path.join(HERE, "plural-candidates.txt")
    open(cand_path, "w").write("\n".join(sorted(candidates)) + "\n")
    print(f"formas de plural:     {len(candidates)} chaves recebem count "
          f"(sufixo vem do i18next)")

    bundle = scan_asar(asar)
    extra = {k: v for k, v in bundle.items() if k not in catalog}
    print(f"adicionados do app.asar: {len(extra)} (fora do catálogo da tag)")

    pairs = {**catalog, **extra}
    out = os.path.join(HERE, "en-all.json")
    json.dump(pairs, open(out, "w"), ensure_ascii=False, indent=1)
    open(os.path.join(ROOT, "ORCA_VERSION"), "w").write(version + "\n")
    print(f"\ntotal {len(pairs)} chaves → {out}")
    print(f"versão da Orca: {version} → ORCA_VERSION")


main()
