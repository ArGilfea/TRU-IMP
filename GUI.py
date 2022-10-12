from array import array
from curses import ERR
from signal import signal
import numpy as np
import os
import matplotlib.pyplot as plt
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.Pickle_Functions as PF
import MyFunctions.Extract_Images_R as Extract_r
import MyFunctions.Extract_Images as Extract
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
        self.generalLayout.addWidget(self.btn,0,3)      
    def _createMessage(self):
        self.msgLabel = QLabel("")
        self.btn = QPushButton("Click Me!")
        self.btn.clicked.connect(self.greet)
        self.generalLayout.addWidget(self.btn)     
        self.generalLayout.addWidget(self.msgLabel)    
    def _createExitButton(self):
        self.exit = QPushButton("Exit")
        self.exit.clicked.connect(self.close)
        self.generalLayout.addWidget(self.exit,6,3)  
    def _createExtractDock(self,line=0):
        msg_extract = QLabel("Path: ")
        source = QLineEdit()
        btn_extr = QPushButton("Extract")
        source.setText("/Users/philippelaporte/Desktop/FantDYN9/PET-AC-DYN-1-MIN/")
        btn_extr.clicked.connect(partial(self.extract_button,source,"d"))

        self.generalLayout.addWidget(msg_extract,line,0)  
        self.generalLayout.addWidget(source,line,1)           
        self.generalLayout.addWidget(btn_extr,line,2)  
    def _createLoadingDock(self,line=1):
        msg_load = QLabel("Path: ")
        source = QLineEdit()
        btn_load = QPushButton("Load")
        source.setText("/Users/philippelaporte/Desktop/Programmation/Python/Data/Fantome_6_1min_comp_2_I_k_all.pkl")
        source.setText("/Users/philippelaporte/Desktop/Fantome_9_1min.pkl")
        btn_load.clicked.connect(partial(self.load_button,source))
        self.generalLayout.addWidget(msg_load,line,0)  
        self.generalLayout.addWidget(source,line,1)   
        self.generalLayout.addWidget(btn_load,line,2)  
    def _createSavingDock(self,line=2):
        msg_save = QLabel("Path: ")
        path = QLineEdit()
        path.setText("")
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(partial(self.save_button,path))

        self.generalLayout.addWidget(msg_save,line,0)  
        self.generalLayout.addWidget(path,line,1)  
        self.generalLayout.addWidget(btn_save,line,2)  
    def _createParameterScreen(self,line=1):
        btn_param = QPushButton("Parameters")
        btn_param.clicked.connect(self.open_parameters)
        self.generalLayout.addWidget(btn_param,line,3)
    def _createImageDisplay(self,line=4):
        size_Image = 200
        msg_Image = QLabel("View: ")
        msg_Axial = QLabel("Axial")
        msg_Sagittal = QLabel("Sagittal")
        msg_Coronal = QLabel("Coronal")
        self.axial = MplCanvas(self, width=5, height=4, dpi=100)
        self.sagittal = MplCanvas(self, width=5, height=4, dpi=100)
        self.coronal = MplCanvas(self, width=5, height=4, dpi=100)
        try:
            self.axial.axes.pcolormesh(self.Image.Image[0,0,:,:])  
            self.coronal.axes.pcolormesh(self.Image.Image[0,:,0,:])  
            self.sagittal.axes.pcolormesh(self.Image.Image[0,:,:,0])
        except:
            self.axial.axes.pcolormesh(np.zeros((100,100)))
            self.coronal.axes.pcolormesh(np.zeros((100,100)))
            self.sagittal.axes.pcolormesh(np.zeros((100,100)))
        self.axial.setMinimumSize(size_Image,size_Image)
        self.coronal.setMinimumSize(size_Image,size_Image)
        self.sagittal.setMinimumSize(size_Image,size_Image)
        self.generalLayout.addWidget(msg_Image,line,0)  
        self.generalLayout.addWidget(msg_Axial,line-1,1)
        self.generalLayout.addWidget(msg_Sagittal,line-1,2)
        self.generalLayout.addWidget(msg_Coronal,line-1,3)
        self.generalLayout.addWidget(self.axial,line,1)
        self.generalLayout.addWidget(self.coronal,line,2)
        self.generalLayout.addWidget(self.sagittal,line,3)
    def _createImageDisplayType(self,line=2):
        self.ImageViewCombo = QComboBox()
        self.view = "Slice"
        self.ImageViewCombo.addItem("Slice")
        self.ImageViewCombo.addItem("Flat")
        self.ImageViewCombo.addItem("Sub. Slice")
        self.ImageViewCombo.addItem("Sub. Flat")
        self.ImageViewCombo.addItem("Segm. Slice")
        self.ImageViewCombo.addItem("Segm. Flat")
        self.ImageViewCombo.activated[str].connect(self.combo_box_changed)
        self.generalLayout.addWidget(self.ImageViewCombo,line,3)
    def _createImageDisplayBars(self,line=5):
        try:
            self.generalLayout.removeWidget(self.slider_widget)
            self.slider_widget.setParent(None)
        except:
            pass
        sizeText = 30
        self.slider_widget = QWidget()
        layout = QGridLayout()
        self.slider_widget.setLayout(layout)
        self.sliderAcq = QSlider(Qt.Horizontal)
        self.sliderAxial = QSlider(Qt.Horizontal)
        self.sliderSagittal = QSlider(Qt.Horizontal)
        self.sliderCoronal = QSlider(Qt.Horizontal)
        self.sliderSegm = QSlider(Qt.Horizontal)
        try:
            self.sliderAcq.setMinimum(0);self.sliderAcq.setMaximum(self.Image.nb_acq-1)
            self.sliderAxial.setMinimum(0);self.sliderAxial.setMaximum(self.Image.nb_slice-1)
            self.sliderSagittal.setMinimum(0);self.sliderSagittal.setMaximum(self.Image.width-1)
            self.sliderCoronal.setMinimum(0);self.sliderCoronal.setMaximum(self.Image.length-1)
            self.sliderSegm.setMinimum(0);self.sliderSegm.setMaximum(self.Image.voi_counter)
        except:
            pass
        self.sliderAcq.setTickPosition(QSlider.TicksBothSides)
        self.sliderAxial.setTickPosition(QSlider.TicksBothSides)
        self.sliderSagittal.setTickPosition(QSlider.TicksBothSides)
        self.sliderCoronal.setTickPosition(QSlider.TicksBothSides)
        self.sliderSegm.setTickPosition(QSlider.TicksBothSides)
        self.sliderAcq.setSingleStep(1)
        self.sliderAxial.setSingleStep(1)
        self.sliderSagittal.setSingleStep(1)
        self.sliderCoronal.setSingleStep(1)
        self.sliderSegm.setSingleStep(1)
        layout.addWidget(self.sliderAcq,0,1)
        layout.addWidget(self.sliderAxial,1,1)
        layout.addWidget(self.sliderSagittal,2,1)
        layout.addWidget(self.sliderCoronal,3,1)
        layout.addWidget(self.sliderSegm,4,1)
        self.AcqValueHeader = QLabel("Acq:")
        self.AxialValueHeader = QLabel("Ax:")
        self.SagittalValueHeader = QLabel("Sag:")
        self.CoronalValueHeader = QLabel("Cor:")
        self.SegmValueHeader = QLabel("Segm:")
        self.sliderAcqValue = QLineEdit()
        self.sliderAxialValue = QLineEdit()
        self.sliderSagittalValue = QLineEdit()
        self.sliderCoronalValue = QLineEdit()
        self.sliderSegmValue = QLineEdit()
        self.sliderAcqValue.setFixedWidth(sizeText)
        self.sliderAxialValue.setFixedWidth(sizeText)
        self.sliderSagittalValue.setFixedWidth(sizeText)
        self.sliderCoronalValue.setFixedWidth(sizeText)
        self.sliderSegmValue.setFixedWidth(sizeText)
        try:
            self.sliderAcqValue.setText(f"{self.set_value_slider(self.sliderAcq,self.sliderAcqValue)}")
            self.sliderAxialValue.setText(f"{self.set_value_slider(self.sliderAxial,self.sliderAxialValue)}")
            self.sliderSagittalValue.setText(f"{self.set_value_slider(self.sliderSagittal,self.sliderSagittalValue)}")
            self.sliderCoronalValue.setText(f"{self.set_value_slider(self.sliderCoronal,self.sliderCoronalValue)}")
            self.sliderSegmValue.setText(f"{self.set_value_slider(self.sliderSegm,self.sliderSegmValue)}")
            self.sliderAcqValue.editingFinished.connect(partial(self.set_value_line_edit,self.sliderAcq,self.sliderAcqValue))
            self.sliderAxialValue.editingFinished.connect(partial(self.set_value_line_edit,self.sliderAxial,self.sliderAxialValue))
            self.sliderSagittalValue.editingFinished.connect(partial(self.set_value_line_edit,self.sliderSagittal,self.sliderSagittalValue))
            self.sliderCoronalValue.editingFinished.connect(partial(self.set_value_line_edit,self.sliderCoronal,self.sliderCoronalValue))
            self.sliderSegmValue.editingFinished.connect(partial(self.set_value_line_edit,self.sliderSegm,self.sliderSegmValue))
            self.sliderAcq.valueChanged.connect(partial(self.set_value_slider,self.sliderAcq,self.sliderAcqValue))
            self.sliderAxial.valueChanged.connect(partial(self.set_value_slider,self.sliderAxial,self.sliderAxialValue))
            self.sliderSagittal.valueChanged.connect(partial(self.set_value_slider,self.sliderSagittal,self.sliderSagittalValue))
            self.sliderCoronal.valueChanged.connect(partial(self.set_value_slider,self.sliderCoronal,self.sliderCoronalValue))
            self.sliderSegm.valueChanged.connect(partial(self.set_value_slider,self.sliderSegm,self.sliderSegmValue))
        except:
            pass
        layout.addWidget(self.AcqValueHeader,0,0)
        layout.addWidget(self.AxialValueHeader,1,0)
        layout.addWidget(self.SagittalValueHeader,2,0)
        layout.addWidget(self.CoronalValueHeader,3,0)
        layout.addWidget(self.SegmValueHeader,4,0)
        layout.addWidget(self.sliderAcqValue,0,2)
        layout.addWidget(self.sliderAxialValue,1,2)
        layout.addWidget(self.sliderSagittalValue,2,2)
        layout.addWidget(self.sliderCoronalValue,3,2)
        layout.addWidget(self.sliderSegmValue,4,2)
        self.generalLayout.addWidget(self.slider_widget,line,1)
        self.slider_widget.resize(500,500)
    def _createTACImage(self):
        self.TACImage = MplCanvas(self, width=5, height=4, dpi=100)
        self.TACImage.axes.set_title("TAC");self.TACImage.axes.grid()
        self.TACImage.axes.set_xlabel("Time");self.TACImage.axes.set_ylabel("Signal")
        self.generalLayout.addWidget(self.TACImage)
    def set_value_slider(self,slider:QSlider,lineedit:QLineEdit):
        lineedit.setText(str(slider.value()))
        self.update_TAC()
        self.update_view()
        return slider.value()
    def set_value_line_edit(self,slider:QSlider,lineedit:QLineEdit):
        try:
            slider.setValue(int(lineedit.text()))
        except:
            slider.setValue(0)
        self.update_TAC()
        self.update_view()
    def combo_box_changed(self):
        print(self.ImageViewCombo.currentText())
        self.view = self.ImageViewCombo.currentText()
        self.update_TAC()
        self.update_view()
    def open_parameters(self):
        self.paramWindow = QDialog()
        self.paramWindow.setWindowTitle("Parameters")
        #self.paramWindow.exec()
        window = ParamWindow(self)
        window.show()
    def show_parameters():
        pass
    def update_TAC(self):
        try:
            values = [self.sliderAcq.value(),self.sliderAxial.value(),self.sliderCoronal.value(),self.sliderSagittal.value()]
            x_axis = self.Image.time
            y_axis = self.Image.Image[:,values[1],values[2],values[3]]
            self.TACImage.axes.plot(x_axis,y_axis)
        except:
            pass
    def update_view(self):
        values = [self.sliderAcq.value(),self.sliderAxial.value(),self.sliderCoronal.value(),self.sliderSagittal.value()]
        key = self.sliderSegm.value()
        if self.view == "Slice":
            try:
                self.axial.axes.pcolormesh(self.Image.Image[values[0],values[1],:,:])
                self.sagittal.axes.pcolormesh(self.Image.Image[values[0],:,:,values[2]])
                self.coronal.axes.pcolormesh(self.Image.Image[values[0],:,values[2],:])
            except:
                #alert = QMessageBox()
                #alert.setText("Can't perform this. No image is loaded")
                pass
        elif self.view == "Flat":
            try:
                self.axial.axes.pcolormesh(self.Image.axial_flat(acq=values[0]))
                self.sagittal.axes.pcolormesh(self.Image.sagittal_flat(acq=values[0]))
                self.coronal.axes.pcolormesh(self.Image.coronal_flat(acq=values[0]))
            except:
                alert = QMessageBox()
                alert.setText("Can't perform this. No image is loaded or the flats are not done")
        elif self.view == "Segm. Slice":
            try:
                self.axial.axes.pcolormesh(self.Image.axial_flat(counter=key)[values[0],values[1],:,:])
                self.sagittal.axes.pcolormesh(self.Image.sagittal_flat(counter=key)[values[0],:,:,values[2]])
                self.coronal.axes.pcolormesh(self.Image.coronal_flat(counter=key)[values[0],:,values[2],:])
            except:
                alert = QMessageBox()
                alert.setText("Can't perform this. No segmentations are present")
        elif self.view == "Segm. Flat":
            try:
                self.axial.axes.pcolormesh(self.Image.axial_flat(counter=key))
                self.sagittal.axes.pcolormesh(self.Image.sagittal_flat(counter=key))
                self.coronal.axes.pcolormesh(self.Image.coronal_flat(counter=key))
            except:
                alert = QMessageBox()
                alert.setText("Can't perform this. No segmentations are present")
        try:
            alert.exec()
        except:
            pass
    def setDisplayText(self, text:str):
        """Set the display's text."""
        self.display.setText(text)
        self.display.setFocus()
    def displayStatus(self,action:str,time_i=time.time()):
        new_status = f"{action} done in {(time.time()-time_i):.2f}' s at {time.strftime('%H:%M:%S')}"
        self.statusBar.showMessage(new_status)
    def displayText(self):
        """Get the display's text."""
        return self.display.text()

    def clearDisplay(self):
        """Clear the display."""
        self.setDisplayText("")
    def show_infos_acq(self):
        a = f"""Name: {self.Image.name}<br>
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
    def extract_button(self,source,method="d"):
        initial = time.time()
        print(source)
        print(source.text())
        if method == "r":
            self.Image = Extract_r.Extract_Images(source.text(),verbose=True,save=False)
        elif method == "d":
            self.Image = Extract.Extract_Images(source.text(),verbose=True,save=False)
        else:
            raise Exception("Extraction method is invalid")
        self.displayStatus("File extracted", initial)
        self._createImageDisplay()
        self._createImageDisplayBars()
    def load_button(self,source):
        initial = time.time()
        self.Image = PF.pickle_open(source.text())
        self.name = self.Image.version
        self.displayStatus("File loading", initial)
        self._createImageDisplay()
        self._createImageDisplayBars()
    def save_button(self,path):
        initial = time.time()
        alert = QMessageBox()
        if path.text() == "":
            alert.setText("Empty path. Please specify where to save.")
        else:
            try:
                PF.pickle_save(self.Image,path.text())
                alert.setText(f"Save successfull")
            except:
                alert.setText(f"Impossible to save to the desired folder")
        self.displayStatus("File saved", initial)
        alert.exec()

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
        self.setMinimumSize(900, 600)
        self.setWindowTitle("My GUI")
        self.generalLayout = QGridLayout()
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)
        self._createExtractDock()
        self._createLoadingDock()
        self._createSavingDock()
        self._createPopUp()
        #self._createMessage()
        self._createParameterScreen()
        self._createImageDisplay()
        self._createImageDisplayType()
        self._createImageDisplayBars()
        self._createTACImage()
        self._createStatusBar()
        self._createExitButton() 
 
def evaluateExpression(expression):
    """Evaluate an expression (Model)."""
    try:
        result = str(eval(expression, {}, {}))
    except Exception:
        result = ERROR_MSG
    return result

class ParamWindow(QMainWindow):
    """
    Class to open a parameter window to get user's inputs
    """
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 500)
        self.setWindowTitle("Parameters")
        self.generalLayout = QGridLayout()
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)
        self._createParamList()
    def _createParamList(self):
        param = ["Acq","SubImage Range","Seed","Save Segm."]
        for i in range(len(param)):
            paramNew = QLabel(param[i]+":")
            self.generalLayout.addWidget(paramNew,i,0)
    def return_param(self):
        pass

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