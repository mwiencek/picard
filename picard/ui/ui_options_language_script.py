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
        self.language_script_label = QtGui.QLabel(self.language_script_groupbox)
        self.language_script_label.setObjectName(_fromUtf8("language_script_label"))
        self.verticalLayout_3.addWidget(self.language_script_label)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.language_script_list = QtGui.QListWidget(self.language_script_groupbox)
        self.language_script_list.setObjectName(_fromUtf8("language_script_list"))
        self.horizontalLayout_4.addWidget(self.language_script_list)
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.add_language_script_button = QtGui.QPushButton(self.language_script_groupbox)
        self.add_language_script_button.setObjectName(_fromUtf8("add_language_script_button"))
        self.verticalLayout_5.addWidget(self.add_language_script_button)
        self.edit_language_script_button = QtGui.QPushButton(self.language_script_groupbox)
        self.edit_language_script_button.setObjectName(_fromUtf8("edit_language_script_button"))
        self.verticalLayout_5.addWidget(self.edit_language_script_button)
        self.remove_language_script_button = QtGui.QPushButton(self.language_script_groupbox)
        self.remove_language_script_button.setObjectName(_fromUtf8("remove_language_script_button"))
        self.verticalLayout_5.addWidget(self.remove_language_script_button)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem)
        self.horizontalLayout_4.addLayout(self.verticalLayout_5)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.artist_locale_label = QtGui.QLabel(self.language_script_groupbox)
        self.artist_locale_label.setObjectName(_fromUtf8("artist_locale_label"))
        self.verticalLayout_3.addWidget(self.artist_locale_label)
        self.artist_locale = QtGui.QComboBox(self.language_script_groupbox)
        self.artist_locale.setObjectName(_fromUtf8("artist_locale"))
        self.verticalLayout_3.addWidget(self.artist_locale)
        self.verticalLayout.addWidget(self.language_script_groupbox)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        self.verticalLayout.addItem(spacerItem1)

        self.retranslateUi(LanguageScriptOptionsPage)
        QtCore.QMetaObject.connectSlotsByName(LanguageScriptOptionsPage)

    def retranslateUi(self, LanguageScriptOptionsPage):
        self.language_script_groupbox.setTitle(_("Language/Script"))
        self.language_script_label.setText(_("Prefer releases using these languages and scripts for titles:"))
        self.add_language_script_button.setText(_("Add"))
        self.edit_language_script_button.setText(_("Edit"))
        self.remove_language_script_button.setText(_("Remove"))
        self.artist_locale_label.setText(_("Translate artist names to this locale where possible:"))

