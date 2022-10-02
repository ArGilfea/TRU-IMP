import numpy as np
import os
import matplotlib.pyplot as plt
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.Pickle_Functions as PF
import MyFunctions.Extract_Images_R as Extract_r
import time
###
import numpy as np
import time
import matplotlib.pyplot as plt
###
import sys
from PyQt5.QtWidgets import *
"""import (
    QApplication, QLabel, QWidget,
    QDialog, QFormLayout, QLineEdit, QVBoxLayout,
    QDialogButtonBox
)"""
###

class Window(QDialog):
    def _createStatusBar(self):
        status = QStatusBar()
        status.showMessage("Hey there!")
    def __init__(self):
        def on_button_clicked():
            alert = QMessageBox()
            alert.setText("Sup dude!")
            alert.exec()


        super().__init__(parent=None)
        self.setWindowTitle("QDialog")
        dialogLayout = QVBoxLayout()
        formLayout = QFormLayout()
        formLayout.addRow("Name:", QLineEdit())
        dialogLayout.addLayout(formLayout)
        button = QPushButton("Click Me!")
        button.clicked.connect(on_button_clicked)
        dialogLayout.addWidget(button)
        btn = QPushButton("Close")
        btn.clicked.connect(self.close)
        slider = QSlider(3)
        dialogLayout.addWidget(slider)
        dialogLayout.addWidget(btn)
        self._createStatusBar()
        self.setLayout(dialogLayout)



os.system('clear')
print(f"Starting program at {time.strftime('%H:%M:%S')}")
initial = time.time()

###
if __name__ == "__main__":
    app = QApplication([])
    window=Window()
    window.show()
    sys.exit(app.exec())