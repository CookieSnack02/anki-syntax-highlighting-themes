# Changelog

## 1.1.0 — 2026-10-22

- Suporte ao Anki 26.9.3, incluindo o novo editor SvelteKit (`NewEditor`), que não tem
  `doPaste`: o código é inserido pela função `pasteHTML` da página.
- Listas de tema e de linguagem da barra funcionam de novo: o editor é servido com
  Content-Security-Policy, que bloqueava o `onchange` inline.
- O foco volta ao último campo antes de inserir o código, depois de usar uma lista da barra.
- `tests/anki_smoke.py`: smoke test dentro de um Anki instalado.

## 1.0.0 — 2026-10-21

- Atualização do cav71/syntax-highlighting-ng para o Anki atual (hooks `gui_hooks`,
  `Editor.doPaste`, `col.get_config/set_config`, Qt 6).
- Seleção de temas na barra do editor e na janela de opções, com pré-visualização.
- Seis temas próprios: GitHub Light, One Light, VS Code Dark+/Light+, Tokyo Night e
  Catppuccin Mocha.
- Pygments 2.21.0 embutido; "Copiar CSS do tema"; classes CSS por tema.
