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
        self.initialize_param_window()
        centralWidget.resize(centralWidget.sizeHint());

    def initialize_param_window(self):
        self.current_line = 1
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
        
        self.generalLayout.addWidget(QLabel("Seed"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.seed}"),self.current_line,1)
        self.generalLayout.addWidget(seedWidget,self.current_line,2)
        self.current_line += 1

    def _createCenterEllipsoidSliders(self):
        sizeText = 30
        seedWidget = QWidget()
        layout = QGridLayout()
        seedWidget.setLayout(layout)
        AxialValueHeaderCenter = QLabel("Ax:")
        SagittalValueHeaderCenter = QLabel("Sag:")
        CoronalValueHeaderCenter = QLabel("Cor:")
        self.sliderCenterAxial = QSlider(Qt.Horizontal)
        self.sliderCenterSagittal = QSlider(Qt.Horizontal)
        self.sliderCenterCoronal = QSlider(Qt.Horizontal)
        self.sliderAxialValueCenter = QLineEdit()
        self.sliderSagittalValueCenter = QLineEdit()
        self.sliderCoronalValueCenter = QLineEdit()
        self.sliderCenterAxial.setMinimum(0);self.sliderCenterAxial.setMaximum(self.parameters._size[1]-1)
        self.sliderCenterSagittal.setMinimum(0);self.sliderCenterSagittal.setMaximum(self.parameters._size[2]-1)
        self.sliderCenterCoronal.setMinimum(0);self.sliderCenterCoronal.setMaximum(self.parameters._size[3]-1)
        self.sliderCenterAxial.setValue(self.parameters.centerEllipsoid[0])
        self.sliderCenterSagittal.setValue(self.parameters.centerEllipsoid[2])
        self.sliderCenterCoronal.setValue(self.parameters.centerEllipsoid[1])
        self.sliderCenterAxial.setTickPosition(QSlider.TicksBothSides);self.sliderCenterAxial.setSingleStep(1)
        self.sliderCenterSagittal.setTickPosition(QSlider.TicksBothSides);self.sliderCenterSagittal.setSingleStep(1)
        self.sliderCenterCoronal.setTickPosition(QSlider.TicksBothSides);self.sliderCenterCoronal.setSingleStep(1)
        self.sliderAxialValueCenter.setFixedWidth(sizeText)
        self.sliderSagittalValueCenter.setFixedWidth(sizeText)
        self.sliderCoronalValueCenter.setFixedWidth(sizeText)

        self.sliderAxialValueCenter.setText(f"{self.parameters.centerEllipsoid[0]}")
        self.sliderSagittalValueCenter.setText(f"{self.parameters.centerEllipsoid[2]}")
        self.sliderCoronalValueCenter.setText(f"{self.parameters.centerEllipsoid[1]}")
        
        self.sliderAxialValueCenter.editingFinished.connect(partial(self.set_value_line_edit,self.sliderCenterAxial,self.sliderAxialValueCenter))
        self.sliderSagittalValueCenter.editingFinished.connect(partial(self.set_value_line_edit,self.sliderCenterSagittal,self.sliderSagittalValueCenter))
        self.sliderCoronalValueCenter.editingFinished.connect(partial(self.set_value_line_edit,self.sliderCenterCoronal,self.sliderCoronalValueCenter))
        
        self.sliderCenterAxial.valueChanged.connect(partial(self.set_value_slider,self.sliderCenterAxial,self.sliderAxialValueCenter))
        self.sliderCenterSagittal.valueChanged.connect(partial(self.set_value_slider,self.sliderCenterSagittal,self.sliderSagittalValueCenter))
        self.sliderCenterCoronal.valueChanged.connect(partial(self.set_value_slider,self.sliderCenterCoronal,self.sliderCoronalValueCenter))

        layout.addWidget(AxialValueHeaderCenter,1,0)
        layout.addWidget(SagittalValueHeaderCenter,3,0)
        layout.addWidget(CoronalValueHeaderCenter,2,0)
        layout.addWidget(self.sliderCenterAxial,1,1)
        layout.addWidget(self.sliderCenterSagittal,3,1)
        layout.addWidget(self.sliderCenterCoronal,2,1)
        layout.addWidget(self.sliderAxialValueCenter,1,2)
        layout.addWidget(self.sliderCoronalValueCenter,2,2)
        layout.addWidget(self.sliderSagittalValueCenter,3,2)
        
        self.generalLayout.addWidget(QLabel("Center Ellips."),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.centerEllipsoid}"),self.current_line,1)
        self.generalLayout.addWidget(seedWidget,self.current_line,2)
        self.current_line += 1

    def _createAxesEllipsoidSliders(self):
        sizeText = 30
        seedWidget = QWidget()
        layout = QGridLayout()
        seedWidget.setLayout(layout)
        AxialValueHeaderAxes = QLabel("Ax:")
        SagittalValueHeaderAxes = QLabel("Sag:")
        CoronalValueHeaderAxes = QLabel("Cor:")
        self.sliderAxesAxial = QSlider(Qt.Horizontal)
        self.sliderAxesSagittal = QSlider(Qt.Horizontal)
        self.sliderAxesCoronal = QSlider(Qt.Horizontal)
        self.sliderAxialValueAxes = QLineEdit()
        self.sliderSagittalValueAxes = QLineEdit()
        self.sliderCoronalValueAxes = QLineEdit()
        self.sliderAxesAxial.setMinimum(0);self.sliderAxesAxial.setMaximum(self.parameters._size[1]-1)
        self.sliderAxesSagittal.setMinimum(0);self.sliderAxesSagittal.setMaximum(self.parameters._size[2]-1)
        self.sliderAxesCoronal.setMinimum(0);self.sliderAxesCoronal.setMaximum(self.parameters._size[3]-1)
        self.sliderAxesAxial.setValue(self.parameters.axesEllipsoid[0])
        self.sliderAxesSagittal.setValue(self.parameters.axesEllipsoid[2])
        self.sliderAxesCoronal.setValue(self.parameters.axesEllipsoid[1])
        self.sliderAxesAxial.setTickPosition(QSlider.TicksBothSides);self.sliderAxesAxial.setSingleStep(1)
        self.sliderAxesSagittal.setTickPosition(QSlider.TicksBothSides);self.sliderAxesSagittal.setSingleStep(1)
        self.sliderAxesCoronal.setTickPosition(QSlider.TicksBothSides);self.sliderAxesCoronal.setSingleStep(1)
        self.sliderAxialValueAxes.setFixedWidth(sizeText)
        self.sliderSagittalValueAxes.setFixedWidth(sizeText)
        self.sliderCoronalValueAxes.setFixedWidth(sizeText)

        self.sliderAxialValueAxes.setText(f"{self.parameters.axesEllipsoid[0]}")
        self.sliderSagittalValueAxes.setText(f"{self.parameters.axesEllipsoid[2]}")
        self.sliderCoronalValueAxes.setText(f"{self.parameters.axesEllipsoid[1]}")
        
        self.sliderAxialValueAxes.editingFinished.connect(partial(self.set_value_line_edit,self.sliderAxesAxial,self.sliderAxialValueAxes))
        self.sliderSagittalValueAxes.editingFinished.connect(partial(self.set_value_line_edit,self.sliderAxesSagittal,self.sliderSagittalValueAxes))
        self.sliderCoronalValueAxes.editingFinished.connect(partial(self.set_value_line_edit,self.sliderAxesCoronal,self.sliderCoronalValueAxes))
        
        self.sliderAxesAxial.valueChanged.connect(partial(self.set_value_slider,self.sliderAxesAxial,self.sliderAxialValueAxes))
        self.sliderAxesSagittal.valueChanged.connect(partial(self.set_value_slider,self.sliderAxesSagittal,self.sliderSagittalValueAxes))
        self.sliderAxesCoronal.valueChanged.connect(partial(self.set_value_slider,self.sliderAxesCoronal,self.sliderCoronalValueAxes))

        layout.addWidget(AxialValueHeaderAxes,1,0)
        layout.addWidget(SagittalValueHeaderAxes,3,0)
        layout.addWidget(CoronalValueHeaderAxes,2,0)
        layout.addWidget(self.sliderAxesAxial,1,1)
        layout.addWidget(self.sliderAxesSagittal,3,1)
        layout.addWidget(self.sliderAxesCoronal,2,1)
        layout.addWidget(self.sliderAxialValueAxes,1,2)
        layout.addWidget(self.sliderCoronalValueAxes,2,2)
        layout.addWidget(self.sliderSagittalValueAxes,3,2)
        
        self.generalLayout.addWidget(QLabel("Axes Ellips."),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.axesEllipsoid}"),self.current_line,1)
        self.generalLayout.addWidget(seedWidget,self.current_line,2)
        self.current_line += 1


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
        #layout.addWidget(self.sliderAcqSubIm,0,1)
        #layout.addWidget(self.sliderAxialSubIm,1,1)
        #layout.addWidget(self.sliderSagittalSubIm,3,1)
        #layout.addWidget(self.sliderCoronalSubIm,2,1)
        layout.addWidget(self.sliderAcqValueSubImMin,0,2)
        layout.addWidget(self.sliderAcqValueSubImMax,0,3)
        layout.addWidget(self.sliderAxialValueSubImMin,1,2)
        layout.addWidget(self.sliderAxialValueSubImMax,1,3)
        layout.addWidget(self.sliderCoronalValueSubImMin,2,2)
        layout.addWidget(self.sliderCoronalValueSubImMax,2,3)
        layout.addWidget(self.sliderSagittalValueSubImMin,3,2)
        layout.addWidget(self.sliderSagittalValueSubImMax,3,3)

        self.generalLayout.addWidget(QLabel("SubImage"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.subImage}"),self.current_line,1)
        self.generalLayout.addWidget(subImageWidget,self.current_line,2)
        self.current_line += 1
    def _createBoolBox(self):
        btn = QCheckBox()
        return btn
    def _createMethodCannyType(self):
        self.MethCombo = QComboBox()
        self.MethCombo.addItem("TaxiCab")
        self.MethCombo.setCurrentText(self.parameters.methodCanny)
        self.MethCombo.activated[str].connect(self.MethCombo_Changed)
        self.generalLayout.addWidget(QLabel("Method Canny"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.methodCanny}"),self.current_line,1)
        self.generalLayout.addWidget(self.MethCombo,self.current_line,2)
        self.current_line +=1
    def _createSegmType(self):
        self.SegmCombo = QComboBox()
        self.SegmCombo.addItem("None")
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
        self.generalLayout.addWidget(QLabel("Segm. Method"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.SegmType}"),self.current_line,1)
        self.generalLayout.addWidget(self.SegmCombo,self.current_line,2)
        self.current_line +=1
    def _createErrorType(self):
        self.ErrorCombo = QComboBox()
        self.ErrorCombo.addItem("None")
        self.ErrorCombo.addItem("Linear Shift")

        self.ErrorCombo.setCurrentText(self.parameters.ErrorType)
        self.ErrorCombo.activated[str].connect(self.ErrorMethodCombo_Changed)
        self.generalLayout.addWidget(QLabel("Error Method"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.ErrorType}"),self.current_line,1)
        self.generalLayout.addWidget(self.ErrorCombo,self.current_line,2)
        self.current_line +=1
    def _createFactorFFilling(self):
        btnNew,slider = self._createIntInput(self.parameters.factor_fill_f)
        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(100)
        slider.setRange(0,1000)
        slider.setValue(100*self.parameters.factor_fill_f)

        self.sliderFactorF = slider   
        self.generalLayout.addWidget(QLabel("Factor Filling"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.factor_fill_f}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1
    def _createFactorFillingRange(self):
        sizeText = 30
        RangeWidget = QWidget()
        layout = QGridLayout()
        RangeWidget.setLayout(layout)    

        self.FactorFRangeValueMin = QLineEdit()
        self.FactorFRangeValueMax = QLineEdit()
        self.FactorFRangeValueMin.setFixedWidth(sizeText)
        self.FactorFRangeValueMax.setFixedWidth(sizeText)
        self.FactorFRangeValueMin.setText(f"{self.parameters.factor_Fill_range[0]}")
        self.FactorFRangeValueMax.setText(f"{self.parameters.factor_Fill_range[1]}")
        layout.addWidget(self.FactorFRangeValueMin,0,0)
        layout.addWidget(self.FactorFRangeValueMax,0,1)
        self.FactorFRangeValueMin.editingFinished.connect(self.update_int)
        self.FactorFRangeValueMax.editingFinished.connect(self.update_int)

        self.generalLayout.addWidget(QLabel("Factor Filling Range"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.factor_Fill_range}"),self.current_line,1)
        self.generalLayout.addWidget(RangeWidget,self.current_line,2)
        self.current_line +=1
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
        number.setMaximumWidth(75)
        layout.addWidget(slider)
        layout.addWidget(number)
        return subWidget,slider
    def _createAcqValue(self):
        btnNew,slider = self._createIntInput(self.parameters.SegmAcq)
        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(1)
        slider.setRange(-1,self.parameters._size[0]-1)
        slider.setValue(self.parameters.SegmAcq)
        self.sliderSegmAcq = slider   

        self.generalLayout.addWidget(QLabel("Acq. Segm."),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.SegmAcq}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1
    def _createErrorValue(self):
        btnNew,slider = self._createIntInput(self.parameters.ErrorSegm)
        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(1)
        slider.setRange(-1,self.parameters._nbSeg-1)
        slider.setValue(self.parameters.ErrorSegm)
        self.sliderErrorAcq = slider   

        self.generalLayout.addWidget(QLabel("Seg. Error"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.ErrorSegm}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1

    def _createOrderShiftError(self):
        btnNew,slider = self._createIntInput(self.parameters.orderShift)
        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(1)
        slider.setRange(1,3)
        slider.setValue(self.parameters.orderShift)
        self.sliderErrorOrderShift = slider   

        self.generalLayout.addWidget(QLabel("Order"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.orderShift}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1
    def _createDShiftError(self):
        btnNew,slider = self._createIntInput(self.parameters.distanceShift)
        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(1)
        slider.setRange(1,10)
        slider.setValue(self.parameters.distanceShift)
        self.sliderErrorDistanceShift = slider   

        self.generalLayout.addWidget(QLabel("Distance"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.distanceShift}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1

    def _createSigmaCanny(self):
        btnNew,slider = self._createIntInput(self.parameters.sigmaCanny)
        slider.valueChanged.connect(self.update_int)
        self.sliderSigma = slider   
        slider.setRange(1,10000)
        try:
            slider.setValue(int(1000*self.parameters.sigmaCanny))
        except:
            slider.setValue(0)
        slider.setTickInterval(1000)
        self.generalLayout.addWidget(QLabel("Sigma Canny"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.sigmaCanny}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1
    def _createAlphaICM(self):
        btnNew,slider = self._createIntInput(self.parameters.alphaICM)
        slider.valueChanged.connect(self.update_int)
        self.sliderAlpha = slider   
        slider.setRange(0,10000)
        try:
            slider.setValue(int(1000*self.parameters.alphaICM))
        except:
            slider.setValue(0)
        slider.setTickInterval(1000)
        self.generalLayout.addWidget(QLabel("Alpha ICM"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.alphaICM}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1
    def _createCombCanny(self):
        btnNew,slider = self._createIntInput(self.parameters.combinationCanny)
        slider.valueChanged.connect(self.update_int)
        slider.setRange(1,3)
        slider.setTickInterval(1)
        slider.setValue(self.parameters.combinationCanny)
        self.sliderComb = slider   

        self.generalLayout.addWidget(QLabel("Comb. Canny"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.combinationCanny}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1
    def _createMaxiIterICM(self):
        btnNew,slider = self._createIntInput(self.parameters.max_iter_ICM)
        slider.valueChanged.connect(self.update_int)
        self.sliderMaxIter = slider   
        slider.setRange(1,10000)
        slider.setTickInterval(1000)
        slider.setValue(self.parameters.max_iter_ICM)
        self.generalLayout.addWidget(QLabel("Max. Iter."),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.max_iter_ICM}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1
    def _createMaxiIterKMeanICM(self):
        btnNew,slider = self._createIntInput(self.parameters.max_iter_kmean_ICM)
        slider.valueChanged.connect(self.update_int)
        self.sliderMaxIterKmean = slider   
        slider.setRange(1,10000)
        slider.setTickInterval(1000)
        slider.setValue(self.parameters.max_iter_kmean_ICM)
        self.generalLayout.addWidget(QLabel("Max. Iter K Mean"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.max_iter_kmean_ICM}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1
    def _createStepsFilling(self):
        btnNew,slider = self._createIntInput(self.parameters.steps_filling)
        slider.valueChanged.connect(self.update_int)   
        slider.setRange(0,1000)
        slider.setTickInterval(100)
        slider.setValue(self.parameters.steps_filling)
        self.sliderStepsFilling = slider
        self.generalLayout.addWidget(QLabel("Steps Filling"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.steps_filling}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1
    def _createMaxIterFilling(self):
        btnNew,slider = self._createIntInput(self.parameters.max_iter_fill)
        slider.valueChanged.connect(self.update_int)
        self.sliderMaxIterFilling = slider   
        slider.setRange(1,1000)
        slider.setTickInterval(100)
        slider.setValue(self.parameters.max_iter_fill)
        self.generalLayout.addWidget(QLabel("Max. Iter Filling"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.max_iter_fill}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1
    def _createVerboseGraphFill(self):
        btnNew = self._createBoolBox()
        btnNew.setChecked(self.parameters.verbose_graph_fill)
        btnNew.stateChanged.connect(partial(self.set_value_checked_VerboseGraphFill,btnNew))
        self.generalLayout.addWidget(QLabel("Graph Filling"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.verbose_graph_fill}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1
    def _createSaveBox(self):
        btnNew = self._createBoolBox()
        btnNew.setChecked(self.parameters.SaveSegm)
        btnNew.stateChanged.connect(partial(self.set_value_checked_SaveSegm,btnNew))
        self.generalLayout.addWidget(QLabel("Save"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.SaveSegm}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1
    def _createStatsBox(self):
        btnNew = self._createBoolBox()
        btnNew.setChecked(self.parameters.doStats)
        btnNew.stateChanged.connect(partial(self.set_value_checked_doStats,btnNew))
        self.generalLayout.addWidget(QLabel("Stats"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.doStats}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1
    def _createCurvesBox(self):
        btnNew = self._createBoolBox()
        btnNew.setChecked(self.parameters.doCurves)
        btnNew.stateChanged.connect(partial(self.set_value_checked_doCurves,btnNew))
        self.generalLayout.addWidget(QLabel("Curves"),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.doCurves}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1
    def _createCoefficientsBox(self):
        btnNew = self._createBoolBox()
        btnNew.setChecked(self.parameters.doCoefficients)
        btnNew.stateChanged.connect(partial(self.set_value_checked_doCoefficients,btnNew))
        self.generalLayout.addWidget(QLabel("Coeff."),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.doCoefficients}"),self.current_line,1)
        self.generalLayout.addWidget(btnNew,self.current_line,2)
        self.current_line +=1
    def _createThresholdBox(self):
        btnNew,slider = self._createIntInput(self.parameters.threshold)
        slider.valueChanged.connect(self.update_int)
        self.sliderThresh = slider  
        slider.setRange(0,100)
        slider.setTickInterval(10)
        subWidget = QWidget()
        layout = QHBoxLayout()
        subWidget.setLayout(layout)
        try:
            slider.setValue(int(100*self.parameters.threshold))
        except:
            pass
        btnThresh = self._createBoolBox()
        btnThresh.setChecked(self.parameters.doThreshold)
        btnThresh.stateChanged.connect(partial(self.set_value_checked_doThreshold,btnThresh))
        layout.addWidget(btnThresh)
        layout.addWidget(btnNew)
        self.generalLayout.addWidget(QLabel("Thresh."),self.current_line,0)
        self.generalLayout.addWidget(QLabel(f"{self.parameters.doThreshold}, {self.parameters.threshold}"),self.current_line,1)
        self.generalLayout.addWidget(subWidget,self.current_line,2)
        self.current_line +=1
    def _createParamList(self):
        text1 = QLabel("Parameter")
        text2 = QLabel("Values")
        text3 = QLabel("New Values")
        self.generalLayout.addWidget(text1,0,0)
        self.generalLayout.addWidget(text2,0,1)
        self.generalLayout.addWidget(text3,0,2)
        
        self._createSegmType()
        self._createErrorType()
        self._createSubImageSliders()
        self._createAcqValue()

        if self.parameters.SegmType in ["Canny Filled","Canny Contour"]:
            self._createMethodCannyType()
            self._createSigmaCanny()
            self._createCombCanny()
        elif self.parameters.SegmType == "ICM":
            self._createAlphaICM()
            self._createMaxiIterICM()
            self._createMaxiIterKMeanICM()
        elif self.parameters.SegmType == "k Mean":
            self._createMaxiIterKMeanICM
        elif self.parameters.SegmType in ["Filling (very slow)","Filling f (very slow)"]:
            self._createSeedSliders()
            self._createVerboseGraphFill()
            self._createStepsFilling()
            self._createMaxIterFilling()
            self._createFactorFillingRange()
            if self.parameters.SegmType == "Filling (very slow)":
                self._createFactorFFilling()
        elif self.parameters.SegmType == "Ellipsoid":
            self._createCenterEllipsoidSliders()
            self._createAxesEllipsoidSliders()
        if self.parameters.ErrorType != "None":
            self._createErrorValue()
        if self.parameters.ErrorType == "Linear Shift":
            self._createOrderShiftError()
            self._createDShiftError()
        self._createSaveBox()
        self._createStatsBox()
        self._createCurvesBox()
        self._createCoefficientsBox()
        self._createThresholdBox()

    def MethCombo_Changed(self):
        self.parameters.methodCanny = self.MethCombo.currentText()
    def SegmCombo_Changed(self):
        self.parameters.SegmType = self.SegmCombo.currentText()
        self.refresh_app()
    def ErrorMethodCombo_Changed(self):
        self.parameters.ErrorType = self.ErrorCombo.currentText()
        self.refresh_app()
    def set_value_checked_doCoefficients(self,box:QCheckBox):
        self.parameters.doCoefficients = box.isChecked()
    def set_value_checked_doThreshold(self,box:QCheckBox):
        self.parameters.doThreshold = box.isChecked()
    def set_value_checked_doStats(self,box:QCheckBox):
        self.parameters.doStats = box.isChecked()
    def set_value_checked_SaveSegm(self,box:QCheckBox):
        self.parameters.SaveSegm = box.isChecked()
    def set_value_checked_VerboseGraphFill(self,box:QCheckBox):
        self.parameters.verbose_graph_fill = box.isChecked()
    def set_value_checked_doCurves(self,box:QCheckBox):
        self.parameters.doCurves = box.isChecked()
    def set_value_slider(self,slider:QSlider,lineedit:QLineEdit):
        lineedit.setText(str(slider.value()))
        try:
            self.update_seed()
        except: pass
        try: self.update_center_ellipsoid()
        except: pass
        try: self.update_axes_ellipsoid()
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
        try: self.update_seed()
        except: pass
        try: self.update_center_ellipsoid()
        except: pass
        try: self.update_axes_ellipsoid()
        except: pass
    def set_value_line_edit_noSlider(self,lineedit:QLineEdit):
        """
        Changes the value of the 
        """
        try:
            lineedit.setText(f"{int(lineedit.text())}")
        except:
            lineedit.setText("0")
        self.update_subImage()
    def update_center_ellipsoid(self):
        self.parameters.centerEllipsoid[0] = self.sliderAxialValueCenter.text()
        self.parameters.centerEllipsoid[1] = self.sliderCoronalValueCenter.text()
        self.parameters.centerEllipsoid[2] = self.sliderSagittalValueCenter.text()
    def update_axes_ellipsoid(self):
        self.parameters.axesEllipsoid[0] = self.sliderAxialValueAxes.text()
        self.parameters.axesEllipsoid[1] = self.sliderCoronalValueAxes.text()
        self.parameters.axesEllipsoid[2] = self.sliderSagittalValueAxes.text()
    def update_seed(self):
        self.parameters.seed[0] = self.sliderAxialValueSeed.text()
        self.parameters.seed[1] = self.sliderCoronalValueSeed.text()
        self.parameters.seed[2] = self.sliderSagittalValueSeed.text()
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
        except: pass
        try:
            self.parameters.alphaICM = self.sliderAlpha.value()/1000
        except: pass
        try:
            self.parameters.sigmaCanny = self.sliderSigma.value()/1000
        except: pass
        try:
            self.parameters.combinationCanny = self.sliderComb.value()
        except: pass
        try:
            self.parameters.max_iter_ICM = self.sliderMaxIter.value()
        except: pass
        try:
            self.parameters.max_iter_kmean_ICM = self.sliderMaxIterKmean.value()
        except: pass
        try:
            self.parameters.max_iter_fill = self.sliderMaxIterFilling.value()
        except: pass
        try:
            self.parameters.steps_filling = self.sliderStepsFilling.value()
        except: pass
        try:
            self.parameters.ErrorSegm = self.sliderErrorAcq.value()
        except: pass
        try:
            self.parameters.orderShift = self.sliderErrorOrderShift.value()
        except: pass
        try:
            self.parameters.distanceShift = self.sliderErrorDistanceShift.value()
        except: pass
        try:
            self.parameters.threshold = self.sliderThresh.value()/100
        except: pass
        try:
            self.parameters.factor_fill_f = self.sliderFactorF.value()/100
        except: pass
        try:
            self.parameters.factor_Fill_range[0] = float(self.FactorFRangeValueMin.text())
        except: pass
        try:
            self.parameters.factor_Fill_range[1] = float(self.FactorFRangeValueMax.text())
        except: pass
    def refresh_app(self):
        if self.generalLayout is not None:
            while self.generalLayout.count():
                item = self.generalLayout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        self.initialize_param_window()