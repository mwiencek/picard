# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
# Copyright (C) 2007 Lukáš Lalinský
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

import sys
from PyQt4 import QtCore, QtGui
from picard import config
from picard.const import MB_LANGUAGES, MB_SCRIPTS
from picard.util import find_existing_path, icontheme


class StandardButton(QtGui.QPushButton):

    OK = 0
    CANCEL = 1
    HELP = 2

    __types = {
        OK: (N_('&Ok'), 'SP_DialogOkButton'),
        CANCEL: (N_('&Cancel'), 'SP_DialogCancelButton'),
        HELP: (N_('&Help'), 'SP_DialogHelpButton'),
    }

    def __init__(self, btntype):
        label = _(self.__types[btntype][0])
        args = [label]
        if sys.platform != 'win32' and sys.platform != 'darwin':
            iconname = self.__types[btntype][1]
            if hasattr(QtGui.QStyle, iconname):
                icon = self.tagger.style().standardIcon(getattr(QtGui.QStyle, iconname))
                args = [icon, label]
        QtGui.QPushButton.__init__(self, *args)


# The following code is there to fix
# http://tickets.musicbrainz.org/browse/PICARD-417
# In some older version of PyQt/sip it's impossible to connect a signal
# emitting an `int` to a slot expecting a `bool`.
# By using `enabledSlot` instead we can force python to do the
# conversion from int (`state`) to bool.
def enabledSlot(func, state):
    """Calls `func` with `state`."""
    func(state)


def find_starting_directory():
    if config.setting["starting_directory"]:
        path = config.setting["starting_directory_path"]
    else:
        path = config.persist["current_directory"] or QtCore.QDir.homePath()
    return find_existing_path(unicode(path))


class ButtonLineEdit(QtGui.QLineEdit):

    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)

        self.clear_button = QtGui.QToolButton(self)
        self.clear_button.setVisible(False)
        self.clear_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.clear_button.setFocusPolicy(QtCore.Qt.NoFocus)
        fallback_icon = icontheme.lookup('edit-clear', icontheme.ICON_SIZE_TOOLBAR)
        self.clear_button.setIcon(QtGui.QIcon.fromTheme("edit-clear",
                                                        fallback_icon))
        self.clear_button.setStyleSheet(
            "QToolButton { background: transparent; border: none;} QToolButton QWidget { color: black;}")
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(self.clear_button, 0, QtCore.Qt.AlignRight)

        layout.setSpacing(0)
        layout.setMargin(5)
        self.clear_button.setToolTip(_("Clear entry"))
        self.clear_button.clicked.connect(self.clear)
        self.textChanged.connect(self._update_clear_button)
        self._margins = self.getTextMargins()

    def _update_clear_button(self, text):
        self.clear_button.setVisible(text != "")
        left, top, right, bottom = self._margins
        self.setTextMargins(left, top, right + self.clear_button.width(), bottom)


def language_script_label(item, language_fallback=None, script_fallback=None):
    # Can't use _() in kwargs
    return '%s / %s' % (_(MB_LANGUAGES.get(item['language'])) or language_fallback or _('[no language]'),
                        _(MB_SCRIPTS.get(item['script'])) or script_fallback or _('[no script]'))
