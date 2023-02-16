from array import array
from signal import signal
from threading import local
from turtle import color
import numpy as np
import os
import matplotlib.pyplot as plt
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
        """
        Initializes the class
        """
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
        """
        Creates all the export parameters that can be chosen
        """
        self.ExportDicom = False
        self.ExportParam = False
        self.ExportLog = False
        self.ExportTAC = False
        self.ExportSegFlat = False
        self.ExportDice = False
        self.ExportJaccard = False
        self.TACTypeSave = "TAC Images"
        self.SegFlatTypeSave = "All"
        self.ExportErrorTAC = False
        self.ErrorTACTypeSave = "Error TAC Images"
        self.ExportDynestyParam = False
        self.DynestyParamTypeSave = "Dynesty Param"
        self.ExportDynestyGraphs = False
        self.DynestyGraphTypeSave = "RunPlot"

    def initialize_export_window(self):
        """
        Initializes the export window.\n
        The current_line parameter allows to dynamically orient the widgets in the window
        """
        self.current_line = 1
        self._createExportList()

    def browse_button_directory(self,source:QLineEdit):
        """
        Opens a browse window and allows the user to determine a folder to select.\n
        The result is passed to the source parameters.
        """
        text =  QFileDialog.getExistingDirectory()
        source.setText(text+"/")

    def _createHeader(self):
        """
        Create the header of the window for each column
        """
        self.generalLayout.addWidget(QLabel("Part"),0,0)
        self.generalLayout.addWidget(QLabel("Save?"),0,1)
        self.generalLayout.addWidget(QLabel("Parameters"),0,2)
        self.generalLayout.addWidget(QLabel("Options"),0,3)

    def _createPathDock(self):
        """
        Creates the Path dock.\n
        This makes a line edit and a browse button from which the destination folder is chosen 
        """
        self.pathName = QLineEdit()
        btn_browse = QPushButton("Browse")
        self.pathName.setToolTip("Destination folder for the exportation process")
        btn_browse.setToolTip("Open a local browser to determine the path for the exportation")
        self.generalLayout.addWidget(QLabel("Path"),self.current_line,0)
        btn_browse.clicked.connect(partial(self.browse_button_directory,self.pathName))
        self.generalLayout.addWidget(self.pathName,self.current_line,2)
        self.generalLayout.addWidget(btn_browse,self.current_line,3)
        self.current_line +=1

    def _createHeaderDock(self):
        """
        Creates the line edit to input the name of the exported material
        """
        self.headerName = QLineEdit()
        self.headerName.setToolTip("""Global name for the exported material.
A suffix will be added for the specific exported material.""")
        self.generalLayout.addWidget(QLabel("Name"),self.current_line,0)
        self.generalLayout.addWidget(self.headerName,self.current_line,2)
        self.current_line +=1
    def _createDicomSave(self):
        """
        Creates the button to determine whether the DicomImage class is saved
        """
        self.DicomImageButton = QCheckBox()
        self.DicomImageButton.setToolTip("""Saves the DicomImage class, which contains all the segmentations and results.
The result will be a pickle (.pkl) file, with a size of at least a few GB.
This is highly recommended after long computations, as it saves the completed progress,
allowing to save a huge amount of computing time.""")
        self.DicomImageButton.stateChanged.connect(self.setValueExportDicom)
        self.generalLayout.addWidget(QLabel("DicomImage"),self.current_line,0)
        self.generalLayout.addWidget(self.DicomImageButton,self.current_line,1)
        self.current_line +=1
    def _createParamSave(self):
        """
        Creates the button to determine whether the Parameter class is saved
        """
        self.ParamButton = QCheckBox()
        self.ParamButton.setToolTip("""Saves the GUIParam class, which contains the parameters used for the segmentations, the errors and the Dynesty analyses.
The result will be a pickle (.pkl) file, with a small size (few kB).
This is recommended when many analyses will be run or to keep track of what had been done before.
Useful for the reproducibility of analyses.""")
        self.ParamButton.stateChanged.connect(self.setValueExportParam)
        self.generalLayout.addWidget(QLabel("Parameters"),self.current_line,0)
        self.generalLayout.addWidget(self.ParamButton,self.current_line,1)
        self.current_line +=1
    def _createLogSave(self):
        """
        Creates the button to determine whether the DicomImage log infos will be saved
        """
        self.LogButton = QCheckBox()
        self.LogButton.setToolTip("")
        self.LogButton.stateChanged.connect(self.setValueExportLog)
        self.generalLayout.addWidget(QLabel("Log"),self.current_line,0)
        self.generalLayout.addWidget(self.LogButton,self.current_line,1)
        self.current_line +=1
    def _createTACsSave(self):
        """
        Creates the dock to save the TACs computed using the segmentations
        """
        self.TACButton = QCheckBox()
        self.TACButton.stateChanged.connect(self.setValueTAC)
        self.TACType = QComboBox()
        self.TACType.addItem("TAC Images")
        self.TACType.addItem("Raw Values")
        self.TACType.addItem("All")
        self.TACButton.setToolTip("Export the specific TAC curve, either via a txt file, the image itself (.png), or both.\n-1 for all of them.")

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
        slider.setToolTip("If -1, all TACs will be saved")
        number.setToolTip("If -1, all TACs will be saved")
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
        """
        Create the dock to save the flats of the segmentations
        """
        self.SegFlatButton = QCheckBox()
        self.SegFlatButton.stateChanged.connect(self.setValueSegmFlat)
        self.SegFlatType = QComboBox()
        self.SegFlatType.addItem("Axial")
        self.SegFlatType.addItem("Sagittal")
        self.SegFlatType.addItem("Coronal")
        self.SegFlatType.addItem("All")
        self.SegFlatButton.setToolTip("Export the specific Segm Flat Images, either one type or all 3, to png images.\n-1 for all of them.")

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
        slider.setToolTip("If -1, all segmentation flats will be saved")
        number.setToolTip("If -1, all segmentation flats will be saved")
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
        """
        Create the button to save the Dice coefficient matrix
        """
        self.DiceCoeffButton = QCheckBox()
        self.DiceCoeffButton.stateChanged.connect(self.setValueExportDice)
        self.DiceCoeffButton.setToolTip("Save the Dice coefficient matrix as a graph")
        self.generalLayout.addWidget(QLabel("Dice Coeff."),self.current_line,0)
        self.generalLayout.addWidget(self.DiceCoeffButton,self.current_line,1)
        self.current_line +=1
    def _createJaccardSave(self):
        """
        Create the button to save the Jaccard coefficient matrix
        """
        self.JaccardCoeffButton = QCheckBox()
        self.JaccardCoeffButton.setToolTip("Save the Jaccard coefficient matrix as a graph")
        self.JaccardCoeffButton.stateChanged.connect(self.setValueExportJaccard)
        self.generalLayout.addWidget(QLabel("Jaccard Coeff."),self.current_line,0)
        self.generalLayout.addWidget(self.JaccardCoeffButton,self.current_line,1)
        self.current_line +=1

    def _createErrorTACsSave(self):
        """
        Create the dock to save the TACs with errors
        """
        self.ErrorTACButton = QCheckBox()
        self.ErrorTACButton.stateChanged.connect(self.setValueErrorTAC)
        self.ErrorTACType = QComboBox()
        self.ErrorTACType.addItem("Error TAC Images")
        self.ErrorTACType.addItem("Raw Values")
        self.ErrorTACType.addItem("All")
        self.ErrorTACButton.setToolTip("Export the specific Error TAC curve, either via a .txt file, the image itself (.png), or both.\n-1 for all of them.")
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
        slider.setToolTip("If -1, all TACs with errors will be saved")
        number.setToolTip("If -1, all TACs with errors will be saved")
        layout.addWidget(slider)
        layout.addWidget(number)
        self.ErrorTACsSaveValues = slider
        self.ErrorTACType.activated[str].connect(self.ErrorTACComboChanged)

        self.generalLayout.addWidget(QLabel("Error TACs"),self.current_line,0)
        self.generalLayout.addWidget(self.ErrorTACButton,self.current_line,1)
        self.generalLayout.addWidget(subWidget,self.current_line,2)
        self.generalLayout.addWidget(self.ErrorTACType,self.current_line,3)
        self.current_line +=1

    def _createDynestyResultSave(self):
        """
        Saves all the results from Dynesty
        """
        self.DynestyParamButton = QCheckBox()
        self.DynestyParamButton.stateChanged.connect(self.setValueDynestyParam)
        self.DynestyParamType = QComboBox()
        self.DynestyParamType.addItem("Dynesty Param")
        self.DynestyParamType.addItem("Raw Values")
        self.DynestyParamType.addItem("All")
        self.DynestyParamButton.setToolTip("Export the specific Dynesty Params, either via a .txt file, the image itself (.png), or both.\n-1 for all of them.")
        subWidget = QWidget()
        layout = QHBoxLayout()
        subWidget.setLayout(layout)
        slider = QSlider(Qt.Horizontal)
        number = QLineEdit()
        number.setText(str(-1))
        slider.setRange(-1,self.Image.bayesian_counter-1)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setSingleStep(1)
        slider.setValue(-1)
        number.setFixedWidth(30)
        slider.valueChanged.connect(partial(self.set_value_slider,slider,number))
        number.editingFinished.connect(partial(self.set_value_line_edit,slider,number))
        slider.setToolTip("If -1, all Params with errors will be saved")
        number.setToolTip("If -1, all Params with errors will be saved")
        layout.addWidget(slider)
        layout.addWidget(number)
        self.DynestyParamSaveValues = slider
        self.DynestyParamType.activated[str].connect(self.DynestyParamComboChanged)

        self.generalLayout.addWidget(QLabel("Dynesty Param"),self.current_line,0)
        self.generalLayout.addWidget(self.DynestyParamButton,self.current_line,1)
        self.generalLayout.addWidget(subWidget,self.current_line,2)
        self.generalLayout.addWidget(self.DynestyParamType,self.current_line,3)
        self.current_line +=1

    def _createDynestyGraphsSave(self):
        """
        Saves the graphs from Dynesty
        """
        self.DynestyGraphButton = QCheckBox()
        self.DynestyGraphButton.stateChanged.connect(self.setValueDynestyGraph)
        self.DynestyGraphType = QComboBox()
        self.DynestyGraphType.addItem("RunPlot")
        self.DynestyGraphType.addItem("TracePlot")
        self.DynestyGraphType.addItem("CornerPlot")
        self.DynestyGraphType.addItem("All")
        self.DynestyGraphType.setToolTip("Export the specific Dynesty Graphs for a given Dynesty analysis.\n-1 for all of them.")
        subWidget = QWidget()
        layout = QHBoxLayout()
        subWidget.setLayout(layout)
        slider = QSlider(Qt.Horizontal)
        number = QLineEdit()
        number.setText(str(-1))
        slider.setRange(-1,self.Image.bayesian_dynesty_counter-1)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setSingleStep(1)
        slider.setValue(-1)
        number.setFixedWidth(30)
        slider.valueChanged.connect(partial(self.set_value_slider,slider,number))
        number.editingFinished.connect(partial(self.set_value_line_edit,slider,number))
        slider.setToolTip("If -1, all Dynesty Analysis will be saved")
        number.setToolTip("If -1, all Dynesty Analysis will be saved")
        layout.addWidget(slider)
        layout.addWidget(number)
        self.DynestyGraphSaveValues = slider
        self.DynestyGraphType.activated[str].connect(self.DynestyGraphComboChanged)

        self.generalLayout.addWidget(QLabel("Dynesty Graph"),self.current_line,0)
        self.generalLayout.addWidget(self.DynestyGraphButton,self.current_line,1)
        self.generalLayout.addWidget(subWidget,self.current_line,2)
        self.generalLayout.addWidget(self.DynestyGraphType,self.current_line,3)
        self.current_line +=1

    def _createExportAll(self):
        """
        Create the Export Button
        """
        self.saveButton = QPushButton("Export")
        self.saveButton.setToolTip("Export the selected choices from above.\nBoxes need to be checked to be exported.")
        self.saveButton.clicked.connect(self.exportInfo)

        self.generalLayout.addWidget(self.saveButton,self.current_line,2)
        self.current_line +=1
    def _createExportList(self):
        """
        Create the docks for the Export Window
        """
        self._createHeader()
        self._createPathDock()
        self._createHeaderDock()
        self._createDicomSave()
        self._createParamSave()
        self._createLogSave()
        self._createTACsSave()
        self._createSegmFlatSave()
        self._createDiceSave()
        self._createJaccardSave()
        self._createErrorTACsSave()
        self._createDynestyResultSave()
        self._createDynestyGraphsSave()

        self._createExportAll()

    def setValueExportDicom(self):
        """Set the export DicomImage with the checkbox"""
        self.ExportDicom = self.DicomImageButton.isChecked()
    def setValueExportParam(self):
        """Set the export GUIParam with the checkbox"""
        self.ExportParam = self.ParamButton.isChecked()
    def setValueExportLog(self):
        """Set the export GUILog with the checkbox"""
        self.ExportLog = self.LogButton.isChecked()
    def setValueTAC(self):
        """Set the export TACs with the checkbox"""
        self.ExportTAC = self.TACButton.isChecked()
    def setValueSegmFlat(self):
        """Set the export Segmentation Flats with the checkbox"""
        self.ExportSegFlat = self.TACButton.isChecked()
    def setValueExportDice(self):
        """Set the export Dice Coefficients with the checkbox"""
        self.ExportDice = self.DiceCoeffButton.isChecked()
    def setValueExportJaccard(self):
        """Set the export Jaccard Coefficients with the checkbox"""
        self.ExportJaccard = self.JaccardCoeffButton.isChecked()
    def setValueErrorTAC(self):
        """Set the export Error TACs with the checkbox"""
        self.ExportErrorTAC = self.ErrorTACButton.isChecked()
    def setValueDynestyParam(self):
        """Set the export Dynesty Parameters with the checkbox"""
        self.ExportDynestyParam = self.DynestyParamButton.isChecked()
    def setValueDynestyGraph(self):
        """Set the export Dynesty Graphs with the checkbox"""
        self.ExportDynestyGraphs = self.DynestyGraphButton.isChecked()
    def TACComboChanged(self):
        """Set the type of TACs with the checkbox"""
        self.TACTypeSave = self.TACType.currentText()
    def ErrorTACComboChanged(self):
        """Set the type of Errors with the checkbox"""
        self.ErrorTACTypeSave = self.ErrorTACType.currentText()
    def DynestyParamComboChanged(self):
        """Set the type of Errors with the checkbox"""
        self.DynestyParamTypeSave = self.DynestyParamType.currentText()
    def DynestyGraphComboChanged(self):
        """Set the type of Graphs with the checkbox"""
        self.DynestyGraphTypeSave = self.DynestyGraphType.currentText()
    def SegFlatComboChanged(self):
        """Set the type of Segmentation Flats with the checkbox"""
        self.SegFlatTypeSave = self.SegFlatType.currentText()
    def set_value_slider(self,slider:QSlider,lineedit:QLineEdit):
        """Set the value of slider with the lineedit"""
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
        """Create an error message. Used when something doesn't work"""
        alert = QMessageBox()
        if message =="":
            alert.setText("An error occurred")
        else:
            alert.setText(message)
        alert.exec()

    def exportDicomImageProcess(self):
        """Exporting of the DicomImage class"""
        if self.pathName.text() != "" and self.headerName.text() != "":
            PF.pickle_save(self.Image,self.pathName.text()+self.headerName.text()+"_DicomImage.pkl")
        else:
            self._createErrorMessage("Unable to Save")
    def exportParamProcess(self):
        """Exporting of the GUIParam class"""
        if self.pathName.text() != "" and self.headerName.text() != "":
            PF.pickle_save(self.parameters,self.pathName.text()+self.headerName.text()+"_Parameters.pkl")
        else:
            self._createErrorMessage("Unable to Save")
    def exportLogProcess(self):
        """Exporting of the DicomImage Log"""
        if self.pathName.text() != "" and self.headerName.text() != "":
            file_name = self.pathName.text()+self.headerName.text()+"_Log.txt"
            text_file = open(file_name,"w")
            text_file.write(self.Image.progress_log)
            text_file.close()
        else:
            self._createErrorMessage("Unable to Save")
    def exportDiceProcess(self):
        """Saving of the Dice Coefficients graph"""
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
        """Saving of the Jaccard Coefficients graph"""
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
        """Saving of the TACs graphs"""
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
        """Saving of the Segmentation Flats graphs"""
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
        """Saving of the TACs with Errors graphs"""
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
    def exportDynestyParamProcess(self):
        """Saving of the Dynesty Parameters"""
        if self.pathName.text() != "" and self.headerName.text() != "":
            k = self.DynestyParamSaveValues.value()
            if k == -1:
                z = np.arange(self.Image.bayesian_results_avg.shape[1])
            else:
                z = np.array([k])
            if self.DynestyParamTypeSave in ["All","Dynesty Param"]:
                for i in range(z.shape[0]):
                    fig = plt.figure()
                    plt.xlabel("Acq"); plt.ylabel("Param");plt.title(f"Dynesty Parameter {z[i]}");plt.grid()
                    plt.errorbar(np.arange(self.Image.bayesian_results_avg.shape[0]),
                                self.Image.bayesian_results_avg[:,z[i]],
                                yerr=[self.Image.bayesian_results_e_down[:,z[i]],
                                self.Image.bayesian_results_e_up[:,z[i]]])
                    fig.savefig(self.pathName.text()+self.headerName.text()+f"_Param_{z[i]}_Dynesty_Param.png")
                    del fig
            if self.DynestyParamTypeSave in ["All","Raw Values"]:
                arrayTAC = np.zeros((self.Image.bayesian_results_avg.shape[0],3*z.shape[0]+1))
                arrayTAC[:,0] = np.arange(self.Image.bayesian_results_avg.shape[0])
                for i in range(z.shape[0]):
                    arrayTAC[:,i+1] = self.Image.bayesian_results_avg[:,i]
                    arrayTAC[:,z.shape[0]+i+1] = self.Image.bayesian_results_e_down[:,i]
                    arrayTAC[:,2*z.shape[0]+i+1] = self.Image.bayesian_results_e_up[:,i]
                np.savetxt(self.pathName.text()+self.headerName.text()+f"_Param_{k}_Dynesty_Param.csv",arrayTAC,delimiter=';')
        else:
            self._createErrorMessage("Unable to Save")
    def exportDynestyGraphsProcess(self):
        """Saving of the Dynesty Graphs"""
        if self.pathName.text() != "" and self.headerName.text() != "":
            k = self.DynestyGraphSaveValues.value()
            if k == -1:
                z = np.arange(self.Image.bayesian_dynesty_counter)
            else:
                z = np.array([k])
            for i in range(z.shape[0]):
                if self.DynestyGraphTypeSave in ["All","RunPlot"]:
                    self.exportDynestyRunPlot(z[i])
                if self.DynestyGraphTypeSave in ["All","TracePlot"]:
                    self.exportDynestyTracePlot(z[i])
                if self.DynestyGraphTypeSave in ["All","CornerPlot"]:
                    self.exportDynestyCornerPlot(z[i])

    def exportDynestyRunPlot(self,index:int):
        """Saving the Dynesty RunPlot"""
        fig = self.Image.bayesian_graphs_runplot[f"{index}"]
        fig.savefig(self.pathName.text()+self.headerName.text()+f"_Param_{index}_Dynesty_RunPlot.png")

    def exportDynestyTracePlot(self,index:int):
        """Saving the Dynesty TracePlot"""
        fig = self.Image.bayesian_graphs_traceplot[f"{index}"]
        fig.savefig(self.pathName.text()+self.headerName.text()+f"_Param_{index}_Dynesty_TracePlot.png")

    def exportDynestyCornerPlot(self,index:int):
        """Saving the Dynesty CornerPlot"""
        fig = self.Image.bayesian_graphs_cornerplot[f"{index}"]
        fig.savefig(self.pathName.text()+self.headerName.text()+f"_Param_{index}_Dynesty_CornerPlot.png")

    def exportInfo(self):
        """Activated when clicked on 'Export'. Undertake all the export processes."""
        try:
            if self.ExportDicom:
                self.exportDicomImageProcess()
            if self.ExportParam:
                self.exportParamProcess()
            if self.ExportLog:
                self.exportLogProcess()
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
            if self.ExportDynestyParam:
                self.exportDynestyParamProcess()
            if self.ExportDynestyGraphs:
                self.exportDynestyGraphsProcess()
            self._createErrorMessage("Export Successful")
        except:
            self._createErrorMessage("Unable to Export")