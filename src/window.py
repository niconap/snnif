import os
import sys
import subprocess
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow


class Worker(QtCore.QThread):
    finished = QtCore.pyqtSignal()
    output = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(str)

    def __init__(self, selected_choice):
        super().__init__()
        self.selected_choice = selected_choice
        self._process = None

    def run(self):
        self._process = subprocess.Popen(
            ["python", "src/main.py", "--name", self.selected_choice, "-v"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        try:
            stdout, stderr = self._process.communicate()
            if stdout:
                self.output.emit(stdout.decode())
            if stderr:
                self.error.emit(stderr.decode())
        finally:
            self.finished.emit()

    def terminate(self):
        if self._process and self._process.poll() is None:
            print("Terminating subprocess...")
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Force killing subprocess...")
                self._process.kill()


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SNNIF")
        self.resize(193, 121)

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(10, 10, 171, 27))

        self.pushButton = QtWidgets.QPushButton("Run", self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(10, 40, 171, 27))
        self.pushButton.clicked.connect(self.logSelectedChoice)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.populateComboBox()

        # These will be set during run
        self.thread = None
        self.worker = None

    def populateComboBox(self):
        protocols_path = os.path.join(os.getcwd(), "protocols")
        if os.path.exists(protocols_path) and os.path.isdir(protocols_path):
            directories = [
                d for d in os.listdir(protocols_path)
                if os.path.isdir(os.path.join(protocols_path, d))
            ]
            self.comboBox.addItems(directories)
        else:
            self.comboBox.addItem("No protocols found")

    def logSelectedChoice(self):
        selected_choice = self.comboBox.currentText()
        self.pushButton.setEnabled(False)
        self.pushButton.setText("Running...")

        self.thread = QtCore.QThread()
        self.worker = Worker(selected_choice)
        self.worker.moveToThread(self.thread)

        # Signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.output.connect(lambda text: print("Output:", text))
        self.worker.error.connect(lambda text: print("Error:", text))

        self.worker.finished.connect(lambda: self.pushButton.setText("Run"))
        self.worker.finished.connect(lambda: self.pushButton.setEnabled(True))

        self.thread.start()

    def closeEvent(self, event):
        print("Window close event triggered.")
        if self.worker:
            self.worker.terminate()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())
