# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1067, 765)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1067, 23))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionabc = QtWidgets.QAction(MainWindow)
        self.actionabc.setObjectName("actionabc")
        self.actionPVP = QtWidgets.QAction(MainWindow)
        self.actionPVP.setObjectName("actionPVP")
        self.actionPVE = QtWidgets.QAction(MainWindow)
        self.actionPVE.setObjectName("actionPVE")
        self.menu.addSeparator()
        self.menu.addAction(self.actionPVP)
        self.menu.addSeparator()
        self.menu.addAction(self.actionPVE)
        self.menu.addSeparator()
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menu.setTitle(_translate("MainWindow", "菜单"))
        self.actionabc.setText(_translate("MainWindow", "abc"))
        self.actionPVP.setText(_translate("MainWindow", "New PVP"))
        self.actionPVE.setText(_translate("MainWindow", "New PVE"))

