# -*- coding: utf-8 -*-

"""
This file is part of the Syntax Highlighting add-on for Anki.

Options dialog with a live theme preview.

License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import annotations

from aqt.qt import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWebEngineView,
    QWidget,
)
from aqt.theme import theme_manager
from aqt.utils import tooltip

from . import config, html_render, themes
from .samples import SAMPLES



class SyntaxHighlightingOptions(QDialog):
    def __init__(self, parent: QWidget, languages: list[str]) -> None:
        super().__init__(parent)
        self.conf = config.get_synced()
        self.languages_map = html_render.languages()
        self.setWindowTitle("Syntax Highlighting — Opções")
        self.resize(720, 640)
        self._setup_ui(languages)
        self.update_preview()

    def _setup_ui(self, languages: list[str]) -> None:
        self.theme_combo = QComboBox()
        all_themes = themes.all_themes()
        n_featured = sum(1 for t in all_themes if t in themes.FEATURED)
        for i, theme in enumerate(all_themes):
            if i == n_featured:
                self.theme_combo.insertSeparator(self.theme_combo.count())
            self.theme_combo.addItem(theme.label, theme.key)
        self.theme_combo.setCurrentIndex(
            max(0, self.theme_combo.findData(self.conf["style"]))
        )
        self.theme_combo.currentIndexChanged.connect(self.update_preview)

        self.lang_combo = QComboBox()
        if self.conf["lang"] not in languages:
            languages = [self.conf["lang"]] + languages
        self.lang_combo.addItems(languages)
        self.lang_combo.setCurrentText(self.conf["lang"])
        self.lang_combo.currentIndexChanged.connect(self.update_preview)

        self.linenos_cb = QCheckBox("Mostrar números de linha")
        self.linenos_cb.setChecked(bool(self.conf["linenos"]))
        self.linenos_cb.stateChanged.connect(self.update_preview)

        self.center_cb = QCheckBox("Centralizar blocos de código")
        self.center_cb.setChecked(bool(self.conf["centerfragments"]))
        self.center_cb.stateChanged.connect(self.update_preview)

        self.cssclasses_cb = QCheckBox(
            "Usar classes CSS em vez de cores embutidas (avançado)"
        )
        self.cssclasses_cb.setToolTip(
            "As notas ficam menores, mas é preciso colar o CSS do tema\n"
            "no Estilo de cada tipo de nota (botão 'Copiar CSS do tema')."
        )
        self.cssclasses_cb.setChecked(bool(self.conf["cssclasses"]))

        self.perdeck_cb = QCheckBox("Lembrar a última linguagem usada em cada baralho")
        self.perdeck_cb.setChecked(bool(self.conf["defaultlangperdeck"]))

        form = QFormLayout()
        form.addRow(QLabel("<b>Tema</b>"), self.theme_combo)
        form.addRow(QLabel("<b>Linguagem padrão</b>"), self.lang_combo)

        # a plain web view: the preview is static html and needs nothing from Anki
        self.preview = QWebEngineView(self)
        self.preview.setMinimumHeight(300)

        copy_css = QPushButton("Copiar CSS do tema")
        copy_css.setToolTip("Para o modo de classes CSS: cole em Ferramentas → Tipos de nota → Cartões → Estilo")
        copy_css.clicked.connect(self.copy_css)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        bottom = QHBoxLayout()
        bottom.addWidget(copy_css)
        bottom.addStretch()
        bottom.addWidget(buttons)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(QLabel("<b>Pré-visualização</b>"))
        layout.addWidget(self.preview, 1)
        for cb in (self.linenos_cb, self.center_cb, self.cssclasses_cb, self.perdeck_cb):
            layout.addWidget(cb)
        layout.addLayout(bottom)
        self.setLayout(layout)

    def selected_theme(self) -> str:
        return self.theme_combo.currentData() or themes.DEFAULT_THEME

    def update_preview(self, *_args: object) -> None:
        lang = self.lang_combo.currentText()
        alias = self.languages_map.get(lang, "python")
        style = html_render.Style(
            language=alias,
            style=self.selected_theme(),
            linenos=self.linenos_cb.isChecked(),
            noclasses=True,  # the preview always uses inline colors
            center=self.center_cb.isChecked(),
        )
        try:
            body = html_render.render_block(SAMPLES.get(alias, SAMPLES["python"]), style)
        except html_render.RenderError as e:
            body = e.render()
        page_bg, page_fg = ("#2c2c2c", "#eeeeee") if theme_manager.night_mode else ("#ffffff", "#222222")
        self.preview.setHtml(
            '<!doctype html><html><head><meta charset="utf-8"></head>'
            f'<body style="margin: 8px; background: {page_bg}; color: {page_fg}; '
            f'font-family: sans-serif; font-size: 14px;">{body}</body></html>'
        )

    def copy_css(self) -> None:
        css = html_render.theme_css(self.selected_theme())
        QApplication.clipboard().setText(css)
        tooltip("CSS do tema copiado para a área de transferência.", parent=self)

    def accept(self) -> None:
        self.conf.update(
            style=self.selected_theme(),
            lang=self.lang_combo.currentText(),
            linenos=self.linenos_cb.isChecked(),
            centerfragments=self.center_cb.isChecked(),
            cssclasses=self.cssclasses_cb.isChecked(),
            defaultlangperdeck=self.perdeck_cb.isChecked(),
        )
        config.set_synced(self.conf)
        super().accept()

    def done(self, result: int) -> None:
        # release the web engine page with the dialog
        self.preview.deleteLater()
        super().done(result)
