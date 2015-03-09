# -*- coding: utf-8 -*-

# Automatically generated - don't edit.
# Use `python setup.py build_ui` to update it.

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_LanguageScriptOptionsPage(object):
    def setupUi(self, LanguageScriptOptionsPage):
        LanguageScriptOptionsPage.setObjectName(_fromUtf8("LanguageScriptOptionsPage"))
        LanguageScriptOptionsPage.resize(423, 553)
        self.verticalLayout = QtGui.QVBoxLayout(LanguageScriptOptionsPage)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.language_script_groupbox = QtGui.QGroupBox(LanguageScriptOptionsPage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.language_script_groupbox.sizePolicy().hasHeightForWidth())
        self.language_script_groupbox.setSizePolicy(sizePolicy)
        self.language_script_groupbox.setMinimumSize(QtCore.QSize(397, 135))
        self.language_script_groupbox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.language_script_groupbox.setObjectName(_fromUtf8("language_script_groupbox"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.language_script_groupbox)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.title_language_label = QtGui.QLabel(self.language_script_groupbox)
        self.title_language_label.setObjectName(_fromUtf8("title_language_label"))
        self.verticalLayout_3.addWidget(self.title_language_label)
        self.preferred_language = QtGui.QComboBox(self.language_script_groupbox)
        self.preferred_language.setObjectName(_fromUtf8("preferred_language"))
        self.verticalLayout_3.addWidget(self.preferred_language)
        self.title_script_label = QtGui.QLabel(self.language_script_groupbox)
        self.title_script_label.setObjectName(_fromUtf8("title_script_label"))
        self.verticalLayout_3.addWidget(self.title_script_label)
        self.preferred_script = QtGui.QComboBox(self.language_script_groupbox)
        self.preferred_script.setObjectName(_fromUtf8("preferred_script"))
        self.verticalLayout_3.addWidget(self.preferred_script)
        self.artist_locale_label = QtGui.QLabel(self.language_script_groupbox)
        self.artist_locale_label.setObjectName(_fromUtf8("artist_locale_label"))
        self.verticalLayout_3.addWidget(self.artist_locale_label)
        self.artist_locale = QtGui.QComboBox(self.language_script_groupbox)
        self.artist_locale.setObjectName(_fromUtf8("artist_locale"))
        self.verticalLayout_3.addWidget(self.artist_locale)
        self.verticalLayout.addWidget(self.language_script_groupbox)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(LanguageScriptOptionsPage)
        QtCore.QMetaObject.connectSlotsByName(LanguageScriptOptionsPage)

    def retranslateUi(self, LanguageScriptOptionsPage):
        self.language_script_groupbox.setTitle(_("Language/Script"))
        self.title_language_label.setText(_("Prefer releases using this language for titles:"))
        self.title_script_label.setText(_("Prefer releases using this script for titles:"))
        self.artist_locale_label.setText(_("Translate artist names to this locale where possible:"))

