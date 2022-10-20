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
class ParamWindow(QMainWindow):
    """
    Class to open a parameter window to get user's inputs
    """
    def __init__(self,parameters:GUIParameters,parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 750)
        self.parameters = parameters
        self.setWindowTitle("Parameters")
        self.generalLayout = QGridLayout()
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)
        self._createParamList()
    def _createSeedSliders(self):
        sizeText = 30
        seedWidget = QWidget()
        layout = QGridLayout()
        seedWidget.setLayout(layout)
        AxialValueHeaderSeed = QLabel("Ax:")
        SagittalValueHeaderSeed = QLabel("Sag:")
        CoronalValueHeaderSeed = QLabel("Cor:")
        self.sliderSeedAxial = QSlider(Qt.Horizontal)
        self.sliderSeedSagittal = QSlider(Qt.Horizontal)
        self.sliderSeedCoronal = QSlider(Qt.Horizontal)
        self.sliderAxialValueSeed = QLineEdit()
        self.sliderSagittalValueSeed = QLineEdit()
        self.sliderCoronalValueSeed = QLineEdit()
        self.sliderSeedAxial.setMinimum(0);self.sliderSeedAxial.setMaximum(self.parameters._size[1]-1)
        self.sliderSeedSagittal.setMinimum(0);self.sliderSeedSagittal.setMaximum(self.parameters._size[2]-1)
        self.sliderSeedCoronal.setMinimum(0);self.sliderSeedCoronal.setMaximum(self.parameters._size[3]-1)
        self.sliderSeedAxial.setValue(self.parameters.seed[0])
        self.sliderSeedSagittal.setValue(self.parameters.seed[1])
        self.sliderSeedCoronal.setValue(self.parameters.seed[2])
        self.sliderSeedAxial.setTickPosition(QSlider.TicksBothSides);self.sliderSeedAxial.setSingleStep(1)
        self.sliderSeedSagittal.setTickPosition(QSlider.TicksBothSides);self.sliderSeedSagittal.setSingleStep(1)
        self.sliderSeedCoronal.setTickPosition(QSlider.TicksBothSides);self.sliderSeedCoronal.setSingleStep(1)
        self.sliderAxialValueSeed.setFixedWidth(sizeText)
        self.sliderSagittalValueSeed.setFixedWidth(sizeText)
        self.sliderCoronalValueSeed.setFixedWidth(sizeText)

        self.sliderAxialValueSeed.setText(f"{self.parameters.seed[0]}")
        self.sliderSagittalValueSeed.setText(f"{self.parameters.seed[1]}")
        self.sliderCoronalValueSeed.setText(f"{self.parameters.seed[2]}")
        
        self.sliderAxialValueSeed.editingFinished.connect(partial(self.set_value_line_edit,self.sliderSeedAxial,self.sliderAxialValueSeed))
        self.sliderSagittalValueSeed.editingFinished.connect(partial(self.set_value_line_edit,self.sliderSeedSagittal,self.sliderSagittalValueSeed))
        self.sliderCoronalValueSeed.editingFinished.connect(partial(self.set_value_line_edit,self.sliderSeedCoronal,self.sliderCoronalValueSeed))
        
        self.sliderSeedAxial.valueChanged.connect(partial(self.set_value_slider,self.sliderSeedAxial,self.sliderAxialValueSeed))
        self.sliderSeedSagittal.valueChanged.connect(partial(self.set_value_slider,self.sliderSeedSagittal,self.sliderSagittalValueSeed))
        self.sliderSeedCoronal.valueChanged.connect(partial(self.set_value_slider,self.sliderSeedCoronal,self.sliderCoronalValueSeed))

        layout.addWidget(AxialValueHeaderSeed,1,0)
        layout.addWidget(SagittalValueHeaderSeed,3,0)
        layout.addWidget(CoronalValueHeaderSeed,2,0)
        layout.addWidget(self.sliderSeedAxial,1,1)
        layout.addWidget(self.sliderSeedSagittal,3,1)
        layout.addWidget(self.sliderSeedCoronal,2,1)
        layout.addWidget(self.sliderAxialValueSeed,1,2)
        layout.addWidget(self.sliderCoronalValueSeed,2,2)
        layout.addWidget(self.sliderSagittalValueSeed,3,2)
        return seedWidget
    def _createSubImageSliders(self):
        sizeText = 30
        subImageWidget = QWidget()
        layout = QGridLayout()
        subImageWidget.setLayout(layout)    
        AcqValueHeaderSubIm = QLabel("Acq:")
        AxialValueHeaderSubIm = QLabel("Ax:")
        SagittalValueHeaderSubI = QLabel("Sag:")
        CoronalValueHeaderSubIm = QLabel("Cor:")

        self.sliderAcqSubIm = QSlider(Qt.Horizontal)
        self.sliderAxialSubIm = QSlider(Qt.Horizontal)
        self.sliderSagittalSubIm = QSlider(Qt.Horizontal)
        self.sliderCoronalSubIm = QSlider(Qt.Horizontal)

        self.sliderAcqSubIm.setMinimum(0);self.sliderAcqSubIm.setMaximum(self.parameters._size[0]-1)
        self.sliderAxialSubIm.setMinimum(0);self.sliderAxialSubIm.setMaximum(self.parameters._size[1]-1)
        self.sliderSagittalSubIm.setMinimum(0);self.sliderSagittalSubIm.setMaximum(self.parameters._size[2]-1)
        self.sliderCoronalSubIm.setMinimum(0);self.sliderCoronalSubIm.setMaximum(self.parameters._size[3]-1)
        self.sliderAcqSubIm.setTickPosition(QSlider.TicksBothSides);self.sliderAcqSubIm.setSingleStep(1)
        self.sliderAxialSubIm.setTickPosition(QSlider.TicksBothSides);self.sliderAxialSubIm.setSingleStep(1)
        self.sliderSagittalSubIm.setTickPosition(QSlider.TicksBothSides);self.sliderSagittalSubIm.setSingleStep(1)
        self.sliderCoronalSubIm.setTickPosition(QSlider.TicksBothSides);self.sliderCoronalSubIm.setSingleStep(1)

        self.sliderAcqValueSubImMin = QLineEdit()
        self.sliderAxialValueSubImMin = QLineEdit()
        self.sliderSagittalValueSubImMin = QLineEdit()
        self.sliderCoronalValueSubImMin = QLineEdit()
        self.sliderAcqValueSubImMax = QLineEdit()
        self.sliderAxialValueSubImMax = QLineEdit()
        self.sliderSagittalValueSubImMax = QLineEdit()
        self.sliderCoronalValueSubImMax = QLineEdit()
        self.sliderAcqValueSubImMin.setFixedWidth(sizeText)
        self.sliderAxialValueSubImMin.setFixedWidth(sizeText)
        self.sliderSagittalValueSubImMin.setFixedWidth(sizeText)
        self.sliderCoronalValueSubImMin.setFixedWidth(sizeText)
        self.sliderAcqValueSubImMax.setFixedWidth(sizeText)
        self.sliderAxialValueSubImMax.setFixedWidth(sizeText)
        self.sliderSagittalValueSubImMax.setFixedWidth(sizeText)
        self.sliderCoronalValueSubImMax.setFixedWidth(sizeText)

        self.sliderAcqValueSubImMin.setText(f"{self.parameters.subImage[0,0]}")
        self.sliderAxialValueSubImMin.setText(f"{self.parameters.subImage[1,0]}")
        self.sliderSagittalValueSubImMin.setText(f"{self.parameters.subImage[3,0]}")
        self.sliderCoronalValueSubImMin.setText(f"{self.parameters.subImage[2,0]}")
        self.sliderAcqValueSubImMax.setText(f"{self.parameters.subImage[0,1]}")
        self.sliderAxialValueSubImMax.setText(f"{self.parameters.subImage[1,1]}")
        self.sliderSagittalValueSubImMax.setText(f"{self.parameters.subImage[3,1]}")
        self.sliderCoronalValueSubImMax.setText(f"{self.parameters.subImage[2,1]}")

        self.sliderAcqValueSubImMin.editingFinished.connect(partial(self.set_value_line_edit_noSlider,self.sliderAcqValueSubImMin))
        self.sliderAcqValueSubImMax.editingFinished.connect(partial(self.set_value_line_edit_noSlider,self.sliderAcqValueSubImMax))
        self.sliderAxialValueSubImMin.editingFinished.connect(partial(self.set_value_line_edit_noSlider,self.sliderAxialValueSubImMin))
        self.sliderAxialValueSubImMax.editingFinished.connect(partial(self.set_value_line_edit_noSlider,self.sliderAxialValueSubImMax))
        self.sliderSagittalValueSubImMin.editingFinished.connect(partial(self.set_value_line_edit_noSlider,self.sliderSagittalValueSubImMin))
        self.sliderSagittalValueSubImMax.editingFinished.connect(partial(self.set_value_line_edit_noSlider,self.sliderSagittalValueSubImMax))
        self.sliderCoronalValueSubImMin.editingFinished.connect(partial(self.set_value_line_edit_noSlider,self.sliderCoronalValueSubImMin))
        self.sliderCoronalValueSubImMax.editingFinished.connect(partial(self.set_value_line_edit_noSlider,self.sliderCoronalValueSubImMax))

        layout.addWidget(AcqValueHeaderSubIm,0,0)
        layout.addWidget(AxialValueHeaderSubIm,1,0)
        layout.addWidget(SagittalValueHeaderSubI,3,0)
        layout.addWidget(CoronalValueHeaderSubIm,2,0)
        layout.addWidget(self.sliderAcqSubIm,0,1)
        layout.addWidget(self.sliderAxialSubIm,1,1)
        layout.addWidget(self.sliderSagittalSubIm,3,1)
        layout.addWidget(self.sliderCoronalSubIm,2,1)
        layout.addWidget(self.sliderAcqValueSubImMin,0,2)
        layout.addWidget(self.sliderAcqValueSubImMax,0,3)
        layout.addWidget(self.sliderAxialValueSubImMin,1,2)
        layout.addWidget(self.sliderAxialValueSubImMax,1,3)
        layout.addWidget(self.sliderCoronalValueSubImMin,2,2)
        layout.addWidget(self.sliderCoronalValueSubImMax,2,3)
        layout.addWidget(self.sliderSagittalValueSubImMin,3,2)
        layout.addWidget(self.sliderSagittalValueSubImMax,3,3)
        return subImageWidget   

    def _createBoolBox(self):
        btn = QCheckBox()
        return btn

    def _createSegmType(self):
        self.SegmCombo = QComboBox()
        self.SegmCombo.addItem("ICM")
        self.SegmCombo.addItem("Canny Filled")
        self.SegmCombo.addItem("Canny Contour")
        self.SegmCombo.addItem("Ellipsoid")
        self.SegmCombo.addItem("k Mean")
        self.SegmCombo.addItem("Threshold")
        self.SegmCombo.addItem("Filling (very slow)")
        self.SegmCombo.addItem("Filling f (very slow)")
        self.SegmCombo.setCurrentText(self.parameters.SegmType)
        self.SegmCombo.activated[str].connect(self.SegmCombo_Changed)
        return self.SegmCombo
    def _createIntInput(self,initvalue:float):
        subWidget = QWidget()
        layout = QHBoxLayout()
        subWidget.setLayout(layout)
        slider = QSlider(Qt.Horizontal)
        number = QLineEdit()
        number.setText(str(initvalue))
        slider.setSliderPosition(initvalue)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setMinimumWidth(200)
        slider.valueChanged.connect(partial(self.set_value_slider,slider,number))
        number.editingFinished.connect(partial(self.set_value_line_edit,slider,number))
        number.setMaximumWidth(50)
        layout.addWidget(slider)
        layout.addWidget(number)
        return subWidget,slider
    def _createParamList(self):
        params = [attr for attr in dir(self.parameters) if not callable(getattr(self.parameters, attr)) and not attr.startswith("__")and not attr.startswith("_")]
        params_ = [attr for attr in dir(self.parameters) if not callable(getattr(self.parameters, attr)) and not attr.startswith("__")and attr.startswith("_")]
        var = vars(self.parameters)
        text1 = QLabel("Parameter")
        text2 = QLabel("Values")
        text3 = QLabel("New Values")
        self.generalLayout.addWidget(text1,0,0)
        self.generalLayout.addWidget(text2,0,1)
        self.generalLayout.addWidget(text3,0,2)
        for i in range(len(params_)):
            if str(params_[i]) == "_size":
                paramNew = QLabel(params_[i]+":")
                labelNew = QLabel(str(var[f"{params_[i]}"]))
            try:
                self.generalLayout.addWidget(paramNew,i+1,0)
                self.generalLayout.addWidget(labelNew,i+1,1)
            except:
                pass 
        for i in range(len(params)):
            paramNew = QLabel(params[i]+":")
            if str(params[i]) != "alpha":
                labelNew = QLabel(str(var[f"{params[i]}"]))
            else:
                labelNew = QLabel(f"{self.parameters.alpha:.4f}")
            if str(params[i]) == "seed":
                self.label_Seed = labelNew
                btnNew = self._createSeedSliders()
            elif str(params[i]) == "subImage":
                btnNew = self._createSubImageSliders()
            elif isinstance(var[f"{params[i]}"],bool):
                btnNew = self._createBoolBox()
                btnNew.setChecked(var[f"{params[i]}"])
                if str(params[i]) == "SaveSegm":
                    btnNew.stateChanged.connect(partial(self.set_value_checked_SaveSegm,btnNew))
                elif str(params[i]) == "doCurves":
                    btnNew.stateChanged.connect(partial(self.set_value_checked_doCurves,btnNew))
                elif str(params[i]) == "doStats":
                    btnNew.stateChanged.connect(partial(self.set_value_checked_doStats,btnNew))
                elif str(params[i]) == "doCoefficients":
                    btnNew.stateChanged.connect(partial(self.set_value_checked_doCoefficients,btnNew))
            elif isinstance(var[f"{params[i]}"],(int,float)):
                btnNew,slider = self._createIntInput(var[f"{params[i]}"])
                slider.valueChanged.connect(self.update_int)
                if str(params[i]) == "SegmAcq":
                    slider.setTickInterval(1)
                    slider.setRange(-1,self.parameters._size[0])
                    slider.setValue(self.parameters.SegmAcq)
                    self.sliderSegmAcq = slider   
                elif str(params[i]) == "alpha": 
                    slider.setRange(0,1000)
                    slider.setValue(int(10/self.parameters.alpha))
                    slider.setTickInterval(100)
                    self.sliderAlpha = slider
                elif str(params[i]) == "max_iter_ICM": 
                    slider.setRange(1,10000)
                    slider.setTickInterval(1000)
                    slider.setValue(self.parameters.max_iter_ICM)
                    self.sliderMaxIter = slider
                elif str(params[i]) == "max_iter_kmean_ICM": 
                    slider.setRange(1,10000)
                    slider.setTickInterval(1000)
                    slider.setValue(self.parameters.max_iter_kmean_ICM)
                    self.sliderMaxIterKmean = slider
            elif str(params[i]) == "SegmType":
                btnNew = self._createSegmType()
            self.generalLayout.addWidget(paramNew,i+len(params_)+1,0)
            self.generalLayout.addWidget(labelNew,i+len(params_)+1,1)
            try:
                self.generalLayout.addWidget(btnNew,i+len(params_)+1,2)
            except:
                pass
    def set_value_slider(self,slider:QSlider,lineedit:QLineEdit):
        lineedit.setText(str(slider.value()))
        return slider.value()
    def SegmCombo_Changed(self):
        self.parameters.SegmType = self.SegmCombo.currentText()
    def set_value_checked_doCoefficients(self,box:QCheckBox):
        self.parameters.doCoefficients = box.isChecked()
    def set_value_checked_doStats(self,box:QCheckBox):
        self.parameters.doStats = box.isChecked()
    def set_value_checked_SaveSegm(self,box:QCheckBox):
        self.parameters.SaveSegm = box.isChecked()
    def set_value_checked_doCurves(self,box:QCheckBox):
        self.parameters.doCurves = box.isChecked()
    def set_value_slider(self,slider:QSlider,lineedit:QLineEdit):
        lineedit.setText(str(slider.value()))
        try:
            self.update_seed()
        except: pass
        return slider.value()
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
        self.update_seed()
    def set_value_line_edit_noSlider(self,lineedit:QLineEdit):
        """
        Changes the value of the 
        """
        try:
            lineedit.setText(f"{int(lineedit.text())}")
        except:
            lineedit.setText("0")
        self.update_subImage()
    def update_seed(self):
        self.parameters.seed[0] = self.sliderAxialValueSeed.text()
        self.parameters.seed[1] = self.sliderSagittalValueSeed.text()
        self.parameters.seed[2] = self.sliderCoronalValueSeed.text()
    def update_subImage(self):
        self.parameters.subImage[0,0] = self.sliderAcqValueSubImMin.text()
        self.parameters.subImage[0,1] = self.sliderAcqValueSubImMax.text()
        self.parameters.subImage[1,0] = self.sliderAxialValueSubImMin.text()
        self.parameters.subImage[1,1] = self.sliderAxialValueSubImMax.text()
        self.parameters.subImage[2,0] = self.sliderCoronalValueSubImMin.text()
        self.parameters.subImage[2,1] = self.sliderCoronalValueSubImMax.text()
        self.parameters.subImage[3,0] = self.sliderSagittalValueSubImMin.text()
        self.parameters.subImage[3,1] = self.sliderSagittalValueSubImMax.text()
    def update_int(self):
        try:
            self.parameters.SegmAcq = self.sliderSegmAcq.value()
            try:
                self.parameters.alpha = 10/self.sliderAlpha.value()
            except:
                self.parameters.alpha = 0
            self.parameters.max_iter_ICM = self.sliderMaxIter.value()
            self.parameters.max_iter_kmean_ICM = self.sliderMaxIterKmean.value()
        except: pass