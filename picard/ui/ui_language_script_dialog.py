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

class Ui_LanguageScriptDialog(object):
    def setupUi(self, LanguageScriptDialog):
        LanguageScriptDialog.setObjectName(_fromUtf8("LanguageScriptDialog"))
        LanguageScriptDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        LanguageScriptDialog.resize(300, 150)
        LanguageScriptDialog.setFocusPolicy(QtCore.Qt.StrongFocus)
        LanguageScriptDialog.setModal(True)
        self.verticalLayout_2 = QtGui.QVBoxLayout(LanguageScriptDialog)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.FieldsStayAtSizeHint)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.language_label = QtGui.QLabel(LanguageScriptDialog)
        self.language_label.setObjectName(_fromUtf8("language_label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.language_label)
        self.language_combo_box = QtGui.QComboBox(LanguageScriptDialog)
        self.language_combo_box.setObjectName(_fromUtf8("language_combo_box"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.language_combo_box)
        self.script_label = QtGui.QLabel(LanguageScriptDialog)
        self.script_label.setObjectName(_fromUtf8("script_label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.script_label)
        self.script_combo_box = QtGui.QComboBox(LanguageScriptDialog)
        self.script_combo_box.setObjectName(_fromUtf8("script_combo_box"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.script_combo_box)
        self.horizontalLayout.addLayout(self.formLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.buttonbox = QtGui.QDialogButtonBox(LanguageScriptDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(150)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonbox.sizePolicy().hasHeightForWidth())
        self.buttonbox.setSizePolicy(sizePolicy)
        self.buttonbox.setMinimumSize(QtCore.QSize(150, 0))
        self.buttonbox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonbox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonbox.setObjectName(_fromUtf8("buttonbox"))
        self.verticalLayout_2.addWidget(self.buttonbox)

        self.retranslateUi(LanguageScriptDialog)
        QtCore.QObject.connect(self.buttonbox, QtCore.SIGNAL(_fromUtf8("accepted()")), LanguageScriptDialog.accept)
        QtCore.QObject.connect(self.buttonbox, QtCore.SIGNAL(_fromUtf8("rejected()")), LanguageScriptDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LanguageScriptDialog)

    def retranslateUi(self, LanguageScriptDialog):
        LanguageScriptDialog.setWindowTitle(_("Preferred Language/Script"))
        self.language_label.setText(_("Language"))
        self.script_label.setText(_("Script"))

