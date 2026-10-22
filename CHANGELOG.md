# Changelog

## 1.2.0 — 2026-10-22

- Trocar o tema com o cursor dentro de um bloco **altera o bloco no lugar**, em vez de
  sobrepor um bloco novo. O mesmo vale para a linguagem e para o botão CH. O código, as
  edições feitas nele e a numeração de linhas são mantidos. Blocos das versões 1.0/1.1
  também são reconhecidos.
- **Ctrl+Z** desfaz a inserção (e a troca de tema/linguagem de um bloco) também depois de
  usar as listas da barra. Antes, o editor regravava o campo ao perder o foco e a inserção
  podia ir para o início do campo.
- Fundos brancos e textos pretos dos temas claros não são mais descartados pelo editor
  (`#fefefe`/`#010101`).
- Blocos marcados (`sh-block`, `data-sh-lang`, `data-sh-theme`, `sh-ln`).
- `tests/e2e/`: teste ponta a ponta num Anki real (editor legado e novo).
- Instalar uma versão nova por cima com o Anki aberto funciona no Windows: o Pygments
  agora vai como pasta (`libs/pygments/`) e não mais como `.whl`, que ficava travado pelo
  *zipimport* e fazia a instalação falhar com "arquivo em uso". Para sair da 1.0/1.1 é
  preciso, uma vez, fechar o Anki e apagar a pasta do add-on (veja o README).

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
