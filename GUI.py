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
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
###
ERROR_MSG = "No can't do!"

class Window(QMainWindow):
    def _createButtons(self):
        pass
    def _createDisplay(self):
        self.display = QLineEdit()
        self.display.setFixedHeight(self.DISPLAY_HEIGHT)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.generalLayout.addWidget(self.display)        
    def _createStatusBar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)      
        self.statusBar.showMessage("Nothing started")
    def _createPopUp(self):
        self.btn = QPushButton("Info")
        self.btn.clicked.connect(self.on_button_clicked_infos)
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
        source.setText("/Users/philippelaporte/Desktop/Programmation/Python/Data/Fantome_6_1min_comp_2_I_k_all.pkl")
        source.setText("/Users/philippelaporte/Desktop/Fantome_9_1min.pkl")
        btn_load.clicked.connect(partial(self.load_button,source))
        self.generalLayout.addWidget(btn_load)  
        self.generalLayout.addWidget(source)   
    def setDisplayText(self, text):
        """Set the display's text."""
        self.display.setText(text)
        self.display.setFocus()
    def displayStatus(self,action,time_i):
        new_status = f"{action} done in {(time.time()-time_i):.2f}' s at {time.strftime('%H:%M:%S')}"
        self.statusBar.showMessage(new_status)
    def displayText(self):
        """Get the display's text."""
        return self.display.text()

    def clearDisplay(self):
        """Clear the display."""
        self.setDisplayText("")
    def show_infos_acq(self):
        a = f"""Name: \t{self.Image.name}<br>
                Description: {self.Image.Description}<br>
                Version: {self.Image.version}<br>
                Number of timeframes: {self.Image.nb_acq}<br>
                Number of slices: {self.Image.nb_slice}<br>
                Width: {self.Image.width}<br>
                Length: {self.Image.length}<br>
                """
        return a
    def on_button_clicked_infos(self):
        alert = QMessageBox()
        #alert.setIcon(QMessageBox.Information)
        alert.setWindowTitle("Infos")
        try:
            alert.setText(self.show_infos_acq())
        except:
            alert.setText("No file uploaded")
        alert.exec()
    def load_button(self,source):
        initial = time.time()
        self.Image = PF.pickle_open(source.text())
        self.name = self.Image.version
        self.displayStatus("File loading", initial)
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.pcolormesh(self.Image.axial_flat(acq=10))
        self.generalLayout.addWidget(sc)
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
        self.setMinimumSize(600, 400)
        self.setWindowTitle("My GUI")
        self.generalLayout = QVBoxLayout()
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)
        self._createLoadingDock()
        self._createPopUp()
        self._createMessage()
        self._createStatusBar()
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
        #self._connectSignalsAndSlots()

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

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

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