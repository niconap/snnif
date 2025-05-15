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
            scaphandre = True
            if not self.sudo_password:
                scaphandre = False
            utils.process_data(self.config, scaphandre)
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
        self.selectProtocolComboBox.currentIndexChanged.connect(
            self.populateProtocolOptions)
        self.updateConfigPath()
        self.populateProtocolOptions()

        self.pushButton.clicked.connect(self.runProtocol)

    def populateComboBox(self):
        """
        Populate the protocol selection combo box with available protocols.
        """
        protocols_path = os.path.join(os.getcwd(), "protocols")
        if os.path.exists(protocols_path) and os.path.isdir(protocols_path):
            directories = [
                d for d in os.listdir(protocols_path)
                if os.path.isdir(os.path.join(protocols_path, d))
            ]
            self.selectProtocolComboBox.addItems(directories)
        else:
            self.selectProtocolComboBox.addItem("No protocols found")

    def populateProtocolOptions(self):
        while self.formLayout_2.rowCount() > 1:
            self.formLayout_2.removeRow(1)
        self.variable_widgets = {}

        protocol_name = self.selectProtocolComboBox.currentText()
        if protocol_name and protocol_name != "No protocols found":
            protocol_path = os.path.join(
                os.getcwd(), "protocols", protocol_name)
            config_path = os.path.join(protocol_path, "config.json")
            config = utils.parse_config(config_path)

            if "modes" in config:
                mode_label = QtWidgets.QLabel("Mode")
                self.modeComboBox = QtWidgets.QComboBox()
                self.modeComboBox.addItems(config["modes"].keys())
                default_mode = config.get("default_mode")
                if default_mode and default_mode in config["modes"]:
                    self.modeComboBox.setCurrentText(default_mode)
                self.formLayout_2.addRow(mode_label, self.modeComboBox)
                self.variable_widgets["MODE"] = self.modeComboBox

                self.modeComboBox.currentIndexChanged.connect(
                    lambda: self.updateConfigPath()
                )

            if "variables" in config:
                for var_name, var_info in config["variables"].items():
                    display_name = (
                        var_name.lower()
                        .replace('_', ' ')
                        .replace('-', ' ')
                        .capitalize()
                    )
                    label = QtWidgets.QLabel(display_name)

                    if "options" in var_info:
                        combo = QtWidgets.QComboBox()
                        combo.addItems(var_info["options"])
                        if "default" in var_info and var_info["default"] \
                                in var_info["options"]:
                            combo.setCurrentText(var_info["default"])
                        self.formLayout_2.addRow(label, combo)
                        self.variable_widgets[var_name] = combo
                    elif "min" in var_info and "max" in var_info:
                        spin = QtWidgets.QSpinBox()
                        spin.setMinimum(var_info["min"])
                        spin.setMaximum(var_info["max"])
                        if "default" in var_info:
                            spin.setValue(var_info["default"])
                        self.formLayout_2.addRow(label, spin)
                        self.variable_widgets[var_name] = spin

    def updateConfigPath(self):
        """
        Update the configuration file path based on the selected protocol.
        """
        choice = self.selectProtocolComboBox.currentText()
        if choice and choice != "No protocols found":
            self.textEdit.setText(f"./protocols/{choice}/config.json")
        else:
            self.textEdit.clear()

    def populateTemplate(self, template_config, variables):
        """
        Substitute variables in the command template.
        """
        template = template_config['command_template']
        for var_name in variables:
            if var_name in template:
                widget = self.variable_widgets.get(var_name)
                if widget is not None:
                    if isinstance(widget, QtWidgets.QComboBox):
                        value = widget.currentText()
                    elif isinstance(widget, QtWidgets.QSpinBox):
                        value = str(widget.value())
                    else:
                        continue
                    template = template.replace(f"${{{var_name}}}", value)
        return template

    def runProtocol(self):
        """
        Run the selected protocol with the specified options.
        """
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

        if "modes" in config and hasattr(self, "modeComboBox"):
            selected_mode = self.modeComboBox.currentText()
            mode_config = config["modes"].get(selected_mode, {})
            if "command_template" in mode_config:
                command = self.populateTemplate(
                    mode_config, config.get("variables", {}))
                config['run'] = command
                config['mode'] = selected_mode
        elif "variables" in config and 'command_template' in config:
            command = self.populateTemplate(config, config["variables"])
            config['run'] = command

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
                "Sudo Password Missing",
                "Power measurements will not be available for this run"
            )
            sudo_password = ""

        self.worker = ProtocolWorker(config, sudo_password)
        self.worker.finished.connect(self.onProtocolFinished)
        self.worker.start()

    def onProtocolFinished(self, success, message):
        """
        Handle the completion of the protocol run.
        """
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
