# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'clutcher/generated.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainFrame(object):
    def setupUi(self, MainFrame):
        MainFrame.setObjectName("MainFrame")
        MainFrame.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainFrame)
        self.centralwidget.setObjectName("centralwidget")
        MainFrame.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainFrame)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 20))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainFrame.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainFrame)
        self.statusbar.setObjectName("statusbar")
        MainFrame.setStatusBar(self.statusbar)
        self.action_Add_Files = QtWidgets.QAction(MainFrame)
        self.action_Add_Files.setObjectName("action_Add_Files")
        self.action_Exit = QtWidgets.QAction(MainFrame)
        self.action_Exit.setObjectName("action_Exit")
        self.menuFile.addAction(self.action_Add_Files)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.action_Exit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainFrame)
        QtCore.QMetaObject.connectSlotsByName(MainFrame)

    def retranslateUi(self, MainFrame):
        _translate = QtCore.QCoreApplication.translate
        MainFrame.setWindowTitle(_translate("MainFrame", "Clutcher"))
        self.menuFile.setTitle(_translate("MainFrame", "File"))
        self.action_Add_Files.setText(_translate("MainFrame", "&Open"))
        self.action_Add_Files.setShortcut(_translate("MainFrame", "Ctrl+N"))
        self.action_Exit.setText(_translate("MainFrame", "&Exit..."))
        self.action_Exit.setShortcut(_translate("MainFrame", "Ctrl+Q"))
