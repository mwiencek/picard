# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
# Copyright (C) 2015 Michael Wiencek
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from picard import config
from picard.ui.options import OptionsPage, register_options_page
from picard.ui.ui_options_language_script import Ui_LanguageScriptOptionsPage
from picard.ui.language_script_dialog import LanguageScriptDialog
from picard.ui.util import language_script_label
from picard.util import load_preferred_languages_scripts
from picard.const import ALIAS_LOCALES


class LanguageScriptOptionsPage(OptionsPage):

    NAME = "language_script"
    TITLE = N_("Language/Script")
    PARENT = "metadata"
    SORT_ORDER = 0
    ACTIVE = True

    options = [
        config.ListOption("setting", "preferred_languages_scripts", []),
        config.TextOption("setting", "artist_locale", u"en"),
    ]

    def __init__(self, parent=None):
        super(LanguageScriptOptionsPage, self).__init__(parent)
        self.ui = Ui_LanguageScriptOptionsPage()
        self.ui.setupUi(self)
        self.ui.add_language_script_button.clicked.connect(self.add_language_script)
        self.ui.edit_language_script_button.clicked.connect(self.edit_language_script)
        self.ui.remove_language_script_button.clicked.connect(self.remove_language_script)
        self.language_script_items = load_preferred_languages_scripts()

    def add_language_script(self):
        LanguageScriptDialog(self.parent(), self, None).exec_()

    def edit_language_script(self):
        LanguageScriptDialog(self.parent(), self, self.ui.language_script_list.currentRow()).exec_()

    def remove_language_script(self):
        list_widget = self.ui.language_script_list
        current_row = list_widget.currentRow()
        if current_row >= 0:
            list_widget.takeItem(current_row)
            del self.language_script_items[current_row]

    def get_item_label(self, item):
        return language_script_label(
            item,
            language_fallback=_('[no preferred language]'),
            script_fallback=_('[no preferred script]')
        )

    def load(self):
        self.ui.language_script_list.addItems(map(self.get_item_label, self.language_script_items))

        artist_locale_combo_box = self.ui.artist_locale
        artist_locale_combo_box.addItem('', '')

        for i, loc in enumerate(sorted(ALIAS_LOCALES.keys())):
            name = ALIAS_LOCALES[loc]
            if "_" in loc:
                name = "    " + name
            artist_locale_combo_box.addItem(name, loc)
            if loc == config.setting["artist_locale"]:
                artist_locale_combo_box.setCurrentIndex(i + 1)

    def save(self):
        config.setting['preferred_languages_scripts'] = map(lambda x: x['language'] + '\0' + x['script'], self.language_script_items)
        config.setting['artist_locale'] = self.ui.artist_locale.itemData(self.ui.artist_locale.currentIndex())


register_options_page(LanguageScriptOptionsPage)
