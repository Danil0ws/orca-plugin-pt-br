# Por que ficou em inglês

Política + relatório. Categorias:

1. **Zona protegida** (`auto.components.settings.plugin*` fora de
   `allowed-chrome.txt`) — o validador da Orca rejeita o pacote inteiro
   (`catalog cannot replace protected security copy`); textos sobre
   confiança em plugins não podem ser substituídos. São 35 chaves;
   o build as corta sozinho.
2. **Literais** — comandos CLI, paths, placeholders, atalhos de teclado,
   nomes de produto. Ver `GLOSSARY.md`.
3. **> 8.192 caracteres** — 2 blocos CSS de vitrine; o validador
   rejeitaria o pacote inteiro.
4. **Termos consagrados** — ver `GLOSSARY.md`.

**Dívidas ≠ decisões:** strings sem tradução ainda são dívidas —
`python3 tools/build.py` mostra o total e
`python3 tools/build.py --pending <lane>` lista as pendências por lane.

**Avisos conhecidos:** 25 strings herdadas do upstream mantêm o sufixo
plural inglês (`reaction{{value1}}`) — o build avisa (`sufixos de plural
mantidos`); correção em issue aberta `[orca-ptbr]`.
