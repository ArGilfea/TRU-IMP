from curses import ERR
from signal import signal
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
ERROR_MSG = "No can't do!"

class Window(QMainWindow):
    def _createButtons(self):
        self.buttonMap = {}
        buttonsLayout = QGridLayout()
        keyBoard = [
            ["7", "8", "9", "/", "C"],
            ["4", "5", "6", "*", "("],
            ["1", "2", "3", "-", ")"],
            ["0", "00", ".", "+", "="],
            ["T","Load","","View",""],
        ]

        for row, keys in enumerate(keyBoard):
            for col, key in enumerate(keys):
                if key == "T":
                    self.edit_box = QLineEdit()
                    self.edit_box.setObjectName("host")
                    self.edit_box.setText("host")
                    self.edit_box.setFixedSize(self.BUTTON_SIZE, self.BUTTON_SIZE)
                    buttonsLayout.addWidget(self.edit_box, row, col)
                else:
                    self.buttonMap[key] = QPushButton(key)
                    self.buttonMap[key].setFixedSize(self.BUTTON_SIZE, self.BUTTON_SIZE)
                    buttonsLayout.addWidget(self.buttonMap[key], row, col)

        self.generalLayout.addLayout(buttonsLayout)
    def _createDisplay(self):
        self.display = QLineEdit()
        self.display.setFixedHeight(self.DISPLAY_HEIGHT)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.generalLayout.addWidget(self.display)        
    def _createStatusBar(self):
        self.status = QStatusBar()
        self.status.showMessage("Hey there!")
        self.generalLayout.addWidget(self.status)      
    def _createPopUp(self):
        self.btn = QPushButton("Click Me Too!!")
        self.btn.clicked.connect(self.on_button_clicked)
        self.generalLayout.addWidget(self.btn)      
    def _createMessage(self):
        self.msgLabel = QLabel("")

        self.btn = QPushButton("Click Me!")
        self.btn.clicked.connect(self.greet)
        self.generalLayout.addWidget(self.btn)     
        self.generalLayout.addWidget(self.msgLabel)    
    def _createExitButton(self):
        self.exit = QPushButton("Exit")
        self.exit.clicked.connect(self.close)
        self.generalLayout.addWidget(self.exit)  
    def _createLoadingDock(self):
        btn_load = QPushButton("Load")
        source = QLineEdit()
        btn_load.clicked.connect(partial(self.load_button,source))
        self.generalLayout.addWidget(btn_load)  
        self.generalLayout.addWidget(source)  
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
    def on_button_clicked(self):
        alert = QMessageBox()
        alert.setText("Sup dude!")
        alert.exec()
    def load_button(self,source):
        self.name = source.text()
    def greet(self):
        try:
            if self.msgLabel.text():
                self.msgLabel.setText("")
            else:
                self.msgLabel.setText(f"Hello, {self.name}!")
        except:
            self.msgLabel.setText(ERROR_MSG)
    def __init__(self):
        self.BUTTON_SIZE = 40
        self.DISPLAY_HEIGHT = 35
        super().__init__(parent=None)
        self.setMinimumSize(500, 400)
        self.setWindowTitle("My GUI")
        self.generalLayout = QVBoxLayout()
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)
        self._createDisplay()
        self._createButtons()
        self._createLoadingDock()
        self._createPopUp()
        self._createMessage()
        self._createExitButton() 
 
def evaluateExpression(expression):
    """Evaluate an expression (Model)."""
    try:
        result = str(eval(expression, {}, {}))
    except Exception:
        result = ERROR_MSG
    return result

class PySeg:
    """PyCalc's controller class."""

    def __init__(self, model, view):
        self._evaluate = model
        self._view = view
        self._connectSignalsAndSlots()

    def _calculateResult(self):
        result = self._evaluate(expression=self._view.displayText())
        self._view.setDisplayText(result)

    def _buildExpression(self, subExpression):
        if self._view.displayText() == ERROR_MSG:
            self._view.clearDisplay()
        expression = self._view.displayText() + subExpression
        self._view.setDisplayText(expression)

    def _connectSignalsAndSlots(self):
        for keySymbol, button in self._view.buttonMap.items():
            if keySymbol not in {"=", "C"}:
                button.clicked.connect(
                    partial(self._buildExpression, keySymbol)
                )
        self._view.buttonMap["="].clicked.connect(self._calculateResult)
        self._view.display.returnPressed.connect(self._calculateResult)
        self._view.buttonMap["C"].clicked.connect(self._view.clearDisplay)
        self._view.buttonMap["C"].clicked.connect(self._view.clearDisplay)


os.system('clear')
print(f"Starting program at {time.strftime('%H:%M:%S')}")
initial = time.time()

###
if __name__ == "__main__":
    app = QApplication([])
    window=Window()
    window.show()
    PySeg(model=evaluateExpression, view=window)
    sys.exit(app.exec())