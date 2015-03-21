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
from PyQt4 import QtGui
from picard import config
from picard.const import MB_LANGUAGES, MB_SCRIPTS
from picard.ui import PicardDialog
from picard.ui.ui_language_script_dialog import Ui_LanguageScriptDialog


class LanguageScriptDialog(PicardDialog):

    def __init__(self, window, parent, edit_index):
        PicardDialog.__init__(self, window)
        self.ui = Ui_LanguageScriptDialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.edit_index = edit_index
        edit_item = parent.language_script_items[self.edit_index] if edit_index is not None else None

        language_combo_box = self.ui.language_combo_box
        language_combo_box.addItem('', '')

        for i, (iso_code, name) in enumerate(sorted(MB_LANGUAGES.iteritems(), key=itemgetter(1))):
            language_combo_box.addItem(name, iso_code)
            if edit_item and iso_code == edit_item['language']:
                language_combo_box.setCurrentIndex(i + 1)

        script_combo_box = self.ui.script_combo_box
        script_combo_box.addItem('', '')

        for i, (iso_code, name) in enumerate(sorted(MB_SCRIPTS.iteritems(), key=itemgetter(1))):
            script_combo_box.addItem(name, iso_code)
            if edit_item and iso_code == edit_item['script']:
                script_combo_box.setCurrentIndex(i + 1)

    def accept(self):
        selected_language = self.ui.language_combo_box.itemData(self.ui.language_combo_box.currentIndex())
        selected_script = self.ui.script_combo_box.itemData(self.ui.script_combo_box.currentIndex())

        if selected_language or selected_script:
            for item in self.parent.language_script_items:
                if item['language'] == selected_language and item['script'] == selected_script:
                    break
            else:
                new_item = {'language': selected_language, 'script': selected_script}
                if self.edit_index is not None:
                    self.parent.language_script_items[self.edit_index] = new_item
                    self.parent.ui.language_script_list.item(self.edit_index).setText(self.parent.get_item_label(new_item))
                else:
                    self.parent.language_script_items.append(new_item)
                    self.parent.ui.language_script_list.addItem(self.parent.get_item_label(new_item))

        QtGui.QDialog.accept(self)
