# orca-plugin-pt-br — Português do Brasil para o Orca (comunitário)

Pacote de idioma pt-BR para [Orca](https://github.com/stablyai/orca) (Stably ADE),
fork comunitário do [stablyai/orca-portuguese](https://github.com/stablyai/orca-portuguese)
com pipeline de contribuição paralela, glossário verificado e validação automática.
_Community pt-BR language pack for the Orca agent IDE — MIT._

Funciona com o mecanismo nativo `contributes.languagePacks`: nada é patcheado
na aplicação; chaves sem tradução caem em inglês (fallback do i18next).

**Compatível com Orca ≥ 1.4.169 · catálogo da tag v1.4.220 (ver `ORCA_VERSION`) ·
cobertura atual: 14.272/15.007 (95%)**

## Instalação

**1) Git URL** — Settings → Plugins → Install plugin → Git URL (`#ref` obrigatório):

```
https://github.com/Danil0ws/orca-plugin-pt-br.git#1.0.1
```

**2) Desenvolvimento local:**

```
git clone https://github.com/Danil0ws/orca-plugin-pt-br.git ~/orca-plugin-pt-br
```

Settings → Plugins → Development → Add path → caminho clonado.
Depois: Settings → Appearance → Language → **Português do Brasil**.

## Estrutura

```
orca-plugin.json      manifesto (id pt-br + publisher danil0ws = chave danil0ws.pt-br, engines >=1.4.169)
ORCA_VERSION          versão da Orca de onde veio o en.json (1.4.220)
COMPAT                menor versão suportada (1.4.169)
GLOSSARY.md           contrato de terminologia EN × pt-BR
UNTRANSLATED.md       por que algo ficou em inglês + dívidas abertas
locales/pt-BR.json    catálogo GERADO — não edite à mão
tools/
  extract.py          baixa en.json da tag + lista da zona protegida
  build.py            monta o catálogo dos dicionários + valida
  test_build.py       9 casos de regressão (rode antes do PR)
  lanes.json          15 lanes = 15 arquivos de dicionário = 15 PRs em paralelo
  glossary.json       espelho verificável do GLOSSARY.md (warnings no build)
  dict/*.json         FONTE DA VERDADE: pares "en" → "pt-BR" por lane
```

## Contribuir

Veja [CONTRIBUTING.md](CONTRIBUTING.md). Resumo:

```bash
python3 tools/build.py --pending <lane>   # o que falta na sua lane
# traduza em tools/dict/<lane>.json (1 PR = 1 lane), seguindo GLOSSARY.md
python3 tools/test_build.py && python3 tools/build.py   # verde = pronto
```

## Origem e licença

MIT. A tradução base veio de `stablyai/orca-portuguese` (12.524 strings);
originais em inglês © Stably AI (Orca, MIT); tooling derivado de
[imgusev/orca-plugin-ru](https://github.com/imgusev/orca-plugin-ru) (MIT).
Projeto não afiliado à Stably AI.
