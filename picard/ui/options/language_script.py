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

from operator import itemgetter
from picard import config
from picard.ui.options import OptionsPage, register_options_page
from picard.ui.ui_options_language_script import Ui_LanguageScriptOptionsPage
from picard.const import ALIAS_LOCALES, MB_LANGUAGES, MB_SCRIPTS


class LanguageScriptOptionsPage(OptionsPage):

    NAME = "language_script"
    TITLE = N_("Language/Script")
    PARENT = "metadata"
    SORT_ORDER = 0
    ACTIVE = True

    options = [
        config.TextOption("setting", "preferred_language", ""),
        config.TextOption("setting", "preferred_script", ""),
        config.TextOption("setting", "artist_locale", u"en"),
    ]

    def __init__(self, parent=None):
        super(LanguageScriptOptionsPage, self).__init__(parent)
        self.ui = Ui_LanguageScriptOptionsPage()
        self.ui.setupUi(self)

    def load(self):
        language_combo_box = self.ui.preferred_language
        language_combo_box.addItem('', '')

        for i, (iso_code, name) in enumerate(sorted(MB_LANGUAGES.iteritems(), key=itemgetter(1))):
            language_combo_box.addItem(name, iso_code)
            if iso_code == config.setting["preferred_language"]:
                language_combo_box.setCurrentIndex(i + 1)

        script_combo_box = self.ui.preferred_script
        script_combo_box.addItem('', '')

        for i, (iso_code, name) in enumerate(sorted(MB_SCRIPTS.iteritems(), key=itemgetter(1))):
            script_combo_box.addItem(name, iso_code)
            if iso_code == config.setting["preferred_script"]:
                script_combo_box.setCurrentIndex(i + 1)

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
        for name in ('preferred_language', 'preferred_script', 'artist_locale'):
            combo_box = getattr(self.ui, name)
            config.setting[name] = combo_box.itemData(combo_box.currentIndex())


register_options_page(LanguageScriptOptionsPage)
