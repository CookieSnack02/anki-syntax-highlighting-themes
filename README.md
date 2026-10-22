# Syntax Highlighting (NG) — Temas · Add-on para Anki

Insira **código com destaque de sintaxe** nos campos das suas notas do Anki e escolha o
**tema de cores**: Monokai, GitHub Dark/Light, One Dark/Light, VS Code Dark+/Light+,
Dracula, Tokyo Night, Catppuccin Mocha, Nord, Gruvbox, Solarized, Material, Night Owl,
Zenburn, Xcode… e todos os estilos do [Pygments](https://pygments.org/styles/)
(56 temas no total e cerca de 600 linguagens).

Este projeto é uma atualização do
[cav71/syntax-highlighting-ng](https://github.com/cav71/syntax-highlighting-ng), que tinha
parado de funcionar nas versões atuais do Anki.

| | |
|---|---|
| **Versão do add-on** | 1.2.0 |
| **Anki testado** | 26.9.3 (editor legado e editor novo) e 25.9.2 |
| **Anki mínimo** | 2.1.55 |
| **Sistemas** | Testado no Windows. É Python puro, sem dependências nativas, então deve funcionar também no macOS e no Linux (não testado) |
| **Licença** | GNU AGPLv3 |

---

## Sumário

1. [Instalação](#1-instalação)
2. [Primeiro uso](#2-primeiro-uso)
3. [Escolhendo o tema](#3-escolhendo-o-tema)
4. [Opções](#4-opções)
5. [Celular (AnkiDroid / AnkiMobile)](#5-celular-ankidroid--ankimobile)
6. [Atualizar e desinstalar](#6-atualizar-e-desinstalar)
7. [Solução de problemas](#7-solução-de-problemas)
8. [Para desenvolvedores](#8-para-desenvolvedores)
9. [O que mudou em relação ao original](#9-o-que-mudou-em-relação-ao-original)
10. [Créditos e licença](#10-créditos-e-licença)

---

## 1. Instalação

### Opção A — Baixar o arquivo pronto (recomendado)

1. **Baixe o add-on:**
   [syntax_highlighting_ng.ankiaddon](https://github.com/CookieSnack02/anki-syntax-highlighting-themes/releases/latest/download/syntax_highlighting_ng.ankiaddon)
   (ou abra a página [Releases](https://github.com/CookieSnack02/anki-syntax-highlighting-themes/releases)
   e baixe o `.ankiaddon` da versão mais recente).
2. **Instale no Anki** de um destes jeitos:
   - **Dois cliques** no arquivo baixado (com o Anki instalado, ele abre o instalador); **ou**
   - No Anki: **Ferramentas → Complementos → Instalar a partir de arquivo…** e escolha o
     arquivo baixado.
3. Confirme a instalação na janela que aparecer.
4. **Feche o Anki completamente e abra de novo.** O add-on só é carregado na inicialização.

> **Já tem o *Syntax Highlighting* antigo instalado?** Ele conflita com este. Em
> **Ferramentas → Complementos**, selecione o antigo e clique em **Desativar** (ou
> **Excluir**). O Anki também avisa sobre o conflito ao instalar.

### Opção B — Gerar o pacote a partir do código

Precisa de **Python 3.9+** e **Git**.

```bash
git clone https://github.com/CookieSnack02/anki-syntax-highlighting-themes.git
cd anki-syntax-highlighting-themes
python build.py
```

O arquivo `dist/syntax_highlighting_ng.ankiaddon` é criado. Instale-o como no passo 2 da
Opção A.

### Opção C — Copiar a pasta manualmente

1. No Anki: **Ferramentas → Complementos → Ver arquivos**. Abre a pasta `addons21`.
   (Caminhos padrão: Windows `%APPDATA%\Anki2\addons21`, macOS
   `~/Library/Application Support/Anki2/addons21`, Linux `~/.local/share/Anki2/addons21`.)
2. Feche o Anki.
3. Copie a pasta `src/syntax_highlighting_ng` deste repositório para dentro de `addons21`
   (o resultado deve ser `addons21/syntax_highlighting_ng/__init__.py`).
4. Abra o Anki.

### Como confirmar que deu certo

- Em **Ferramentas** aparece o item **Syntax Highlighting (temas)…**.
- Ao abrir **Adicionar** (ou **Editar**), a barra do editor mostra um botão **CH** e duas
  listas: **linguagem** e **tema**.

---

## 2. Primeiro uso

1. Abra **Adicionar** (ou edite uma nota existente).
2. **Clique no campo** onde o código deve entrar (por exemplo, *Verso*).
3. Na lista de **linguagem** da barra, escolha a linguagem do código (ex.: *Python*).
4. Insira o código de um destes jeitos:
   - **Pela área de transferência:** copie o código de qualquer lugar (`Ctrl+C`), volte ao
     campo e clique em **CH** (ou pressione **`Alt+S`**); **ou**
   - **Pela seleção:** cole o código como texto simples no campo, selecione-o e clique em
     **CH** (ou **`Alt+S`**). O texto selecionado é trocado pelo bloco destacado.
5. O bloco aparece com cores, fundo do tema e números de linha. Continue digitando abaixo
   dele normalmente.

**Errou o código? Ctrl+Z.** A inserção entra no histórico de desfazer do editor: um
`Ctrl+Z` logo depois remove o bloco e devolve o campo como estava (inclusive o texto que
estava selecionado). Vale também para a troca de tema/linguagem de um bloco (seção 3).

Dicas:

- A linguagem escolhida fica **memorizada por baralho** (dá para desligar nas opções).
- Para refazer um bloco com outro código, basta `Ctrl+Z` e inserir de novo.
- Sequências que o Anki usa em modelos, como `{{`, `}}` e `::`, são protegidas
  automaticamente, então o código não quebra os seus cartões (nem os *cloze*).

---

## 3. Escolhendo o tema

Há dois lugares para trocar o tema:

- **Na barra do editor:** a segunda lista. Ao escolher, aparece a mensagem
  *"Tema: …"* e o próximo bloco inserido já usa o tema novo.
- **Em Ferramentas → Syntax Highlighting (temas)…:** a janela de opções tem uma
  **pré-visualização ao vivo** do tema com código de exemplo da linguagem escolhida.

### Trocar o tema de um bloco que já está na nota

O bloco é **alterado no lugar**: ele não ganha um segundo bloco por cima, o código e a
numeração de linhas continuam iguais, e só as cores mudam.

1. Clique **dentro do bloco** (ou selecione um trecho que inclua um ou mais blocos).
2. Escolha o novo tema na lista da barra. Aparece *"Tema … aplicado ao bloco"*.

Do mesmo jeito:

- **Trocar a linguagem do bloco:** clique dentro dele e escolha outra linguagem na lista.
  O bloco é destacado de novo com a linguagem nova e mantém o tema.
- **Botão CH (ou `Alt+S`) com o cursor dentro de um bloco:** aplica ao bloco o tema
  atual da barra, em vez de inserir um bloco novo.
- **Desfazer:** `Ctrl+Z` volta o tema/linguagem anterior.

Isso também funciona com blocos criados pelas versões 1.0 e 1.1 do add-on. Edições que
você tenha feito no texto do código dentro do bloco são mantidas.

Temas em destaque (aparecem primeiro na lista):

| Escuros | Claros |
|---|---|
| Monokai *(padrão)* · GitHub Dark · One Dark · VS Code Dark+ · Dracula · Tokyo Night · Catppuccin Mocha · Nord · Gruvbox Dark · Solarized Dark · Material · Night Owl · Zenburn | GitHub Light · One Light · VS Code Light+ · Gruvbox Light · Solarized Light · Xcode · Visual Studio · Pygments Default |

Os demais estilos do Pygments aparecem depois de um separador. Para ver todos lado a lado,
rode `python build.py` e abra `dist/temas.html` no navegador.

---

## 4. Opções

### Ferramentas → Syntax Highlighting (temas)…

Também abre pelo botão **Config** do add-on em **Ferramentas → Complementos**.
Estas opções **sincronizam com a sua conta AnkiWeb** junto com a coleção.

| Opção | O que faz |
|---|---|
| **Tema** | Tema dos próximos blocos. |
| **Linguagem padrão** | Linguagem usada quando não há uma memorizada para o baralho. |
| **Mostrar números de linha** | Liga/desliga a numeração. |
| **Centralizar blocos de código** | Centraliza o bloco no cartão. |
| **Usar classes CSS** *(avançado)* | Em vez de cores embutidas, gera classes CSS (notas menores). Exige colar o CSS do tema no tipo de nota — veja abaixo. |
| **Lembrar a última linguagem usada em cada baralho** | Memoriza a linguagem por baralho. |
| **Copiar CSS do tema** | Copia o CSS do tema selecionado para a área de transferência. |

**Modo classes CSS, passo a passo:**

1. Marque **Usar classes CSS** e escolha o tema.
2. Clique em **Copiar CSS do tema**.
3. Vá em **Ferramentas → Gerenciar tipos de nota → (seu tipo) → Cartões… → Estilo** e
   cole o CSS no final.
4. Repita o passo 3 para cada tipo de nota em que usar código. Cada tema usa a sua própria
   classe (`.sh-monokai`, `.sh-dracula`, …), então vários temas podem coexistir.

### Opções locais (`config.json`)

Ficam no arquivo `config.json` do add-on. Como o botão **Config** abre a janela de opções
acima, edite o arquivo assim: **Ferramentas → Complementos**, selecione o add-on →
**Ver arquivos**, feche o Anki e abra `config.json` num editor de texto. Estas opções não
sincronizam e só valem depois de reiniciar o Anki.

| Chave | Padrão | Descrição |
|---|---|---|
| `hotkey` | `"Alt+S"` | Atalho para inserir o código destacado. |
| `limitToLangs` | `[]` | Limita a lista de linguagens. Ex.: `["Python", "Java", "JavaScript", "SQL"]`. |
| `showThemeSelector` | `true` | Mostra a lista de temas na barra do editor. |

---

## 5. Celular (AnkiDroid / AnkiMobile)

O add-on roda só no **Anki para computador**, mas os blocos criados funcionam em qualquer
lugar: as cores ficam embutidas no HTML da nota, então aparecem iguais no **AnkiDroid**, no
**AnkiMobile** e no **AnkiWeb** depois de sincronizar. (No modo *classes CSS*, o CSS precisa
estar no tipo de nota, que também sincroniza.)

---

## 6. Atualizar e desinstalar

- **Atualizar:** baixe o `.ankiaddon` novo em
  [Releases](https://github.com/CookieSnack02/anki-syntax-highlighting-themes/releases),
  instale por cima (mesmos passos da instalação) e reinicie o Anki. Suas opções são mantidas.
- **Vindo da 1.0 ou da 1.1 no Windows (uma vez só):** essas versões deixam um arquivo do
  add-on travado enquanto o Anki está aberto, e instalar por cima falha com
  *"O arquivo já está sendo usado por outro processo: …pygments-2.21.0-py3-none-any.whl"*.
  Para atualizar:
  1. **Feche o Anki.**
  2. Abra a pasta `%APPDATA%\Anki2\addons21` (cole o caminho na barra do Explorador de
     Arquivos) e **apague a pasta `syntax_highlighting_ng`**.
  3. Instale o `.ankiaddon` novo (dois cliques) e reinicie o Anki.

  As opções de tema, linguagem etc. ficam salvas na sua coleção e não se perdem; apenas o
  `config.json` (atalho, `limitToLangs`), se você o tiver editado, volta ao padrão. A partir
  da 1.2.0 a atualização funciona normalmente com o Anki aberto.
- **Desinstalar:** **Ferramentas → Complementos**, selecione
  *Syntax Highlighting (NG) — Temas* → **Excluir**, e reinicie. Os blocos já inseridos
  continuam nas notas, pois são HTML comum.

---

## 7. Solução de problemas

| Sintoma | Causa provável / solução |
|---|---|
| O botão **CH** e as listas não aparecem | O Anki não foi reiniciado após instalar, ou o add-on está desativado em **Ferramentas → Complementos**. |
| Aviso de conflito ao instalar | O *Syntax Highlighting* antigo está instalado: desative-o ou exclua-o. |
| Erro ao instalar por cima: *"O arquivo já está sendo usado por outro processo"* (`pygments-…whl`) | Acontece ao atualizar a partir da 1.0/1.1 no Windows. Siga o passo único da seção 6 (fechar o Anki e apagar a pasta antes de instalar). Depois disso, o botão CH pode ficar sem ícone até a reinstalação, porque a tentativa interrompida apaga parte dos arquivos. |
| *"Clique em um campo antes de inserir o código."* | Clique dentro de um campo da nota antes de usar **CH**/**Alt+S**. |
| *"Nada para destacar…"* | Não havia texto selecionado nem texto na área de transferência. |
| Escolhi outro tema e o bloco existente não mudou | Clique **dentro** do bloco antes de escolher o tema (seção 3). Sem o cursor num bloco, o tema vale para os próximos blocos. Requer a versão 1.2.0 ou maior. |
| Ctrl+Z não remove o bloco | Use o `Ctrl+Z` com o cursor no campo, antes de digitar outra coisa. Requer a versão 1.2.0 ou maior: nas anteriores, depois de usar uma lista da barra, a inserção podia ir para o lugar errado. |
| Blocos sem cor no modo *classes CSS* | Falta colar o CSS do tema no tipo de nota (seção 4). |
| O tema escolhido não "pega" | Confirme a versão em **Ferramentas → Complementos** (use a mais recente). A 1.0.0 tinha um bug no Anki 26 com o editor novo. |
| Editor novo do Anki 26 | Suportado. Ele abre com `Shift` ao clicar em Adicionar/Editar ou com o experimento *Svelte editor* ligado; o add-on funciona nele e no legado. |

**Onde fica o log:** **Ferramentas → Complementos → Ver arquivos**, depois suba uma pasta e
abra `logs/addons/syntax_highlighting_ng/syntax_highlighting_ng.log`. A cada inicialização
deve aparecer uma linha `addon syntax_highlighting_ng loaded pygments 2.21.0`. Se pedir
ajuda em uma *issue*, anexe esse arquivo e a versão do Anki (**Ajuda → Sobre**).

---

## 8. Para desenvolvedores

Estrutura:

```
src/syntax_highlighting_ng/   o add-on (é o conteúdo do .ankiaddon)
  __init__.py                 ponto de entrada; põe o Pygments embutido no sys.path
  main.py                     integração com o Anki (barra do editor, hooks, inserção)
  editor.js                   lado JS no editor: foco/seleção, blocos sob o cursor,
                              inserção e substituição via pasteHTML (desfazível)
  html_render.py              renderização pura (sem Anki), testável
  themes.py                   catálogo de temas + temas próprios
  options.py / samples.py     janela de opções com pré-visualização
  config.py                   opções sincronizadas (col.get_config/set_config)
  libs/pygments/              Pygments 2.21.0 embutido (pasta, licença BSD)
tests/test_render.py          testes de renderização (pytest, sem Anki)
tests/anki_smoke.py           smoke test dentro de um Anki instalado (legado + novo editor)
tests/e2e/                    teste ponta a ponta num Anki real, controlado via DevTools
build.py                      gera dist/*.ankiaddon e dist/temas.html
```

Comandos:

```bash
python -m pip install pytest websocket-client
python -m pytest tests
python -I tests/anki_smoke.py
python -I tests/e2e/run.py both
python build.py
```

`tests/e2e/run.py` abre um **Anki de verdade** (os pacotes do Anki instalado, com uma
pasta-base temporária, então o seu perfil não é tocado; pode rodar com o seu Anki aberto),
instala o add-on de `src/`, abre *Adicionar* e controla o editor pelo DevTools
(porta 9333): inserir, `Ctrl+Z`, trocar tema/linguagem de blocos existentes, blocos de
versões antigas. Use `legacy`, `new` ou `both` (os dois editores do Anki 26). A janela do
Anki aparece durante o teste.

`tests/anki_smoke.py` carrega o add-on dentro dos pacotes do Anki instalado (padrão:
`%LOCALAPPDATA%/Programs/Anki/app_packages`, do instalador oficial do Anki 26 no Windows).
Precisa de um Python **3.13**, a mesma versão do Anki, porque o Anki 26 distribui só
bytecode. Para outra instalação, passe a pasta de pacotes como argumento, ex.:
`python tests/anki_smoke.py "%LOCALAPPDATA%/AnkiProgramFiles/.venv/Lib/site-packages"`.

Para adicionar um tema, crie uma classe em `themes.py` usando `_palette(...)`, registre-a
em `CUSTOM_STYLES` e, se quiser destaque, em `FEATURED`.

---

## 9. O que mudou em relação ao original

- **Hooks modernos** (`gui_hooks.editor_did_init_buttons`, `editor_did_init`,
  `webview_did_receive_js_message`) em vez de *monkey-patch* de `Editor.__init__` /
  `Editor.onBridgeCmd`.
- **Inserção do HTML** pela função `pasteHTML(html, internal=true)` que os dois editores
  expõem: o `document.execCommand` antigo não alcança mais os campos (que hoje ficam em
  Shadow DOM). Ela passa pelo `execCommand('insertHTML')`, então entra no histórico de
  desfazer (**Ctrl+Z**).
- **Blocos existentes são substituídos, não aninhados:** cada bloco é marcado
  (`<table class="sh-block" data-sh-lang data-sh-theme>` e números de linha com
  `class="sh-ln"`), e o código é recuperado do próprio campo para ser redesenhado com o
  tema/linguagem novos. Blocos das versões anteriores também são reconhecidos.
- **Posição do cursor guardada como caminho de nós**, não como `Range`: quando o campo
  perde o foco (ao usar uma lista da barra), o editor regrava o HTML do campo e um `Range`
  colapsaria para o início.
- **Branco e preto puros** nos estilos do bloco viram `#fefefe`/`#010101`: o
  `insertHTML` do Chromium descarta cores iguais às do editor (fundo branco, texto
  preto), e o cartão perderia essas cores, por exemplo no modo noturno.
- **Anki 26: dois editores suportados** — o legado (`aqt.editor.Editor`) e o novo
  SvelteKit (`aqt.editor.NewEditor`).
- **Listas da barra sem `onchange` inline:** o editor é servido com
  Content-Security-Policy, que bloqueia handlers inline; um listener delegado é injetado
  via `web.eval`.
- **Foco:** depois de usar uma lista da barra, o foco e a seleção voltam ao último campo
  antes de inserir o código.
- **Configuração** com `col.get_config/set_config` (`col.setMod()` e a mutação direta de
  `col.conf` não existem mais ou não persistem).
- **Pygments 2.21.0** embutido; **6 temas próprios**; números de linha esmaecidos;
  janela de opções com pré-visualização; "Copiar CSS"; classes CSS por tema
  (`.sh-<tema>`); borda sutil para temas claros.

---

## 10. Créditos e licença

- Add-on original: Tiago Barroso, Tim Rae, [Glutanimate](https://glutanimate.com/) e
  [A. Cavallo (cav71)](https://github.com/cav71/syntax-highlighting-ng).
- Destaque de sintaxe: [Pygments](https://pygments.org/) (licença BSD).
- Paletas dos temas próprios inspiradas em GitHub Primer, Atom One, VS Code, Tokyo Night e
  Catppuccin.

Distribuído sob a **GNU Affero General Public License v3** (veja [LICENSE](LICENSE)),
como o projeto original.
