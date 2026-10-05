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

**Dívidas ≠ decisões:** não há dívidas abertas — `python3 tools/build.py`
mostra `sem tradução: 0` e o `--pending <lane>` de cada lane vem vazio.
`python3 tools/build.py --pending <lane>` continua sendo o teste de uma lane.

**Avisos conhecidos:** nenhum. Os 25 sufixos plurais herdados do upstream
(`reaction{{value1}}`) foram corrigidos; o build reporta `mantidos (deve
ser 0)` = 0.
