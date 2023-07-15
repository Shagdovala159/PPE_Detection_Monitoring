import sys

from PyQt5.QtWidgets import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        button = QPushButton("Press me for a dialog!")
        # button.clicked.connect(self.button_clicked)
        button.clicked.connect(self.warning)
        self.setCentralWidget(button)

    def button_clicked(self, s):
        print("click", s)

        dlg = QDialog(self)
        dlg.setWindowTitle("HELLO!")
        dlg.exec()

    def warning(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)

        # setting message for Message Box
        msg.setText("Budi terdeteksi")

        # setting Message box window title
        msg.setWindowTitle("Warning")

        # declaring buttons on Message Box
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        # start the app
        msg.exec()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()