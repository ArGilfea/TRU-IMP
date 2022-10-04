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
from PyQt5.QtCore import Qt
from functools import partial
###
DISPLAY_HEIGHT = 35
BUTTON_SIZE = 40
ERROR_MSG = "No can do!"

class Window(QMainWindow):
    def _createButtons(self):
        self.buttonMap = {}
        buttonsLayout = QGridLayout()
        keyBoard = [
            ["7", "8", "9", "/", "C"],
            ["4", "5", "6", "*", "("],
            ["1", "2", "3", "-", ")"],
            ["0", "00", ".", "+", "="],
        ]

        for row, keys in enumerate(keyBoard):
            for col, key in enumerate(keys):
                self.buttonMap[key] = QPushButton(key)
                self.buttonMap[key].setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
                buttonsLayout.addWidget(self.buttonMap[key], row, col)

        self.generalLayout.addLayout(buttonsLayout)
    def _createDisplay(self):
        self.display = QLineEdit()
        self.display.setFixedHeight(DISPLAY_HEIGHT)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.generalLayout.addWidget(self.display)        
    def _createStatusBar(self):
        self.status = QStatusBar()
        self.status.showMessage("Hey there!")
        self.generalLayout.addWidget(self.status)        
    def setDisplayText(self, text):
        """Set the display's text."""
        self.display.setText(text)
        self.display.setFocus()

    def displayText(self):
        """Get the display's text."""
        return self.display.text()

    def clearDisplay(self):
        """Clear the display."""
        self.setDisplayText("")
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
        self.setMinimumSize(500, 400)
        self.setWindowTitle("My GUI")
        self.generalLayout = QVBoxLayout()
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)
        self._createDisplay()
        self._createButtons()
        self._createStatusBar()

        msgLabel = QLabel("")

        self.btn = QPushButton("Click Me!")
        self.btn.clicked.connect(greet)
        self.generalLayout.addWidget(self.btn)     
        self.generalLayout.addWidget(msgLabel)     

        self.btn = QPushButton("Click Me Too!!")
        self.btn.clicked.connect(on_button_clicked)
        self.generalLayout.addWidget(self.btn)     
def evaluateExpression(expression):
    """Evaluate an expression (Model)."""
    try:
        result = str(eval(expression, {}, {}))
    except Exception:
        result = ERROR_MSG
    return result

os.system('clear')
print(f"Starting program at {time.strftime('%H:%M:%S')}")
initial = time.time()

###
if __name__ == "__main__":
    app = QApplication([])
    window=Window()
    window.show()
    sys.exit(app.exec())