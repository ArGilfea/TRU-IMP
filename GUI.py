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
from functools import partial
###

class Window(QMainWindow):
    def _createStatusBar(self):
        status = QStatusBar()
        status.showMessage("Hey there!")
    def __init__(self):
        def on_button_clicked():
            alert = QMessageBox()
            alert.setText("Sup dude!")
            alert.exec()
        def greet(name="World"):
            if msgLabel.text():
                msgLabel.setText("")
            else:
                msgLabel.setText(f"Hello, {name}!")

        super().__init__(parent=None)
        #self.setMinimumSize(500, 400)
        self.setWindowTitle("My GUI")
        dialogLayout = QVBoxLayout()
        formLayout = QFormLayout()
        self.name = formLayout.addRow("Name:", QLineEdit())
        dialogLayout.addLayout(formLayout)
        button = QPushButton("Click Me!")
        button2 = QPushButton("Greetings")
        button.clicked.connect(on_button_clicked)
        button2.clicked.connect(partial(greet,self.name))
        dialogLayout.addWidget(button)
        msgLabel = QLabel("")
        dialogLayout.addWidget(button2)
        dialogLayout.addWidget(msgLabel)
        btn = QPushButton("Close")
        btn.clicked.connect(self.close)
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