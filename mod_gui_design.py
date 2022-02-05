# -*- coding: utf-8 -*-
"""Converted PyQT Design file."""

# Form implementation generated from reading ui file 'gui_design.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets
import logging

log = logging.getLogger(__name__)


class Ui_MainWindow(object):
    """This class holds all the GUI features."""

    def setupUi(self, MainWindow):
        """Set the GUI."""
        log.debug("--setupUi--")

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(660, 535)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.pushButton_quit = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_quit.setGeometry(QtCore.QRect(20, 460, 113, 32))
        self.pushButton_quit.setObjectName("pushButton_quit")

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 0, 641, 461))
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setElideMode(QtCore.Qt.ElideRight)
        self.tabWidget.setObjectName("tabWidget")

        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")
        self.frame_box_mountpoints = QtWidgets.QFrame(self.tab_1)
        self.frame_box_mountpoints.setGeometry(QtCore.QRect(0, 0, 301, 431))
        self.frame_box_mountpoints.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_box_mountpoints.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_box_mountpoints.setObjectName("frame_box_mountpoints")
        self.label_name = QtWidgets.QLabel(self.frame_box_mountpoints)
        self.label_name.setGeometry(QtCore.QRect(10, 10, 50, 20))
        self.label_name.setObjectName("label_name")
        self.label_mounted = QtWidgets.QLabel(self.frame_box_mountpoints)
        self.label_mounted.setGeometry(QtCore.QRect(180, 10, 70, 20))
        self.label_mounted.setObjectName("label_mounted")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.frame_box_mountpoints)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 30, 281, 391))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_mountpoints = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_mountpoints.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_mountpoints.setObjectName("verticalLayout_mountpoints")

        # removed original code, moved to makeMountItem()

        self.frame_box_textwindow = QtWidgets.QFrame(self.tab_1)
        self.frame_box_textwindow.setGeometry(QtCore.QRect(300, 0, 331, 431))
        self.frame_box_textwindow.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_box_textwindow.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_box_textwindow.setObjectName("frame_box_textwindow")
        self.textBrowser = QtWidgets.QTextBrowser(self.frame_box_textwindow)
        self.textBrowser.setGeometry(QtCore.QRect(10, 10, 311, 391))
        self.textBrowser.setObjectName("textBrowser")
        self.pushButton_cleartext = QtWidgets.QPushButton(self.frame_box_textwindow)
        self.pushButton_cleartext.setGeometry(QtCore.QRect(0, 400, 81, 32))
        self.pushButton_cleartext.setObjectName("pushButton_cleartext")
        self.tabWidget.addTab(self.tab_1, "")

        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.textEdit = QtWidgets.QTextEdit(self.tab_2)
        self.textEdit.setGeometry(QtCore.QRect(0, 0, 631, 401))
        self.textEdit.setObjectName("textEdit")

        self.pushButton_save = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_save.setGeometry(QtCore.QRect(500, 400, 113, 32))
        self.pushButton_save.setObjectName("pushButton_save")

        self.pushButton_cancel = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_cancel.setGeometry(QtCore.QRect(380, 400, 113, 32))
        self.pushButton_cancel.setObjectName("pushButton_cancel")
        self.tabWidget.addTab(self.tab_2, "")

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 660, 22))
        self.menubar.setObjectName("menubar")
        self.menufile = QtWidgets.QMenu(self.menubar)
        self.menufile.setObjectName("menufile")
        self.menuabout = QtWidgets.QMenu(self.menubar)
        self.menuabout.setObjectName("menuabout")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.actionquit = QtWidgets.QAction(MainWindow)
        self.actionquit.setObjectName("actionquit")
        self.actionshow_about = QtWidgets.QAction(MainWindow)
        self.actionshow_about.setObjectName("actionshow_about")
        self.menufile.addAction(self.actionquit)
        self.menuabout.addAction(self.actionshow_about)
        self.menubar.addAction(self.menufile.menuAction())
        self.menubar.addAction(self.menuabout.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.textBrowser, self.pushButton_cleartext)
        # MainWindow.setTabOrder(self.pushButton_cleartext, self.lineEdit_1)
        # MainWindow.setTabOrder(self.lineEdit_1, self.pushButton_1)
        # MainWindow.setTabOrder(self.pushButton_1, self.checkBox_1)

    def retranslateUi(self, MainWindow):
        """Translate the GUI items."""
        log.debug("--retranslateUi--")

        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_quit.setText(_translate("MainWindow", "Quit"))
        self.label_name.setText(_translate("MainWindow", "Name:"))
        self.label_mounted.setText(_translate("MainWindow", "Mounted:"))
        self.pushButton_cleartext.setText(_translate("MainWindow", "Clear"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("MainWindow", "Mounts"))
        self.pushButton_save.setText(_translate("MainWindow", "Save"))
        self.pushButton_cancel.setText(_translate("MainWindow", "Cancel"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Config"))
        self.menufile.setTitle(_translate("MainWindow", "File"))
        self.menuabout.setTitle(_translate("MainWindow", "About"))
        self.actionquit.setText(_translate("MainWindow", "Quit"))
        self.actionshow_about.setText(_translate("MainWindow", "Show about"))

    def makeMountItem(self, n):
        """Make the buttons and labels for a mount object."""
        log.debug("--makeMountItem--")

        self.horizontalLayout_set_1 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_set_1.setObjectName(f"horizontalLayout_set_{n}")
        self.lineEdit_1 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_1.setObjectName(f"lineEdit_{n}")
        self.lineEdit_1.setReadOnly(True)
        self.horizontalLayout_set_1.addWidget(self.lineEdit_1)
        self.pushButton_1 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_1.setObjectName(f"pushButton_{n}")
        self.pushButton_1.setText("Mount")
        self.pushButton_1.clicked.connect(lambda: self.actionButtonClick())
        self.horizontalLayout_set_1.addWidget(self.pushButton_1)
        self.checkBox_1 = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.checkBox_1.setText("")
        self.checkBox_1.setObjectName(f"checkBox_{n}")
        self.checkBox_1.setEnabled(False)
        self.horizontalLayout_set_1.addWidget(self.checkBox_1)
        self.verticalLayout_mountpoints.addLayout(self.horizontalLayout_set_1)
