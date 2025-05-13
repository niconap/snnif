#!/usr/bin/env python3
"""
window.py

This module provides a GUI for selecting and running protocols in the
demonstrator.
"""

import sys
import os

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QInputDialog, QLineEdit, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal

import utils


class ProtocolWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, config, sudo_password):
        super().__init__()
        self.config = config
        self.sudo_password = sudo_password

    def run(self):
        result = utils.run_protocol(self.config, self.sudo_password)
        if not result[0]:
            self.finished.emit(False, result[1])
            return
        try:
            utils.process_data(self.config)
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1320, 820)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.formLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 40, 341, 111))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.iterationsLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.iterationsLabel.setObjectName("iterationsLabel")
        self.formLayout.setWidget(
            0, QtWidgets.QFormLayout.LabelRole, self.iterationsLabel)
        self.iterationsSpinBox = QtWidgets.QSpinBox(self.formLayoutWidget)
        self.iterationsSpinBox.setMinimum(1)
        self.iterationsSpinBox.setMaximum(1000)
        self.iterationsSpinBox.setObjectName("iterationsSpinBox")
        self.formLayout.setWidget(
            0, QtWidgets.QFormLayout.FieldRole, self.iterationsSpinBox)
        self.scaphandreMaxLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.scaphandreMaxLabel.setObjectName("scaphandreMaxLabel")
        self.formLayout.setWidget(
            1, QtWidgets.QFormLayout.LabelRole, self.scaphandreMaxLabel)
        self.scaphandreMaxSpinBox = QtWidgets.QSpinBox(self.formLayoutWidget)
        self.scaphandreMaxSpinBox.setMinimum(15)
        self.scaphandreMaxSpinBox.setMaximum(999999)
        self.scaphandreMaxSpinBox.setObjectName("scaphandreMaxSpinBox")
        self.formLayout.setWidget(
            1, QtWidgets.QFormLayout.FieldRole, self.scaphandreMaxSpinBox)
        self.label_2 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(
            2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.textEdit = QtWidgets.QTextEdit(self.formLayoutWidget)
        self.textEdit.setObjectName("textEdit")
        self.formLayout.setWidget(
            2, QtWidgets.QFormLayout.FieldRole, self.textEdit)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 20, 211, 19))
        self.label.setObjectName("label")

        self.settingsDivider = QtWidgets.QFrame(self.centralwidget)
        self.settingsDivider.setFrameShape(QtWidgets.QFrame.HLine)
        self.settingsDivider.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.settingsDivider.setLineWidth(2)
        self.settingsDivider.setGeometry(QtCore.QRect(10, 160, 341, 2))

        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(10, 170, 121, 21))
        self.label_3.setObjectName("label_3")
        self.formLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(10, 190, 341, 551))
        self.formLayoutWidget_2.setObjectName("formLayoutWidget_2")
        self.formLayout_2 = QtWidgets.QFormLayout(self.formLayoutWidget_2)
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.formLayout_2.setObjectName("formLayout_2")
        self.selectProtocolLabel = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.selectProtocolLabel.setObjectName("selectProtocolLabel")
        self.formLayout_2.setWidget(
            0, QtWidgets.QFormLayout.LabelRole, self.selectProtocolLabel)
        self.selectProtocolComboBox = QtWidgets.QComboBox(
            self.formLayoutWidget_2)
        self.selectProtocolComboBox.setObjectName("selectProtocolComboBox")
        self.formLayout_2.setWidget(
            0, QtWidgets.QFormLayout.FieldRole, self.selectProtocolComboBox)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(10, 750, 341, 41))
        self.pushButton.setObjectName("pushButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1316, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.populateComboBox()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.selectProtocolComboBox.currentIndexChanged.connect(
            self.updateConfigPath)
        self.updateConfigPath()

        self.pushButton.clicked.connect(self.runProtocol)

    def populateComboBox(self):
        protocols_path = os.path.join(os.getcwd(), "protocols")
        if os.path.exists(protocols_path) and os.path.isdir(protocols_path):
            directories = [
                d for d in os.listdir(protocols_path)
                if os.path.isdir(os.path.join(protocols_path, d))
            ]
            self.selectProtocolComboBox.addItems(directories)
        else:
            self.selectProtocolComboBox.addItem("No protocols found")

    def updateConfigPath(self):
        choice = self.selectProtocolComboBox.currentText()
        if choice and choice != "No protocols found":
            self.textEdit.setText(f"./protocols/{choice}/config.json")
        else:
            self.textEdit.clear()

    def runProtocol(self):
        self.pushButton.setEnabled(False)
        self.pushButton.setText("Running...")
        config_path = self.textEdit.toPlainText()
        if config_path.startswith("./"):
            config_path = os.path.abspath(config_path)
        config = utils.parse_config(config_path)

        config['iterations'] = self.iterationsSpinBox.value()
        config['max-top'] = self.scaphandreMaxSpinBox.value()
        config['path'] = os.path.dirname(config_path)
        config['verbose'] = True
        config['name'] = self.selectProtocolComboBox.currentText()

        if utils.validate_config(config) is False:
            print("Invalid configuration")
            self.pushButton.setText("Run protocol")
            self.pushButton.setEnabled(True)
            return

        sudo_password, ok = QInputDialog.getText(
            None,
            "Authorization",
            ("Enter your sudo password (this is required for power"
             " measurements)"),
            QLineEdit.Password
        )
        if not ok or not sudo_password:
            QMessageBox.warning(
                None,
                "Sudo Password Required",
                "Sudo password entry canceled, aborting..."
            )
            self.pushButton.setEnabled(True)
            self.pushButton.setText("Run protocol")
            return

        self.worker = ProtocolWorker(config, sudo_password)
        self.worker.finished.connect(self.onProtocolFinished)
        self.worker.start()

    def onProtocolFinished(self, success, message):
        if not success:
            QMessageBox.critical(
                None,
                "Error",
                f"Error running protocol or processing data: {message}"
            )
        self.pushButton.setText("Run protocol")
        self.pushButton.setEnabled(True)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate(
            "MainWindow", "SNNI demonstrator"))
        self.iterationsLabel.setText(_translate("MainWindow", "Iterations"))
        self.scaphandreMaxLabel.setText(
            _translate("MainWindow", "Max power ranking"))
        self.label_2.setText(_translate("MainWindow", "Path to config file"))
        self.label.setText(
            f"<b>{_translate('MainWindow', 'General settings')}</b>")
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label_3.setText(
            f"<b>{_translate('MainWindow', 'Protocol settings')}</b>")
        self.label_3.setTextFormat(QtCore.Qt.RichText)
        self.selectProtocolLabel.setText(
            _translate("MainWindow", "Choose protocol"))
        self.pushButton.setText(_translate("MainWindow", "Run protocol"))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    sys.exit(app.exec_())
