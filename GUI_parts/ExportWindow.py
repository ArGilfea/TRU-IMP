from array import array
from signal import signal
from threading import local
from turtle import color
import numpy as np
import os
import matplotlib.pyplot as plt
from sympy import Q
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.Pickle_Functions as PF
import MyFunctions.Extract_Images_R as Extract_r
import MyFunctions.Extract_Images as Extract
from GUI_parts.GUIParam import GUIParameters
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
class ExportWindow(QMainWindow):
    """
    Class to open an export window to get user's inputs for exporting results
    """
    def __init__(self,parameters:GUIParameters,Image:DicomImage,parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 400)
        self.parameters = parameters
        self.Image = Image
        self.setWindowTitle("Export")
        self.generalLayout = QGridLayout()
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)
        self.initializeParam()
        self.initialize_export_window()
        centralWidget.resize(centralWidget.sizeHint())

    def initializeParam(self):
        self.ExportDicom = False
        self.ExportParam = False
        self.ExportTAC = False
        self.ExportSegFlat = False
        self.ExportDice = False
        self.ExportJaccard = False
        self.TACTypeSave = "TAC Images"
        self.SegFlatTypeSave = "All"
        self.ExportErrorTAC = False
        self.ErrorTACTypeSave = "Error TAC Images"

    def initialize_export_window(self):
        self.current_line = 1
        self._createExportList()

    def browse_button_directory(self,source:QLineEdit):
        text =  QFileDialog.getExistingDirectory()
        source.setText(text+"/")

    def _createHeader(self):
        self.generalLayout.addWidget(QLabel("Part"),0,0)
        self.generalLayout.addWidget(QLabel("Save?"),0,1)
        self.generalLayout.addWidget(QLabel("Parameters"),0,2)
        self.generalLayout.addWidget(QLabel("Options"),0,3)

    def _createPathDock(self):
        self.pathName = QLineEdit()
        btn_browse = QPushButton("Browse")
        self.generalLayout.addWidget(QLabel("Path."),self.current_line,0)
        btn_browse.clicked.connect(partial(self.browse_button_directory,self.pathName))
        self.generalLayout.addWidget(self.pathName,self.current_line,2)
        self.generalLayout.addWidget(btn_browse,self.current_line,3)
        self.current_line +=1

    def _createHeaderDock(self):
        self.headerName = QLineEdit()
        self.generalLayout.addWidget(QLabel("Name"),self.current_line,0)
        self.generalLayout.addWidget(self.headerName,self.current_line,2)
        self.current_line +=1
    def _createDicomSave(self):
        self.DicomImageButton = QCheckBox()
        self.DicomImageButton.stateChanged.connect(self.setValueExportDicom)
        self.generalLayout.addWidget(QLabel("DicomImage"),self.current_line,0)
        self.generalLayout.addWidget(self.DicomImageButton,self.current_line,1)
        self.current_line +=1
    def _createParamSave(self):
        self.ParamButton = QCheckBox()
        self.ParamButton.stateChanged.connect(self.setValueExportParam)
        self.generalLayout.addWidget(QLabel("Parameters"),self.current_line,0)
        self.generalLayout.addWidget(self.ParamButton,self.current_line,1)
        self.current_line +=1
    def _createTACsSave(self):
        self.TACButton = QCheckBox()
        self.TACButton.stateChanged.connect(self.setValueTAC)
        self.TACType = QComboBox()
        self.TACType.addItem("TAC Images")
        self.TACType.addItem("Raw Values")
        self.TACType.addItem("All")
        self.TACButton.setToolTip("Export the specific TAC curve, either via a txt file or the image itself.\n-1 for all of them.")

        subWidget = QWidget()
        layout = QHBoxLayout()
        subWidget.setLayout(layout)
        slider = QSlider(Qt.Horizontal)
        number = QLineEdit()
        number.setText(str(-1))
        slider.setRange(-1,self.Image.voi_counter-1)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setSingleStep(1)
        slider.setValue(-1)
        number.setFixedWidth(30)
        slider.valueChanged.connect(partial(self.set_value_slider,slider,number))
        number.editingFinished.connect(partial(self.set_value_line_edit,slider,number))
        layout.addWidget(slider)
        layout.addWidget(number)
        self.TACsSaveValues = slider
        self.TACType.activated[str].connect(self.TACComboChanged)

        self.generalLayout.addWidget(QLabel("Base TACs"),self.current_line,0)
        self.generalLayout.addWidget(self.TACButton,self.current_line,1)
        self.generalLayout.addWidget(subWidget,self.current_line,2)
        self.generalLayout.addWidget(self.TACType,self.current_line,3)
        self.current_line +=1

    def _createSegmFlatSave(self):
        self.SegFlatButton = QCheckBox()
        self.SegFlatButton.stateChanged.connect(self.setValueSegmFlat)
        self.SegFlatType = QComboBox()
        self.SegFlatType.addItem("Axial")
        self.SegFlatType.addItem("Sagittal")
        self.SegFlatType.addItem("Coronal")
        self.SegFlatType.addItem("All")
        self.SegFlatButton.setToolTip("Export the specific Segm Flat Images.\n-1 for all of them.")

        subWidget = QWidget()
        layout = QHBoxLayout()
        subWidget.setLayout(layout)
        slider = QSlider(Qt.Horizontal)
        number = QLineEdit()
        number.setText(str(-1))
        slider.setRange(-1,self.Image.voi_counter-1)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setSingleStep(1)
        slider.setValue(-1)
        number.setFixedWidth(30)
        slider.valueChanged.connect(partial(self.set_value_slider,slider,number))
        number.editingFinished.connect(partial(self.set_value_line_edit,slider,number))
        layout.addWidget(slider)
        layout.addWidget(number)
        self.SegmFlatSaveValues = slider
        self.SegFlatType.activated[str].connect(self.SegFlatComboChanged)

        self.generalLayout.addWidget(QLabel("Segm. Flats"),self.current_line,0)
        self.generalLayout.addWidget(self.SegFlatButton,self.current_line,1)
        self.generalLayout.addWidget(subWidget,self.current_line,2)
        self.generalLayout.addWidget(self.SegFlatType,self.current_line,3)
        self.current_line +=1

    def _createDiceSave(self):
        self.DiceCoeffButton = QCheckBox()
        self.DiceCoeffButton.stateChanged.connect(self.setValueExportDice)
        self.generalLayout.addWidget(QLabel("Dice Coeff."),self.current_line,0)
        self.generalLayout.addWidget(self.DiceCoeffButton,self.current_line,1)
        self.current_line +=1
    def _createJaccardSave(self):
        self.JaccardCoeffButton = QCheckBox()
        self.JaccardCoeffButton.stateChanged.connect(self.setValueExportJaccard)
        self.generalLayout.addWidget(QLabel("Jaccard Coeff."),self.current_line,0)
        self.generalLayout.addWidget(self.JaccardCoeffButton,self.current_line,1)
        self.current_line +=1

    def _createErrorTACsSave(self):
        self.ErrorTACButton = QCheckBox()
        self.ErrorTACButton.stateChanged.connect(self.setValueErrorTAC)
        self.ErrorTACType = QComboBox()
        self.ErrorTACType.addItem("Error TAC Images")
        self.ErrorTACType.addItem("Raw Values")
        self.ErrorTACType.addItem("All")
        self.ErrorTACButton.setToolTip("Export the specific Error TAC curve, either via a txt file or the image itself.\n-1 for all of them.")

        subWidget = QWidget()
        layout = QHBoxLayout()
        subWidget.setLayout(layout)
        slider = QSlider(Qt.Horizontal)
        number = QLineEdit()
        number.setText(str(-1))
        slider.setRange(-1,self.Image.voi_statistics_counter-1)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setSingleStep(1)
        slider.setValue(-1)
        number.setFixedWidth(30)
        slider.valueChanged.connect(partial(self.set_value_slider,slider,number))
        number.editingFinished.connect(partial(self.set_value_line_edit,slider,number))
        layout.addWidget(slider)
        layout.addWidget(number)
        self.ErrorTACsSaveValues = slider
        self.ErrorTACType.activated[str].connect(self.ErrorTACComboChanged)

        self.generalLayout.addWidget(QLabel("Error TACs"),self.current_line,0)
        self.generalLayout.addWidget(self.ErrorTACButton,self.current_line,1)
        self.generalLayout.addWidget(subWidget,self.current_line,2)
        self.generalLayout.addWidget(self.ErrorTACType,self.current_line,3)
        self.current_line +=1

    def _createExportAll(self):
        self.saveButton = QPushButton("Export")

        self.saveButton.clicked.connect(self.exportInfo)

        self.generalLayout.addWidget(self.saveButton,self.current_line,2)
        self.current_line +=1
    def _createExportList(self):
        self._createHeader()
        self._createPathDock()
        self._createHeaderDock()
        self._createDicomSave()
        self._createParamSave()
        self._createTACsSave()
        self._createSegmFlatSave()
        self._createDiceSave()
        self._createJaccardSave()
        self._createErrorTACsSave()

        self._createExportAll()

    def setValueExportDicom(self):
        self.ExportDicom = self.DicomImageButton.isChecked()
    def setValueExportParam(self):
        self.ExportParam = self.ParamButton.isChecked()
    def setValueTAC(self):
        self.ExportTAC = self.TACButton.isChecked()
    def setValueSegmFlat(self):
        self.ExportSegFlat = self.TACButton.isChecked()
    def setValueExportDice(self):
        self.ExportDice = self.DiceCoeffButton.isChecked()
    def setValueExportJaccard(self):
        self.ExportJaccard = self.JaccardCoeffButton.isChecked()
    def setValueErrorTAC(self):
        self.ExportErrorTAC = self.ErrorTACButton.isChecked()
    def TACComboChanged(self):
        self.TACTypeSave = self.TACType.currentText()
    def ErrorTACComboChanged(self):
        self.ErrorTACTypeSave = self.ErrorTACType.currentText()
    def SegFlatComboChanged(self):
        self.SegFlatTypeSave = self.SegFlatType.currentText()
    def set_value_slider(self,slider:QSlider,lineedit:QLineEdit):
        lineedit.setText(str(slider.value()))
    def set_value_line_edit(self,slider:QSlider,lineedit:QLineEdit):
        """
        Changes the value of the slider when the lineEdit is changed
        """
        try:
            lineedit.setText(f"{int(lineedit.text())}")
        except:
            lineedit.setText("0")
        try:
            slider.setValue(int(lineedit.text()))
        except:
            slider.setValue(0)
    def _createErrorMessage(self,message:str=""):
        alert = QMessageBox()
        if message =="":
            alert.setText("An error occurred")
        else:
            alert.setText(message)
        alert.exec()

    def exportDicomImageProcess(self):
        if self.pathName.text() != "" and self.headerName.text() != "":
            PF.pickle_save(self.Image,self.pathName.text()+self.headerName.text()+"_DicomImage.pkl")
        else:
            self._createErrorMessage("Unable to Save")
    def exportParamProcess(self):
        if self.pathName.text() != "" and self.headerName.text() != "":
            PF.pickle_save(self.parameters,self.pathName.text()+self.headerName.text()+"_Parameters.pkl")
        else:
            self._createErrorMessage("Unable to Save")
    def exportDiceProcess(self):
        if self.pathName.text() != "" and self.headerName.text() != "":
            fig = plt.figure()
            plt.xlabel("Segm."); plt.ylabel("Segm.");plt.title("Dice Coefficients");plt.grid()
            plt.pcolormesh(self.Image.dice_all)
            plt.colorbar()
            fig.savefig(self.pathName.text()+self.headerName.text()+f"_Dice.png")
            del fig
        else:
            self._createErrorMessage("Unable to Save")
    def exportJaccardProcess(self):
        if self.pathName.text() != "" and self.headerName.text() != "":
            fig = plt.figure()
            plt.xlabel("Segm."); plt.ylabel("Segm.");plt.title("Jaccard Coefficients");plt.grid()
            plt.pcolormesh(self.Image.jaccard_all)
            plt.colorbar()
            fig.savefig(self.pathName.text()+self.headerName.text()+f"_Jaccard.png")
            del fig
        else:
            self._createErrorMessage("Unable to Save")
    def exportTACProcess(self):
        if self.pathName.text() != "" and self.headerName.text() != "":
            k = self.TACsSaveValues.value()
            if k == -1:
                z = np.arange(self.Image.voi_counter)
            else:
                z = np.array([k])
            if self.TACTypeSave in ["All","TAC Images"]:
                for i in range(z.shape[0]):
                    fig = plt.figure()
                    plt.xlabel("Time (min)"); plt.ylabel("Signal");plt.title("TAC");plt.grid()
                    plt.plot(self.Image.time,self.Image.voi_statistics[z[i]])
                    fig.savefig(self.pathName.text()+self.headerName.text()+f"_Acq_{z[i]}_TAC.png")
                    del fig
            if self.TACTypeSave in ["All","Raw Values"]:
                arrayTAC = np.zeros((self.Image.time.shape[0],z.shape[0]+1))
                arrayTAC[:,0] = self.Image.time
                for i in range(z.shape[0]):
                    arrayTAC[:,i+1] = self.Image.voi_statistics[z[i]]
                np.savetxt(self.pathName.text()+self.headerName.text()+f"_Acq_{k}_TAC.csv",arrayTAC,delimiter=';')
        else:
            self._createErrorMessage("Unable to Save")
    def exportSegFlatProcess(self):
        if self.pathName.text() != "" and self.headerName.text() != "":
            k = self.SegmFlatSaveValues.value()
            if k == -1:
                z = np.arange(self.Image.voi_counter)
            else:
                z = np.array([k])
            if self.SegFlatTypeSave in ["All","Axial"]:
                 for i in range(z.shape[0]):
                    fig = plt.figure()
                    plt.pcolormesh(self.Image.axial_flat(counter=z[i]))
                    plt.title("Axial Flat")
                    fig.savefig(self.pathName.text()+self.headerName.text()+f"_Segm_{z[i]}_AxialFlat.png")
                    del fig
            if self.SegFlatTypeSave in ["All","Sagittal"]:
                for i in range(z.shape[0]):
                    fig = plt.figure()
                    plt.pcolormesh(self.Image.sagittal_flat(counter=z[i]))
                    plt.title("Sagittal Flat")
                    fig.savefig(self.pathName.text()+self.headerName.text()+f"_Segm_{z[i]}_SagittalFlat.png")
                    del fig
            if self.SegFlatTypeSave in ["All","Coronal"]:
                for i in range(z.shape[0]):
                    fig = plt.figure()
                    plt.pcolormesh(self.Image.coronal_flat(counter=z[i]))
                    plt.title("Sagittal Flat")
                    fig.savefig(self.pathName.text()+self.headerName.text()+f"_Segm_{z[i]}_CoronalFlat.png")
                    del fig
        else:
            self._createErrorMessage("Unable to Save")
    def exportErrorTACProcess(self):
        if self.pathName.text() != "" and self.headerName.text() != "":
            k = self.ErrorTACsSaveValues.value()
            if k == -1:
                z = np.arange(self.Image.voi_statistics_counter)
            else:
                z = np.array([k])
            if self.ErrorTACTypeSave in ["All","Error TAC Images"]:
                for i in range(z.shape[0]):
                    fig = plt.figure()
                    plt.xlabel("Time (min)"); plt.ylabel("Signal");plt.title("Error TAC");plt.grid()
                    plt.errorbar(self.Image.time,self.Image.voi_statistics_avg[z[i]],self.Image.voi_statistics_std[z[i]])
                    fig.savefig(self.pathName.text()+self.headerName.text()+f"_Acq_{z[i]}_Error_TAC.png")
                    del fig
            if self.ErrorTACTypeSave in ["All","Raw Values"]:
                arrayTAC = np.zeros((self.Image.time.shape[0],2*z.shape[0]+1))
                arrayTAC[:,0] = self.Image.time
                for i in range(z.shape[0]):
                    arrayTAC[:,2*i+1] = self.Image.voi_statistics_avg[z[i]]
                    arrayTAC[:,2*i+2] = self.Image.voi_statistics_std[z[i]]
                np.savetxt(self.pathName.text()+self.headerName.text()+f"_Acq_{k}_Error_TAC.csv",arrayTAC,delimiter=';')
        else:
            self._createErrorMessage("Unable to Save")
    def exportInfo(self):
        try:
            if self.ExportDicom:
                self.exportDicomImageProcess()
            if self.ExportParam:
                self.exportParamProcess()
            if self.ExportTAC:
                self.exportTACProcess()
            if self.ExportSegFlat:
                self.exportSegFlatProcess()
            if self.ExportDice:
                self.exportDiceProcess()
            if self.ExportJaccard:
                self.exportJaccardProcess()
            if self.ExportErrorTAC:
                self.exportErrorTACProcess()
            self._createErrorMessage("Export Successful")
        except:
            self._createErrorMessage("Unable to Export")