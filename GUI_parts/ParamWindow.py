import numpy as np
import MyFunctions.Statistic_Functions as SF
from GUI_parts.GUIParam import GUIParameters
import os
from sys import platform
###
import numpy as np
###
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from functools import partial
from PyQt5.QtGui import QPixmap
###
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from scipy.stats import norm
from scipy.fft import fft
###

size_Image = 200
class ParamWindow(QMainWindow):
    """
    Class to open a parameter window to get user's inputs
    """
    def __init__(self,parameters:GUIParameters,parent=None):
        """Initializes the ParamWindow with the GUI Parameters"""
        super().__init__(parent)
        self.setMinimumSize(300, 850)
        self.tabs = QTabWidget()
        self.parameters = parameters
        self.setWindowTitle("Parameters")
        self.generalLayoutSegm = QGridLayout()
        self.generalLayoutDefor = QGridLayout()
        self.generalLayoutError = QGridLayout()
        self.generalLayoutBayesian = QGridLayout()
        self.generalLayoutNoise = QGridLayout()
        self.generalLayoutErase = QGridLayout()
        centralWidgetSegm = QWidget(self)
        centralWidgetDefor = QWidget(self)
        centralWidgetErrors = QWidget(self)
        centralWidgetBayesian = QWidget(self)
        centralWidgetNoise = QWidget(self)
        centralWidgetErase = QWidget(self)
        centralWidgetSegm.setLayout(self.generalLayoutSegm)
        centralWidgetDefor.setLayout(self.generalLayoutDefor)
        centralWidgetErrors.setLayout(self.generalLayoutError)
        centralWidgetBayesian.setLayout(self.generalLayoutBayesian)
        centralWidgetNoise.setLayout(self.generalLayoutNoise)
        centralWidgetErase.setLayout(self.generalLayoutErase)

        self.tabs.addTab(centralWidgetSegm,"Segm.")
        self.tabs.addTab(centralWidgetDefor,"Defor.")
        self.tabs.addTab(centralWidgetErrors,"Errors.")
        self.tabs.addTab(centralWidgetBayesian,"Bayesian.")
        self.tabs.addTab(centralWidgetNoise,"Noise")
        self.tabs.addTab(centralWidgetErase,"Erase")
        self.setCentralWidget(self.tabs)
        self.initialize_param_window()

    def initialize_param_window(self):
        """Start the creation of the param window for the widgets"""
        self.current_line_Segm = 2
        self.current_line_Defor = 2
        self.current_line_Error = 2
        self.current_line_Bayesian = 2
        self.current_line_Noise = 2
        self.current_line_Erase = 2
        self._createParamList()

    def _createSeedSliders(self):
        """Create the sliders and the line edits for the seed"""
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
        self.sliderSagittalValueSeed.setText(f"{self.parameters.seed[2]}")
        self.sliderCoronalValueSeed.setText(f"{self.parameters.seed[1]}")
        
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
        layout.addWidget(self.sliderSeedCoronal,2,1)
        layout.addWidget(self.sliderSeedSagittal,3,1)
        layout.addWidget(self.sliderAxialValueSeed,1,2)
        layout.addWidget(self.sliderCoronalValueSeed,2,2)
        layout.addWidget(self.sliderSagittalValueSeed,3,2)
        
        self.generalLayoutSegm.addWidget(QLabel("Seed"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.seed}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(seedWidget,self.current_line_Segm,2)
        self.current_line_Segm += 1

    def _createCenterEllipsoidSliders(self):
        """Creates the sliders and line edits for the center of the ellipsoid segmentation"""
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
        
        self.generalLayoutSegm.addWidget(QLabel("Center Ellips."),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.centerEllipsoid}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(seedWidget,self.current_line_Segm,2)
        self.current_line_Segm += 1

    def _createAxesEllipsoidSliders(self):
        """Creates the sliders and line edits for the axes of the ellipsoid segmentation"""
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
        
        self.generalLayoutSegm.addWidget(QLabel("Axes Ellips."),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.axesEllipsoid}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(seedWidget,self.current_line_Segm,2)
        self.current_line_Segm += 1


    def _createSubImageSliders(self):
        """Creates the line edits for the sub image"""
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

        self.generalLayoutSegm.addWidget(QLabel("SubImage"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.subImage}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(subImageWidget,self.current_line_Segm,2)
        self.current_line_Segm += 1
    def _createBoolBox(self):
        """Creates a CheckBox and returns it (for bool parameters)"""
        btn = QCheckBox()
        return btn
    def _createMethodCannyType(self):
        """Creates the Combo Box for the Distance method calculation for Canny"""
        self.MethCombo = QComboBox()
        self.MethCombo.addItem("TaxiCab")
        self.MethCombo.setCurrentText(self.parameters.methodCanny)
        self.MethCombo.activated[str].connect(self.MethCombo_Changed)
        self.generalLayoutSegm.addWidget(QLabel("Method Canny"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.methodCanny}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(self.MethCombo,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createSegmType(self):
        """Creates the Combo Box for the segmentation method"""
        self.SegmCombo = QComboBox()
        self.SegmCombo.addItem("None")
        self.SegmCombo.addItem("ICM")
        self.SegmCombo.addItem("FCM")
        self.SegmCombo.addItem("Canny Filled")
        self.SegmCombo.addItem("Canny Contour")
        self.SegmCombo.addItem("Ellipsoid")
        self.SegmCombo.addItem("Prism")
        self.SegmCombo.addItem("k Mean")
        self.SegmCombo.addItem("Threshold")
        self.SegmCombo.addItem("Filling (very slow)")
        self.SegmCombo.addItem("Filling f (very slow)")
        self.SegmCombo.setCurrentText(self.parameters.SegmType)
        self.SegmCombo.activated[str].connect(self.SegmCombo_Changed)
        self.generalLayoutSegm.addWidget(QLabel("Segm. Method"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.SegmType}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(self.SegmCombo,self.current_line_Segm,2)
        self.generalLayoutSegm.setRowStretch(self.current_line_Segm,1)
        self.current_line_Segm +=1
    def _createDeformationType(self):
        """Creates the Combo Box for the deformation type method"""
        self.DeformationCombo = QComboBox()
        self.DeformationCombo.addItem("None")
        self.DeformationCombo.addItem("Linear Shift")
        self.DeformationCombo.addItem("Rotation")
        self.DeformationCombo.addItem("Expansion")
        self.DeformationCombo.addItem("Reflection")
        self.DeformationCombo.addItem("Flip All")
        self.DeformationCombo.addItem("Switch Two")
        self.DeformationCombo.addItem("Complement")
        self.DeformationCombo.addItem("Union")
        self.DeformationCombo.addItem("Intersection")

        self.DeformationCombo.setCurrentText(self.parameters.deformationType)
        self.DeformationCombo.activated[str].connect(self.DeformationMethodCombo_Changed)

        self.generalLayoutDefor.addWidget(QLabel("Deformation Method"),self.current_line_Defor,0)
        self.generalLayoutDefor.addWidget(QLabel(f"{self.parameters.deformationType}"),self.current_line_Defor,1)
        self.generalLayoutDefor.addWidget(self.DeformationCombo,self.current_line_Defor,2)
        self.generalLayoutDefor.setRowStretch(self.current_line_Defor,1)
        self.current_line_Defor +=1
    def _createDeformationSeg(self):
        """Creates the slider and the line edit for the choice of segmentation for the deformations.\n 
        -1 will mean all"""
        btnNew,slider = self._createIntInput(self.parameters.deformationSegm)
        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(1)
        slider.setRange(-1,self.parameters._nbSeg-1)
        slider.setValue(self.parameters.deformationSegm)
        self.sliderDeforSeg = slider   

        self.generalLayoutDefor.addWidget(QLabel("Seg. Deform."),self.current_line_Defor,0)
        self.generalLayoutDefor.addWidget(QLabel(f"{self.parameters.deformationSegm}"),self.current_line_Defor,1)
        self.generalLayoutDefor.addWidget(btnNew,self.current_line_Defor,2)
        self.generalLayoutDefor.setRowStretch(self.current_line_Defor,1)
        self.current_line_Defor +=1

    def _createDShiftDeformation(self):
        """Creates the sliders and the line edits for the distance of the deformation."""
        btnNew1,slider1 = self._createIntInput(self.parameters.deformationDistanceShift[0])
        btnNew2,slider2 = self._createIntInput(self.parameters.deformationDistanceShift[1])
        btnNew3,slider3 = self._createIntInput(self.parameters.deformationDistanceShift[2])
        slider1.valueChanged.connect(self.update_int)
        slider2.valueChanged.connect(self.update_int)
        slider3.valueChanged.connect(self.update_int)
        slider1.setTickInterval(5)
        slider2.setTickInterval(5)
        slider3.setTickInterval(5)
        slider1.setRange(0,50)
        slider2.setRange(0,50)
        slider3.setRange(0,50)
        slider1.setValue(self.parameters.deformationDistanceShift[0])
        slider2.setValue(self.parameters.deformationDistanceShift[1])
        slider3.setValue(self.parameters.deformationDistanceShift[2])
        self.sliderDeformationDistanceShift1 = slider1   
        self.sliderDeformationDistanceShift2 = slider2   
        self.sliderDeformationDistanceShift3 = slider3   

        subImageWidget = QWidget()
        layout = QGridLayout()
        subImageWidget.setLayout(layout)

        layout.addWidget(btnNew1,0,0)
        layout.addWidget(btnNew2,1,0)
        layout.addWidget(btnNew3,2,0)

        self.generalLayoutDefor.addWidget(QLabel("Distance"),self.current_line_Defor,0)
        self.generalLayoutDefor.addWidget(QLabel(f"{self.parameters.deformationDistanceShift}"),self.current_line_Defor,1)
        self.generalLayoutDefor.addWidget(subImageWidget,self.current_line_Defor,2)
        self.generalLayoutDefor.setRowStretch(self.current_line_Defor,3)
        self.current_line_Defor +=1

    def _createAngleDeformation(self):
        """Creates the sliders and the line edits for the angles of the rotation deformation."""
        btnNew1,slider1 = self._createIntInput(self.parameters.deformationRotate[0])
        btnNew2,slider2 = self._createIntInput(self.parameters.deformationRotate[1])
        btnNew3,slider3 = self._createIntInput(self.parameters.deformationRotate[2])
        slider1.valueChanged.connect(self.update_int)
        slider2.valueChanged.connect(self.update_int)
        slider3.valueChanged.connect(self.update_int)
        slider1.setTickInterval(90)
        slider2.setTickInterval(90)
        slider3.setTickInterval(90)
        slider1.setRange(0,360)
        slider2.setRange(0,360)
        slider3.setRange(0,360)
        slider1.setValue(self.parameters.deformationRotate[0])
        slider2.setValue(self.parameters.deformationRotate[1])
        slider3.setValue(self.parameters.deformationRotate[2])
        self.sliderDeformationRotate1 = slider1   
        self.sliderDeformationRotate2 = slider2   
        self.sliderDeformationRotate3 = slider3   

        subImageWidget = QWidget()
        layout = QGridLayout()
        subImageWidget.setLayout(layout)

        layout.addWidget(btnNew1,0,0)
        layout.addWidget(btnNew2,1,0)
        layout.addWidget(btnNew3,2,0)

        self.generalLayoutDefor.addWidget(QLabel("Angle (degrees)"),self.current_line_Defor,0)
        self.generalLayoutDefor.addWidget(QLabel(f"{self.parameters.deformationRotate}"),self.current_line_Defor,1)
        self.generalLayoutDefor.addWidget(subImageWidget,self.current_line_Defor,2)
        self.generalLayoutDefor.setRowStretch(self.current_line_Defor,3)
        self.current_line_Defor +=1

    def _createFactorDeformation(self):
        """Creates the sliders and the line edits for the angles of the rotation deformation."""
        btnNew1,slider1 = self._createIntInput(self.parameters.deformationExpansion[0])
        btnNew2,slider2 = self._createIntInput(self.parameters.deformationExpansion[1])
        btnNew3,slider3 = self._createIntInput(self.parameters.deformationExpansion[2])
        slider1.valueChanged.connect(self.update_int)
        slider2.valueChanged.connect(self.update_int)
        slider3.valueChanged.connect(self.update_int)
        slider1.setTickInterval(100)
        slider2.setTickInterval(100)
        slider3.setTickInterval(100)
        slider1.setRange(0,1000)
        slider2.setRange(0,1000)
        slider3.setRange(0,1000)
        slider1.setValue(int(self.parameters.deformationExpansion[0]*100))
        slider2.setValue(int(self.parameters.deformationExpansion[1]*100))
        slider3.setValue(int(self.parameters.deformationExpansion[2]*100))
        self.sliderDeformationExpansion1 = slider1   
        self.sliderDeformationExpansion2 = slider2   
        self.sliderDeformationExpansion3 = slider3   

        subImageWidget = QWidget()
        layout = QGridLayout()
        subImageWidget.setLayout(layout)

        layout.addWidget(btnNew1,0,0)
        layout.addWidget(btnNew2,1,0)
        layout.addWidget(btnNew3,2,0)

        self.generalLayoutDefor.addWidget(QLabel("Factor"),self.current_line_Defor,0)
        self.generalLayoutDefor.addWidget(QLabel(f"{self.parameters.deformationExpansion}"),self.current_line_Defor,1)
        self.generalLayoutDefor.addWidget(subImageWidget,self.current_line_Defor,2)
        self.generalLayoutDefor.setRowStretch(self.current_line_Defor,3)
        self.current_line_Defor +=1       

    def _createAxisReflectionDeformation(self):
        """Create the slider for the axis of reflection"""
        btnNew,slider = self._createIntInput(self.parameters.deformationReflectionAxis)
        self.sliderDeformationAxisReflection = slider
        slider.valueChanged.connect(self.update_int)
        slider.setRange(0,2)
        slider.setValue(self.parameters.deformationReflectionAxis)


        self.generalLayoutDefor.addWidget(QLabel("Ax. Refl."),self.current_line_Defor,0)
        self.generalLayoutDefor.addWidget(QLabel(f"{self.parameters.deformationReflectionAxis}"),self.current_line_Defor,1)
        self.generalLayoutDefor.addWidget(btnNew,self.current_line_Defor,2)
        self.generalLayoutDefor.setRowStretch(self.current_line_Defor,1)
        self.current_line_Defor +=1   
    def _createAxesSwitchDeformation(self):
        """Create the slider for the axes to switch"""
        btnNew,slider = self._createIntInput(self.parameters.switchAxes[0])
        self.sliderDeformationAxesSwitch1 = slider
        slider.valueChanged.connect(self.update_int)
        slider.setRange(1,3)
        slider.setValue(self.parameters.switchAxes[0])
        self.generalLayoutDefor.addWidget(QLabel("Switch Axis 1"),self.current_line_Defor,0)
        self.generalLayoutDefor.addWidget(QLabel(f"{self.parameters.switchAxes[0]}"),self.current_line_Defor,1)
        self.generalLayoutDefor.addWidget(btnNew,self.current_line_Defor,2)
        self.generalLayoutDefor.setRowStretch(self.current_line_Defor,1)
        self.current_line_Defor +=1  
        btnNew,slider = self._createIntInput(self.parameters.switchAxes[1])
        self.sliderDeformationAxesSwitch2 = slider
        slider.valueChanged.connect(self.update_int)
        slider.setRange(1,3)
        slider.setValue(self.parameters.switchAxes[1])
        self.generalLayoutDefor.addWidget(QLabel("Switch Axis 2"),self.current_line_Defor,0)
        self.generalLayoutDefor.addWidget(QLabel(f"{self.parameters.switchAxes[1]}"),self.current_line_Defor,1)
        self.generalLayoutDefor.addWidget(btnNew,self.current_line_Defor,2)
        self.generalLayoutDefor.setRowStretch(self.current_line_Defor,1)
        self.current_line_Defor +=1  
        
    def _createAxisFlipDeformation(self):
        """Create the slider for the axis to flip"""
        btnNew,slider = self._createIntInput(self.parameters.flipAxis)
        self.sliderDeformationAxisFlip = slider
        slider.valueChanged.connect(self.update_int)
        slider.setRange(1,3)
        slider.setValue(self.parameters.flipAxis)
        self.generalLayoutDefor.addWidget(QLabel("Flip Axis"),self.current_line_Defor,0)
        self.generalLayoutDefor.addWidget(QLabel(f"{self.parameters.flipAxis}"),self.current_line_Defor,1)
        self.generalLayoutDefor.addWidget(btnNew,self.current_line_Defor,2)
        self.generalLayoutDefor.setRowStretch(self.current_line_Defor,1)
        self.current_line_Defor +=1  
    def _createDeleteAfterDeformation(self):
        """Creates the CheckBox to Delete the original segmentations after having done a deformation"""
        btnNew = self._createBoolBox()
        btnNew.setChecked(self.parameters.deleteAfterDeformation)
        btnNew.stateChanged.connect(partial(self.set_value_checked_DeleteAfterDeformation,btnNew))
        btnNew.setToolTip("Deletes the original segmentations after the deformations are computed")
        self.generalLayoutDefor.addWidget(QLabel("Delete After"),self.current_line_Defor,0)
        self.generalLayoutDefor.addWidget(QLabel(f"{self.parameters.deleteAfterDeformation}"),self.current_line_Defor,1)
        self.generalLayoutDefor.addWidget(btnNew,self.current_line_Defor,2)
        self.current_line_Defor +=1
     
    def _createErrorType(self):
        """Creates the Combo Box for the error type method"""
        self.ErrorCombo = QComboBox()
        self.ErrorCombo.addItem("None")
        self.ErrorCombo.addItem("Linear Shift")
        self.ErrorCombo.addItem("Rotation")
        self.ErrorCombo.addItem("Expansion")
        self.ErrorCombo.addItem("Reflection")
        self.ErrorCombo.addItem("FCM")

        self.ErrorCombo.setCurrentText(self.parameters.ErrorType)
        self.ErrorCombo.activated[str].connect(self.ErrorMethodCombo_Changed)
        self.generalLayoutError.addWidget(QLabel("Error Method"),self.current_line_Error,0)
        self.generalLayoutError.addWidget(QLabel(f"{self.parameters.ErrorType}"),self.current_line_Error,1)
        self.generalLayoutError.addWidget(self.ErrorCombo,self.current_line_Error,2)
        self.current_line_Error +=1
    def _createBayesianType(self):
        """Creates the Combo Box for the bayesian analysis"""
        self.BayesianCombo = QComboBox()
        self.BayesianCombo.addItem("None")
        self.BayesianCombo.addItem("Dynesty")
        self.BayesianCombo.addItem("scipy")

        self.ModelCombo = QComboBox()
        self.ModelCombo.addItem("2_Comp_A1")
        self.ModelCombo.addItem("2_Comp_A2")
        self.ModelCombo.addItem("2_Comp_A2_Pause")

        self.CurvesCombo = QComboBox()
        self.CurvesCombo.addItem("Average")
        self.CurvesCombo.addItem("Errors")

        self.BayesianCombo.setCurrentText(self.parameters.BayesianType)
        self.BayesianCombo.activated[str].connect(self.BayesianMethodCombo_Changed)
        self.ModelCombo.setCurrentText(self.parameters.ModelBayesian)
        self.ModelCombo.activated[str].connect(self.ModelBayesianMethodCombo_Changed)
        self.CurvesCombo.setCurrentText(self.parameters.CurveTypeBayesian)
        self.CurvesCombo.activated[str].connect(self.CurvesBayesianMethodCombo_Changed)

        self.generalLayoutBayesian.addWidget(QLabel("Bayesian Method"),self.current_line_Bayesian,0)
        self.generalLayoutBayesian.addWidget(QLabel(f"{self.parameters.BayesianType}"),self.current_line_Bayesian,1)
        self.generalLayoutBayesian.addWidget(self.BayesianCombo,self.current_line_Bayesian,2)
        self.current_line_Bayesian +=1
        self.generalLayoutBayesian.addWidget(QLabel("Bayesian Model"),self.current_line_Bayesian,0)
        self.generalLayoutBayesian.addWidget(QLabel(f"{self.parameters.ModelBayesian}"),self.current_line_Bayesian,1)
        self.generalLayoutBayesian.addWidget(self.ModelCombo,self.current_line_Bayesian,2)
        self.current_line_Bayesian +=1
        self.generalLayoutBayesian.addWidget(QLabel("Curves Used"),self.current_line_Bayesian,0)
        self.generalLayoutBayesian.addWidget(QLabel(f"{self.parameters.CurveTypeBayesian}"),self.current_line_Bayesian,1)
        self.generalLayoutBayesian.addWidget(self.CurvesCombo,self.current_line_Bayesian,2)
        self.current_line_Bayesian +=1
    def _createNoiseGraphs(self):
        """Creates the Graphs for the Noise Functions"""
        self.pdfImage = MplCanvas(self, width=1, height=1, dpi=75)
        self.pdfImageF = MplCanvas(self, width=1, height=1, dpi=75)
        self.cdfImage = MplCanvas(self, width=1, height=1, dpi=75)
        self.cdfImageF = MplCanvas(self, width=1, height=1, dpi=75)

        self.pdfImage.setMinimumSize(size_Image,size_Image)
        self.cdfImage.setMinimumSize(size_Image,size_Image)

        self.pdfImage.axes.grid()
        self.pdfImageF.axes.grid()
        self.cdfImage.axes.grid()
        self.cdfImageF.axes.grid()
        self.pdfImage.axes.set_title("pdf")
        self.pdfImageF.axes.set_title("Fourier pdf")
        self.cdfImage.axes.set_title("cdf")
        self.cdfImageF.axes.set_title("Fourier cdf")

        if self.parameters.NoiseType == "Rayleigh":
            y = np.random.rand(int(1e6))
            noise = SF.rayleigh_noise_pdf(y, a=self.parameters.NoiseARayleigh, b=self.parameters.NoiseBRayleigh, type= "icdf")
            mean = self.parameters.NoiseARayleigh + np.sqrt(np.pi * self.parameters.NoiseBRayleigh/4)
            std = self.parameters.NoiseBRayleigh * (4 - np.pi)/4
            x = np.linspace(self.parameters.NoiseARayleigh,mean+5*std,1000)
            length = [self.parameters.NoiseARayleigh , mean+5*std]
            ypdf = SF.rayleigh_noise_pdf(x, a= self.parameters.NoiseARayleigh, b= self.parameters.NoiseBRayleigh, type= "pdf")
            ycdf = SF.rayleigh_noise_pdf(x, a= self.parameters.NoiseARayleigh, b= self.parameters.NoiseBRayleigh, type= "cdf")
        elif self.parameters.NoiseType == "Gaussian":
            x = np.arange(self.parameters.NoiseMu - 4 * self.parameters.NoiseSigma,self.parameters.NoiseMu + 4 * self.parameters.NoiseSigma,0.001)
            x = np.linspace(self.parameters.NoiseMu - 4 * self.parameters.NoiseSigma,self.parameters.NoiseMu + 4 * self.parameters.NoiseSigma,1000)
            ypdf = 1/(self.parameters.NoiseSigma*np.sqrt(4*np.pi))*np.exp(-(x-self.parameters.NoiseMu)**2/(2*self.parameters.NoiseSigma**2))
            ycdf = norm.cdf(x,loc = self.parameters.NoiseMu, scale=self.parameters.NoiseSigma)
        elif self.parameters.NoiseType == "Poisson":
            pass
        elif self.parameters.NoiseType == "Erlang (Gamma)":
            y = np.random.rand(int(1e6))
            noise = SF.get_pdf_from_uniform(y,SF.Erlang_noise_pdf,[self.parameters.NoiseAErlang,self.parameters.NoiseBErlang])
            x = np.linspace(-1, 5*self.parameters.NoiseBErlang/self.parameters.NoiseAErlang, 1000)
            ypdf = SF.Erlang_noise_pdf(x, a= self.parameters.NoiseAErlang, b= self.parameters.NoiseBErlang, type= "pdf")
            ycdf = SF.Erlang_noise_pdf(x, a= self.parameters.NoiseAErlang, b= self.parameters.NoiseBErlang, type= "cdf")
            length = [0, 5*self.parameters.NoiseBErlang/self.parameters.NoiseAErlang]
        elif self.parameters.NoiseType == "Exponential":
            y = np.random.rand(int(1e6))
            noise = SF.exponential_noise_pdf(y, a=self.parameters.NoiseExponential, type= "icdf")
            x = np.linspace(-1/self.parameters.NoiseExponential, 5/self.parameters.NoiseExponential, 1000)
            ypdf = SF.exponential_noise_pdf(x, a= self.parameters.NoiseExponential, type= "pdf")
            ycdf = SF.exponential_noise_pdf(x, a= self.parameters.NoiseExponential, type= "cdf")
            length = [0/self.parameters.NoiseExponential, 5/self.parameters.NoiseExponential]
        elif self.parameters.NoiseType == "Uniform":
            y = np.random.rand(int(1e6))
            noise = SF.uniform_noise_pdf(y, a=self.parameters.NoiseAUniform, b=self.parameters.NoiseBUniform, type= "icdf")
            x = np.linspace(-1 + self.parameters.NoiseAUniform, self.parameters.NoiseBUniform + 1, 1000)
            ypdf = SF.uniform_noise_pdf(x, a= self.parameters.NoiseAUniform, b= self.parameters.NoiseBUniform, type= "pdf")
            ycdf = SF.uniform_noise_pdf(x, a= self.parameters.NoiseAUniform, b= self.parameters.NoiseBUniform, type= "cdf")
            length = [self.parameters.NoiseAUniform - 0.5,self.parameters.NoiseBUniform + 0.5]
        try:
            self.pdfImage.axes.plot(x,ypdf,label='pdf')
        except: pass
        try:
            self.cdfImage.axes.plot(x,ycdf)
        except:pass
        try:
            self.pdfImage.axes.hist(noise,100,range=length,density=True,label="hist")
            self.pdfImage.axes.legend()
        except: pass
        
        try:
            size = x.shape[0]
            fx = (np.fft.fftshift(np.fft.fftfreq(size, x[1]-x[0])))
            self.pdfImageF.axes.plot(fx[int(size/2-50):int(size/2+50)],np.abs(np.fft.fftshift(np.fft.fft(ypdf)))[int(size/2-50):int(size/2+50)]/np.sqrt(x.shape[0]/2),label='pdf')
            self.cdfImageF.axes.plot(fx[int(size/2-50):int(size/2+50)],np.abs(np.fft.fftshift(np.fft.fft(ycdf)))[int(size/2-50):int(size/2+50)]/np.sqrt(x.shape[0]/2),label='pdf')
        except: 
            pass
        self.generalLayoutNoise.addWidget(QLabel("Dist."),self.current_line_Noise,0)
        self.generalLayoutNoise.addWidget(self.pdfImage,self.current_line_Noise,1)
        self.generalLayoutNoise.addWidget(self.cdfImage,self.current_line_Noise,2)
        self.generalLayoutNoise.setRowStretch(self.current_line_Noise,5)
        self.current_line_Noise +=1
        self.generalLayoutNoise.addWidget(QLabel("Fourier"),self.current_line_Noise,0)
        self.generalLayoutNoise.addWidget(self.pdfImageF,self.current_line_Noise,1)
        self.generalLayoutNoise.addWidget(self.cdfImageF,self.current_line_Noise,2)
        self.generalLayoutNoise.setRowStretch(self.current_line_Noise,5)
        self.current_line_Noise +=1
    def _createNoiseType(self):
        """Creates the Combo Box for the noise"""
        self.NoiseCombo = QComboBox()
        self.NoiseCombo.addItem("None")
        self.NoiseCombo.addItem("Gaussian")
        self.NoiseCombo.addItem("Poisson")
        self.NoiseCombo.addItem("Rayleigh")
        self.NoiseCombo.addItem("Erlang (Gamma)")
        self.NoiseCombo.addItem("Exponential")
        self.NoiseCombo.addItem("Uniform")

        self.NoiseCombo.setCurrentText(self.parameters.NoiseType)
        self.NoiseCombo.activated[str].connect(self.NoiseMethodCombo_Changed)

        self.generalLayoutNoise.addWidget(QLabel("Noise Type"),self.current_line_Noise,0)
        self.generalLayoutNoise.addWidget(QLabel(f"{self.parameters.NoiseType}"),self.current_line_Noise,1)
        self.generalLayoutNoise.addWidget(self.NoiseCombo,self.current_line_Noise,2)
        self.generalLayoutNoise.setRowStretch(self.current_line_Noise,1)
        self.current_line_Noise +=1
    def _createNoiseFormulaeDisplay(self):
        """Shows the formula of the pdf, the mean (and its value) and the std (and its value)"""
        basedir = os.path.dirname(__file__)
        if self.parameters.NoiseType == "Gaussian":
            pdf = os.path.join(basedir,"Images", "Gaussian_pdf.png")
            mu_f = os.path.join(basedir,"Images", "Gaussian_mu.png")
            sigma_f = os.path.join(basedir,"Images", "Gaussian_sigma.png")   
            mu = self.parameters.NoiseMu
            sigma = self.parameters.NoiseSigma
        elif self.parameters.NoiseType == "Uniform":
            pdf = os.path.join(basedir,"Images", "Uniform_pdf.png")
            mu_f = os.path.join(basedir,"Images", "Uniform_mu.png")
            sigma_f = os.path.join(basedir,"Images", "Uniform_sigma.png")   
            mu = SF.uniform_noise_pdf(a=self.parameters.NoiseAUniform,b = self.parameters.NoiseBUniform,type="mu")
            sigma = SF.uniform_noise_pdf(a=self.parameters.NoiseAUniform,b = self.parameters.NoiseBUniform,type="sigma")
        elif self.parameters.NoiseType == "Erlang (Gamma)":
            pdf = os.path.join(basedir,"Images", "Erlang_pdf.png")
            mu_f = os.path.join(basedir,"Images", "Erlang_mu.png")
            sigma_f = os.path.join(basedir,"Images", "Erlang_sigma.png")   
            mu = SF.Erlang_noise_pdf(a=self.parameters.NoiseAErlang,b = self.parameters.NoiseBErlang,type="mu")
            sigma = SF.Erlang_noise_pdf(a=self.parameters.NoiseAErlang,b = self.parameters.NoiseBErlang,type="sigma")
        elif self.parameters.NoiseType == "Exponential":
            pdf = os.path.join(basedir,"Images", "Exponential_pdf.png")
            mu_f = os.path.join(basedir,"Images", "Exponential_mu.png")
            sigma_f = os.path.join(basedir,"Images", "Exponential_sigma.png")   
            mu = SF.exponential_noise_pdf(a=self.parameters.NoiseExponential,type="mu")
            sigma = SF.exponential_noise_pdf(a=self.parameters.NoiseExponential,type="sigma")
        elif self.parameters.NoiseType == "Rayleigh":
            pdf = os.path.join(basedir,"Images", "Rayleigh_pdf.png")
            mu_f = os.path.join(basedir,"Images", "Rayleigh_mu.png")
            sigma_f = os.path.join(basedir,"Images", "Rayleigh_sigma.png")        
            mu = SF.rayleigh_noise_pdf(a=self.parameters.NoiseARayleigh,b = self.parameters.NoiseBRayleigh,type="mu")
            sigma = SF.rayleigh_noise_pdf(a=self.parameters.NoiseARayleigh,b = self.parameters.NoiseBRayleigh,type="sigma")
        else:
            pdf = os.path.join(basedir,"Images", "None.png")
            mu_f = os.path.join(basedir,"Images", "None.png")
            sigma_f = os.path.join(basedir,"Images", "None.png")  
            mu = 0
            sigma = 0
        im_pdf = QLabel()
        im_mu = QLabel()
        im_sigma = QLabel()
        try:
            pixmap_pdf = QPixmap(pdf)
            im_pdf.resize(int(self.width()/3), int(self.width()/12))
            im_pdf.setPixmap(pixmap_pdf.scaled(im_pdf.size(), Qt.IgnoreAspectRatio))
        except: pass
        try:
            pixmap_mu = QPixmap(mu_f)
            im_mu.resize(int(self.width()/3), int(self.width()/12))
            im_mu.setPixmap(pixmap_mu.scaled(im_mu.size(), Qt.IgnoreAspectRatio))
        except: pass
        try:
            pixmap_sigma = QPixmap(sigma_f)
            im_sigma.resize(int(self.width()/3), int(self.width()/12))
            im_sigma.setPixmap(pixmap_sigma.scaled(im_sigma.size(), Qt.IgnoreAspectRatio))
        except: pass

        self.generalLayoutNoise.addWidget(QLabel(r"Noise PDF"),self.current_line_Noise,0)
        self.generalLayoutNoise.addWidget(im_pdf,self.current_line_Noise,1)
        self.generalLayoutNoise.setRowStretch(self.current_line_Noise,1)
        self.current_line_Noise +=1
        self.generalLayoutNoise.addWidget(QLabel(r"Noise μ"),self.current_line_Noise,0)
        self.generalLayoutNoise.addWidget(im_mu,self.current_line_Noise,1)
        self.generalLayoutNoise.addWidget(QLabel(f"{mu:.2f}"),self.current_line_Noise,2)
        self.generalLayoutNoise.setRowStretch(self.current_line_Noise,1)
        self.current_line_Noise +=1
        self.generalLayoutNoise.addWidget(QLabel(r"Noise σ"),self.current_line_Noise,0)
        self.generalLayoutNoise.addWidget(im_sigma,self.current_line_Noise,1)
        self.generalLayoutNoise.addWidget(QLabel(f"{sigma:.2f}"),self.current_line_Noise,2)
        self.generalLayoutNoise.setRowStretch(self.current_line_Noise,1)
        self.current_line_Noise +=1


    def _createNoiseMu(self):
        """Creates the QLineEdits for Mu for the Noise"""
        self.btnMuNoise = self._createFloatInput(self.parameters.NoiseMu)

        self.btnMuNoise.editingFinished.connect(self.update_QLines)

        self.generalLayoutNoise.addWidget(QLabel("Noise Mu"),self.current_line_Noise,0)
        self.generalLayoutNoise.addWidget(QLabel(f"{self.parameters.NoiseMu}"),self.current_line_Noise,1)
        self.generalLayoutNoise.addWidget(self.btnMuNoise,self.current_line_Noise,2)
        self.generalLayoutNoise.setRowStretch(self.current_line_Noise,1)
        self.current_line_Noise +=1
    def _createNoiseSigma(self):
        """Creates the QLineEdits for Sigma for the Noise"""
        self.btnSigmaNoise = self._createFloatInput(self.parameters.NoiseSigma)
        self.btnSigmaNoise.editingFinished.connect(self.update_QLines)

        self.generalLayoutNoise.addWidget(QLabel("Noise Sigma"),self.current_line_Noise,0)
        self.generalLayoutNoise.addWidget(QLabel(f"{self.parameters.NoiseSigma}"),self.current_line_Noise,1)
        self.generalLayoutNoise.addWidget(self.btnSigmaNoise,self.current_line_Noise,2)
        self.generalLayoutNoise.setRowStretch(self.current_line_Noise,1)
        self.current_line_Noise +=1
    def _createNoiseRayleighA(self):
        """Creates the QLineEdits for a for the Rayleigh Noise"""
        self.btnNoiseRayleighA = self._createFloatInput(self.parameters.NoiseARayleigh)
        self.btnNoiseRayleighA.editingFinished.connect(self.update_QLines)

        self.generalLayoutNoise.addWidget(QLabel("Rayleigh a"),self.current_line_Noise,0)
        self.generalLayoutNoise.addWidget(QLabel(f"{self.parameters.NoiseARayleigh}"),self.current_line_Noise,1)
        self.generalLayoutNoise.addWidget(self.btnNoiseRayleighA,self.current_line_Noise,2)
        self.generalLayoutNoise.setRowStretch(self.current_line_Noise,1)
        self.current_line_Noise +=1
    def _createNoiseRayleighB(self):
        """Creates the QLineEdits for b for the Rayleigh Noise"""
        self.btnNoiseRayleighB = self._createFloatInput(self.parameters.NoiseBRayleigh)
        self.btnNoiseRayleighB.editingFinished.connect(self.update_QLines)

        self.generalLayoutNoise.addWidget(QLabel("Rayleigh b"),self.current_line_Noise,0)
        self.generalLayoutNoise.addWidget(QLabel(f"{self.parameters.NoiseBRayleigh}"),self.current_line_Noise,1)
        self.generalLayoutNoise.addWidget(self.btnNoiseRayleighB,self.current_line_Noise,2)
        self.generalLayoutNoise.setRowStretch(self.current_line_Noise,1)
        self.current_line_Noise +=1
    def _createNoiseErlangA(self):
        """Creates the QLineEdits for a for the Erlang Noise"""
        self.btnNoiseErlangA = self._createFloatInput(self.parameters.NoiseAErlang)
        self.btnNoiseErlangA.editingFinished.connect(self.update_QLines)

        self.generalLayoutNoise.addWidget(QLabel("Erlang a"),self.current_line_Noise,0)
        self.generalLayoutNoise.addWidget(QLabel(f"{self.parameters.NoiseAErlang}"),self.current_line_Noise,1)
        self.generalLayoutNoise.addWidget(self.btnNoiseErlangA,self.current_line_Noise,2)
        self.generalLayoutNoise.setRowStretch(self.current_line_Noise,1)
        self.current_line_Noise +=1
    def _createNoiseErlangB(self):
        """Creates the QLineEdits for b for the Erlang Noise"""
        self.btnNoiseErlangB = self._createFloatInput(self.parameters.NoiseBErlang)
        self.btnNoiseErlangB.editingFinished.connect(self.update_QLines)

        self.generalLayoutNoise.addWidget(QLabel("Erlang b"),self.current_line_Noise,0)
        self.generalLayoutNoise.addWidget(QLabel(f"{self.parameters.NoiseBErlang}"),self.current_line_Noise,1)
        self.generalLayoutNoise.addWidget(self.btnNoiseErlangB,self.current_line_Noise,2)
        self.generalLayoutNoise.setRowStretch(self.current_line_Noise,1)
    def _createNoiseUnifA(self):
        """Creates the QLineEdits for a for the Unif Noise"""
        self.btnNoiseUnifA = self._createFloatInput(self.parameters.NoiseAUniform)
        self.btnNoiseUnifA.editingFinished.connect(self.update_QLines)

        self.generalLayoutNoise.addWidget(QLabel("Unif a"),self.current_line_Noise,0)
        self.generalLayoutNoise.addWidget(QLabel(f"{self.parameters.NoiseAUniform}"),self.current_line_Noise,1)
        self.generalLayoutNoise.addWidget(self.btnNoiseUnifA,self.current_line_Noise,2)
        self.generalLayoutNoise.setRowStretch(self.current_line_Noise,1)
        self.current_line_Noise +=1
    def _createNoiseUnifB(self):
        """Creates the QLineEdits for b for the Unif Noise"""
        self.btnNoiseUnifB = self._createFloatInput(self.parameters.NoiseBUniform)
        self.btnNoiseUnifB.editingFinished.connect(self.update_QLines)

        self.generalLayoutNoise.addWidget(QLabel("Unif b"),self.current_line_Noise,0)
        self.generalLayoutNoise.addWidget(QLabel(f"{self.parameters.NoiseBUniform}"),self.current_line_Noise,1)
        self.generalLayoutNoise.addWidget(self.btnNoiseUnifB,self.current_line_Noise,2)
        self.generalLayoutNoise.setRowStretch(self.current_line_Noise,1)
    def _createNoiseExponential(self):
        """Creates the QLineEdits for the param for the Exponential Noise"""
        self.btnNoiseExponential = self._createFloatInput(self.parameters.NoiseExponential)
        self.btnNoiseExponential.editingFinished.connect(self.update_QLines)

        self.generalLayoutNoise.addWidget(QLabel("Exp"),self.current_line_Noise,0)
        self.generalLayoutNoise.addWidget(QLabel(f"{self.parameters.NoiseExponential}"),self.current_line_Noise,1)
        self.generalLayoutNoise.addWidget(self.btnNoiseExponential,self.current_line_Noise,2)
        self.generalLayoutNoise.setRowStretch(self.current_line_Noise,1)        
    def _createHeadersErase(self):
        """Creates the Values for the Erase Button"""
        self.EraseTypeChoice = QComboBox()
        self.EraseTypeChoice.addItem("None")
        self.EraseTypeChoice.addItem("Segmentation")
        self.EraseTypeChoice.addItem("Error")
        self.EraseTypeChoice.addItem("Bayesian")
        self.EraseTypeChoice.setCurrentText(self.parameters.EraseType)
        self.EraseTypeChoice.activated[str].connect(self.EraseChoiceComboChanged)

        SegmNumber = QLineEdit()
        SegmNumber.setText(str(self.parameters._nbSeg))
        SegmNumber.setFixedWidth(70)
        SegmNumber.setReadOnly(True)
        ErrorNumber = QLineEdit()
        ErrorNumber.setText(str(self.parameters._nbError))
        ErrorNumber.setFixedWidth(70)
        ErrorNumber.setReadOnly(True)
        BayesianNumber = QLineEdit()
        BayesianNumber.setText(str(self.parameters._nbBayesian))
        BayesianNumber.setFixedWidth(70)
        BayesianNumber.setReadOnly(True)

        btnNewSegm,sliderSegm = self._createIntInput(self.parameters.EraseSegm)
        btnNewError,sliderError = self._createIntInput(self.parameters.EraseError)
        btnNewBayesian,sliderBayesian = self._createIntInput(self.parameters.EraseBayesian)
        self.sliderEraseSegm = sliderSegm
        self.sliderEraseError = sliderError
        self.sliderEraseBayesian = sliderBayesian
        sliderSegm.valueChanged.connect(self.update_EraseValues)
        sliderSegm.setTickInterval(1)
        sliderSegm.setRange(-1,self.parameters._nbSeg-1)
        sliderSegm.setValue(self.parameters.EraseSegm)
        sliderError.valueChanged.connect(self.update_EraseValues)
        sliderError.setTickInterval(1)
        sliderError.setRange(-1,self.parameters._nbError-1)
        sliderError.setValue(self.parameters.EraseError)
        sliderBayesian.valueChanged.connect(self.update_EraseValues)
        sliderBayesian.setTickInterval(1)
        sliderBayesian.setRange(-1,self.parameters._nbBayesian-1)
        sliderBayesian.setValue(self.parameters.EraseBayesian)

        self.generalLayoutErase.addWidget(QLabel("Current Number of Segmentations"),self.current_line_Erase,0)
        self.generalLayoutErase.addWidget(SegmNumber,self.current_line_Erase,1)
        self.current_line_Erase += 1
        self.generalLayoutErase.addWidget(QLabel("Current Number of Errors"),self.current_line_Erase,0)
        self.generalLayoutErase.addWidget(ErrorNumber,self.current_line_Erase,1)
        self.current_line_Erase += 1
        self.generalLayoutErase.addWidget(QLabel("Current Number of Bayesian Analyses"),self.current_line_Erase,0)
        self.generalLayoutErase.addWidget(BayesianNumber,self.current_line_Erase,1)
        self.current_line_Erase += 1

        self.generalLayoutErase.addWidget(QLabel("Type"),self.current_line_Erase,0)
        self.generalLayoutErase.addWidget(QLabel(self.parameters.EraseType),self.current_line_Erase,1)
        self.generalLayoutErase.addWidget(self.EraseTypeChoice,self.current_line_Erase,2)
        self.current_line_Erase += 1

        self.generalLayoutErase.addWidget(QLabel("Segmentation"),self.current_line_Erase,0)
        self.generalLayoutErase.addWidget(QLabel(str(self.parameters.EraseSegm)),self.current_line_Erase,1)
        self.generalLayoutErase.addWidget(btnNewSegm,self.current_line_Erase,2)
        self.current_line_Erase += 1

        self.generalLayoutErase.addWidget(QLabel("Error"),self.current_line_Erase,0)
        self.generalLayoutErase.addWidget(QLabel(str(self.parameters.EraseError)),self.current_line_Erase,1)
        self.generalLayoutErase.addWidget(btnNewError,self.current_line_Erase,2)
        self.current_line_Erase += 1

        self.generalLayoutErase.addWidget(QLabel("Bayesian"),self.current_line_Erase,0)
        self.generalLayoutErase.addWidget(QLabel(str(self.parameters.EraseBayesian)),self.current_line_Erase,1)
        self.generalLayoutErase.addWidget(btnNewBayesian,self.current_line_Erase,2)
        self.current_line_Erase += 1
    def _createEraseButton(self):
        """Creates the dangerous erase button"""
        self.EraseButton = QPushButton("Erase")
        self.EraseButton.setToolTip("Danger! Will erase a calculated aspect as specified")
        self.EraseButton.clicked.connect(self.EraseButtonClicked)

        self.generalLayoutErase.addWidget(self.EraseButton,self.current_line_Erase,1)
        self.current_line_Erase += 1

    def _createExitButtons(self):
        """Creates exit buttons for the param window"""
        self.exitSegm = QPushButton("Close")
        self.exitNoise = QPushButton("Close")
        self.exitError = QPushButton("Close")
        self.exitBayesian = QPushButton("Close")
        self.exitDeform = QPushButton("Close")
        self.exitErase = QPushButton("Close")

        self.exitSegm.clicked.connect(self.close)
        self.exitNoise.clicked.connect(self.close)
        self.exitError.clicked.connect(self.close)
        self.exitBayesian.clicked.connect(self.close)
        self.exitDeform.clicked.connect(self.close)
        self.exitErase.clicked.connect(self.close)
        self.generalLayoutSegm.addWidget(self.exitSegm,self.current_line_Segm,3)  
        self.generalLayoutNoise.addWidget(self.exitNoise,self.current_line_Noise,3)  
        self.generalLayoutError.addWidget(self.exitError,self.current_line_Error,3)  
        self.generalLayoutBayesian.addWidget(self.exitBayesian,self.current_line_Bayesian,3)  
        self.generalLayoutDefor.addWidget(self.exitDeform,self.current_line_Defor,3)  
        self.generalLayoutErase.addWidget(self.exitErase,self.current_line_Erase,3)  
        self.current_line_Segm += 1
        self.current_line_Noise += 1
        self.current_line_Error += 1
        self.current_line_Bayesian += 1
        self.current_line_Defor += 1
        self.current_line_Erase += 1
    def _createThreshBaySliders(self):
        btnNew,slider = self._createIntInput(self.parameters.Bayesian_thresh_perc)
        btnNew2,slider2 = self._createIntInput(self.parameters.Bayesian_thresh_value)

        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(10)
        slider.setRange(0,100)
        slider.setValue(int(100*self.parameters.Bayesian_thresh_perc))

        slider2.valueChanged.connect(self.update_int)
        slider2.setTickInterval(10)
        slider2.setRange(0,100)
        slider2.setValue(int(100*self.parameters.Bayesian_thresh_value))

        self.sliderBayesianThreshPerc = slider
        self.sliderBayesianThreshValue = slider2

        self.generalLayoutBayesian.addWidget(QLabel("Bayesian Thresh Perc"),self.current_line_Bayesian,0)
        self.generalLayoutBayesian.addWidget(QLabel(f"{self.parameters.Bayesian_thresh_perc}"),self.current_line_Bayesian,1)
        self.generalLayoutBayesian.addWidget(btnNew,self.current_line_Bayesian,2)
        self.current_line_Bayesian +=1
        self.generalLayoutBayesian.addWidget(QLabel("Bayesian Thresh Value"),self.current_line_Bayesian,0)
        self.generalLayoutBayesian.addWidget(QLabel(f"{self.parameters.Bayesian_thresh_value}"),self.current_line_Bayesian,1)
        self.generalLayoutBayesian.addWidget(btnNew2,self.current_line_Bayesian,2)
        self.current_line_Bayesian +=1
    def _createFactorFFilling(self):
        """Creates the slider and the line edit for the factor f (for filling)"""
        btnNew,slider = self._createIntInput(self.parameters.factor_fill_f)
        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(100)
        slider.setRange(0,1000)
        slider.setValue(int(100*self.parameters.factor_fill_f))

        self.sliderFactorF = slider   
        self.generalLayoutSegm.addWidget(QLabel("Factor Filling"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.factor_fill_f}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createFactorFillingRange(self):
        """Creates the slider and the line edit for the factor range (for filling)"""
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

        self.generalLayoutSegm.addWidget(QLabel("Factor Filling Range"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.factor_Fill_range}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(RangeWidget,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createThresholdLimitFilling(self):
        """Creates a line edit for the max factor of filling"""
        sizeText = 30
        self.ThresholdFillingLimit = QLineEdit()
        self.ThresholdFillingLimit.setFixedWidth(sizeText)
        self.ThresholdFillingLimit.setText(f"{self.parameters.threshold_fill}")
        self.ThresholdFillingLimit.editingFinished.connect(self.update_int)


        self.generalLayoutSegm.addWidget(QLabel("Threshold Limit"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.threshold_fill}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(self.ThresholdFillingLimit,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createIntInput(self,initvalue:float):
        """Creates a subwidet with a QLineEdit and a QSlider linked in their value.\n
        Returns the subWidget and the slider"""
        initvalue = int(initvalue)
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
    def _createFloatInput(self,initvalue:float):
        """Creates a basic QLineEdit and returns it"""
        number = QLineEdit()
        number.setText(str(initvalue))
        number.setMaximumWidth(75)
        return number
    def _createAcqValue(self):
        """Creates the slider and the line edit for the choice of acquisition.\n 
        -1 will mean all"""
        btnNew,slider = self._createIntInput(self.parameters.SegmAcq)
        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(1)
        slider.setRange(-1,self.parameters._size[0]-1)
        slider.setValue(self.parameters.SegmAcq)
        self.sliderSegmAcq = slider   

        self.generalLayoutSegm.addWidget(QLabel("Acq. Segm."),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.SegmAcq}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createErrorValue(self):
        """Creates the slider and the line edit for the choice of segmentation for the error computation.\n 
        -1 will mean all"""
        btnNew,slider = self._createIntInput(self.parameters.ErrorSegm)
        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(1)
        slider.setRange(-1,self.parameters._nbSeg-1)
        slider.setValue(self.parameters.ErrorSegm)
        self.sliderErrorAcq = slider   

        self.generalLayoutError.addWidget(QLabel("Seg. Error"),self.current_line_Error,0)
        self.generalLayoutError.addWidget(QLabel(f"{self.parameters.ErrorSegm}"),self.current_line_Error,1)
        self.generalLayoutError.addWidget(btnNew,self.current_line_Error,2)
        self.current_line_Error +=1

    def _createBayesianValue(self):
        """Creates the slider and the line edit for the choice of segmentation for the error computation.\n 
        -1 will mean all"""
        btnNew,slider = self._createIntInput(self.parameters.BayesianAcq)
        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(1)
        slider.setRange(-1,self.parameters._nbError-1)
        slider.setValue(self.parameters.BayesianAcq)
        self.sliderBayesianAcq = slider   

        self.generalLayoutBayesian.addWidget(QLabel("Seg. Error"),self.current_line_Bayesian,0)
        self.generalLayoutBayesian.addWidget(QLabel(f"{self.parameters.BayesianAcq}"),self.current_line_Bayesian,1)
        self.generalLayoutBayesian.addWidget(btnNew,self.current_line_Bayesian,2)
        self.current_line_Bayesian +=1

    def _createOrderShiftError(self):
        """Creates the slider and the line edit for the order of the shift (linear shift error)."""
        btnNew,slider = self._createIntInput(self.parameters.orderShift)
        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(1)
        slider.setRange(1,3)
        slider.setValue(self.parameters.orderShift)
        self.sliderErrorOrderShift = slider   

        self.generalLayoutError.addWidget(QLabel("Order"),self.current_line_Error,0)
        self.generalLayoutError.addWidget(QLabel(f"{self.parameters.orderShift}"),self.current_line_Error,1)
        self.generalLayoutError.addWidget(btnNew,self.current_line_Error,2)
        self.current_line_Error +=1
    def _createDShiftError(self):
        """Creates the slider and the line edit for the distance of the shift (linear shift error)."""
        btnNew,slider = self._createIntInput(self.parameters.distanceShift)
        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(1)
        slider.setRange(1,10)
        slider.setValue(self.parameters.distanceShift)
        self.sliderErrorDistanceShift = slider   

        self.generalLayoutError.addWidget(QLabel("Distance"),self.current_line_Error,0)
        self.generalLayoutError.addWidget(QLabel(f"{self.parameters.distanceShift}"),self.current_line_Error,1)
        self.generalLayoutError.addWidget(btnNew,self.current_line_Error,2)
        self.current_line_Error +=1

    def _createAngleError(self):
        """Creates the slider and the line edit for the distance of the shift (linear shift error)."""
        btnNew,slider = self._createIntInput(self.parameters.angleError)
        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(90)
        slider.setRange(0,360)
        slider.setValue(self.parameters.angleError)
        self.sliderErrorAngle = slider   

        self.generalLayoutError.addWidget(QLabel("Angle (degrees)"),self.current_line_Error,0)
        self.generalLayoutError.addWidget(QLabel(f"{self.parameters.angleError}"),self.current_line_Error,1)
        self.generalLayoutError.addWidget(btnNew,self.current_line_Error,2)
        self.current_line_Error +=1

    def _createExpansionError(self):
        """Creates the slider and the line edit for the factor of the expansion (expansion error)."""
        btnNew,slider = self._createIntInput(self.parameters.factorError)
        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(100)
        slider.setRange(0,1000)
        slider.setValue(int(self.parameters.factorError*100))
        self.sliderErrorFactor = slider   

        self.generalLayoutError.addWidget(QLabel("Factor"),self.current_line_Error,0)
        self.generalLayoutError.addWidget(QLabel(f"{self.parameters.factorError}"),self.current_line_Error,1)
        self.generalLayoutError.addWidget(btnNew,self.current_line_Error,2)
        self.current_line_Error +=1
    def _createIterationsFCMError(self):
        """Creates the slider and the line edit for the number of iteration for the FCM error."""
        btnNew,slider = self._createIntInput(self.parameters.iterationError)
        slider.valueChanged.connect(self.update_int)
        slider.setTickInterval(10)
        slider.setRange(1,10)
        slider.setValue(int(self.parameters.iterationError/10))
        self.sliderErrorIteration = slider   

        self.generalLayoutError.addWidget(QLabel("Iterations"),self.current_line_Error,0)
        self.generalLayoutError.addWidget(QLabel(f"{self.parameters.iterationError}"),self.current_line_Error,1)
        self.generalLayoutError.addWidget(btnNew,self.current_line_Error,2)
        self.current_line_Error +=1
    def _createSigmaCanny(self):
        """Creates the slider and the line edit for the sigma (Canny)."""
        btnNew,slider = self._createIntInput(self.parameters.sigmaCanny)
        slider.valueChanged.connect(self.update_int)
        self.sliderSigma = slider   
        slider.setRange(1,10000)
        try:
            slider.setValue(int(1000*self.parameters.sigmaCanny))
        except:
            slider.setValue(0)
        slider.setTickInterval(1000)
        self.generalLayoutSegm.addWidget(QLabel("Sigma Canny"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.sigmaCanny}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createAlphaICM(self):
        """Creates the slider and the line edit for the alpha (ICM)."""
        btnNew,slider = self._createIntInput(self.parameters.alphaICM)
        slider.valueChanged.connect(self.update_int)
        self.sliderAlpha = slider   
        slider.setRange(0,10000)
        try:
            slider.setValue(int(1000*self.parameters.alphaICM))
        except:
            slider.setValue(0)
        slider.setTickInterval(1000)
        self.generalLayoutSegm.addWidget(QLabel("Alpha ICM"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.alphaICM}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createCombCanny(self):
        """Creates the slider and the line edit for the combination (Canny)."""
        btnNew,slider = self._createIntInput(self.parameters.combinationCanny)
        slider.valueChanged.connect(self.update_int)
        slider.setRange(1,3)
        slider.setTickInterval(1)
        slider.setValue(self.parameters.combinationCanny)
        self.sliderComb = slider   

        self.generalLayoutSegm.addWidget(QLabel("Comb. Canny"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.combinationCanny}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createCombPostCanny(self):
        """Creates the slider and the line edit for the combination Post (Canny filled)."""
        btnNew,slider = self._createIntInput(self.parameters.combinationCannyPost)
        slider.valueChanged.connect(self.update_int)
        slider.setRange(1,3)
        slider.setTickInterval(1)
        slider.setValue(self.parameters.combinationCannyPost)
        self.sliderCombPost = slider   

        self.generalLayoutSegm.addWidget(QLabel("Comb. Post Canny"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.combinationCannyPost}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createSigmaThreshCanny(self):
        """Creates the slider for the lower and upper thresholds of the Canny segmentations"""
        btnNew,slider = self._createIntInput(self.parameters.sigmaThreshLowCanny)
        btnNew2,slider2 = self._createIntInput(self.parameters.sigmaThreshHighCanny)
        slider.valueChanged.connect(self.update_int)
        slider2.valueChanged.connect(self.update_int)
        slider.setRange(0,100)
        slider2.setRange(0,100)
        slider.setTickInterval(10)
        slider2.setTickInterval(10)
        slider.setValue(int(self.parameters.sigmaThreshLowCanny*100))
        slider2.setValue(int(self.parameters.sigmaThreshHighCanny*100))
        self.sliderThreshLow = slider   
        self.sliderThreshHigh = slider2 

        self.generalLayoutSegm.addWidget(QLabel("Thresh. Low Canny"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.sigmaThreshLowCanny}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
        self.generalLayoutSegm.addWidget(QLabel("Thresh. High Canny"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.sigmaThreshHighCanny}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew2,self.current_line_Segm,2)
        self.current_line_Segm +=1

    def _createMaxiIterICM(self):
        """Creates the slider and the line edit for the max iteration of the ICM (ICM)."""
        btnNew,slider = self._createIntInput(self.parameters.max_iter_ICM)
        slider.valueChanged.connect(self.update_int)
        self.sliderMaxIter = slider   
        slider.setRange(1,10000)
        slider.setTickInterval(1000)
        slider.setValue(self.parameters.max_iter_ICM)
        self.generalLayoutSegm.addWidget(QLabel("Max. Iter."),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.max_iter_ICM}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createMaxiIterKMeanICM(self):
        """Creates the slider and the line edit for the max iteration of the kMean (ICM & KMean)."""
        btnNew,slider = self._createIntInput(self.parameters.max_iter_kmean_ICM)
        slider.valueChanged.connect(self.update_int)
        self.sliderMaxIterKmean = slider   
        slider.setRange(1,10000)
        slider.setTickInterval(1000)
        slider.setValue(self.parameters.max_iter_kmean_ICM)
        self.generalLayoutSegm.addWidget(QLabel("Max. Iter K Mean"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.max_iter_kmean_ICM}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createAlphaFCM(self):
        """Creates the slider and the line edit for the alpha (FCM)."""
        btnNew,slider = self._createIntInput(self.parameters.alphaFCM)
        slider.valueChanged.connect(self.update_int)
        self.sliderAlphaFCM = slider   
        slider.setRange(1,1000)
        try:
            slider.setValue(int(100*(self.parameters.alphaFCM - 1)))
        except:
            slider.setValue(1)
        slider.setTickInterval(1000)
        self.generalLayoutSegm.addWidget(QLabel("Alpha FCM"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.alphaFCM:.2f}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createmFCM(self):
        """Creates the slider and the line edit for the m (FCM)."""
        btnNew,slider = self._createIntInput(self.parameters.mFCM)
        slider.valueChanged.connect(self.update_int)
        self.slidermFCM = slider   
        slider.setRange(1,1000)
        try:
            slider.setValue(int(100*(self.parameters.mFCM - 1)))
        except:
            slider.setValue(1)
        slider.setTickInterval(1000)
        self.generalLayoutSegm.addWidget(QLabel("Fuzziness Parameter"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.mFCM:.2f}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createClassNumberFCM(self):
        """Creates the slider and the line edit for the Class Number (FCM)."""
        btnNew,slider = self._createIntInput(self.parameters.classNumberFCM)
        slider.valueChanged.connect(self.update_int)
        self.sliderClassNumberFCM = slider   
        slider.setRange(2,10)
        try:
            slider.setValue(int(self.parameters.classNumberFCM ))
        except:
            slider.setValue(2)
        slider.setTickInterval(1)
        self.generalLayoutSegm.addWidget(QLabel("Class Number"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.classNumberFCM}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createMaxiIterFCM(self):
        """Creates the slider and the line edit for the max iteration of the FCM (FCM)."""
        btnNew,slider = self._createIntInput(self.parameters.maxIterFCM)
        slider.valueChanged.connect(self.update_int)
        self.sliderMaxIterFCM = slider   
        slider.setRange(1,1000)
        slider.setTickInterval(100)
        slider.setValue(self.parameters.maxIterFCM)
        self.generalLayoutSegm.addWidget(QLabel("Max. Iter."),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.maxIterFCM}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createMaxiIterConvergenceFCM(self):
        """Creates the slider and the line edit for the max iteration convergences of mus of the FCM (FCM)."""
        btnNew,slider = self._createIntInput(self.parameters.maxIterConvergenceFCM)
        slider.valueChanged.connect(self.update_int)
        self.sliderMaxIterConvFCM = slider   
        slider.setRange(1,1000)
        slider.setTickInterval(100)
        slider.setValue(self.parameters.maxIterConvergenceFCM)
        self.generalLayoutSegm.addWidget(QLabel("Max. Iter. Conv."),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.maxIterConvergenceFCM}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createConvergenceDeltaFCM(self):
        """Create the threshold parameter for the mu optimization in FCM"""
        self.ConvergenceDeltaFCMLine = QLineEdit()
        self.ConvergenceDeltaFCMLine.setText(str(self.parameters.convergenceDeltaFCM))
        self.ConvergenceDeltaFCMLine.editingFinished.connect(self.update_int)

        self.generalLayoutSegm.addWidget(QLabel("Mu Thresh"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.convergenceDeltaFCM}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(self.ConvergenceDeltaFCMLine,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createConvergenceStepFCM(self):
        """Create the step parameter for the gradient descent in FCM"""
        self.ConvergenceStepFCMLine = QLineEdit()
        self.ConvergenceStepFCMLine.setText(str(self.parameters.convergenceStepFCM))
        self.ConvergenceStepFCMLine.editingFinished.connect(self.update_int)

        self.generalLayoutSegm.addWidget(QLabel("Grad. Step"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.convergenceStepFCM}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(self.ConvergenceStepFCMLine,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createStepsFilling(self):
        """Creates the slider and the line edit for the number of steps (filling)."""
        btnNew,slider = self._createIntInput(self.parameters.steps_filling)
        slider.valueChanged.connect(self.update_int)   
        slider.setRange(0,1000)
        slider.setTickInterval(100)
        slider.setValue(self.parameters.steps_filling)
        self.sliderStepsFilling = slider
        self.generalLayoutSegm.addWidget(QLabel("Steps Filling"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.steps_filling}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createMaxIterFilling(self):
        """Creates the slider and the line edit for the max iteration (filling)."""
        btnNew,slider = self._createIntInput(self.parameters.max_iter_fill)
        slider.valueChanged.connect(self.update_int)
        self.sliderMaxIterFilling = slider   
        slider.setRange(1,1000)
        slider.setTickInterval(100)
        slider.setValue(self.parameters.max_iter_fill)
        self.generalLayoutSegm.addWidget(QLabel("Max. Iter Filling"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.max_iter_fill}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createVerboseGraphFill(self):
        """Creates the slider and the line edit for the return of the graph in filling (filling f)."""
        btnNew = self._createBoolBox()
        btnNew.setChecked(self.parameters.verbose_graph_fill)
        btnNew.stateChanged.connect(partial(self.set_value_checked_VerboseGraphFill,btnNew))
        btnNew.setToolTip("Outputs the graph in the filling f process")
        self.generalLayoutSegm.addWidget(QLabel("Graph Filling"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.verbose_graph_fill}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createVerbose(self):
        """Creates the slider and the line edit for the return of the graph in filling (filling f)."""
        btnNew = self._createBoolBox()
        btnNew.setChecked(self.parameters.verbose)
        btnNew.stateChanged.connect(partial(self.set_value_checked_Verbose,btnNew))
        btnNew.setToolTip("Outputs steps in the process")
        btnNew2 = self._createBoolBox()
        btnNew2.setChecked(self.parameters.verbose)
        btnNew2.stateChanged.connect(partial(self.set_value_checked_Verbose,btnNew))
        btnNew2.setToolTip("Outputs steps in the process")
        btnNew3 = self._createBoolBox()
        btnNew3.setChecked(self.parameters.verbose)
        btnNew3.stateChanged.connect(partial(self.set_value_checked_Verbose,btnNew))
        btnNew3.setToolTip("Outputs steps in the process")
        self.generalLayoutSegm.addWidget(QLabel("Verbose"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.verbose}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
        self.generalLayoutError.addWidget(QLabel("Verbose"),self.current_line_Error,0)
        self.generalLayoutError.addWidget(QLabel(f"{self.parameters.verbose}"),self.current_line_Error,1)
        self.generalLayoutError.addWidget(btnNew2,self.current_line_Error,2)
        self.current_line_Error +=1
        self.generalLayoutBayesian.addWidget(QLabel("Verbose"),self.current_line_Bayesian,0)
        self.generalLayoutBayesian.addWidget(QLabel(f"{self.parameters.verbose}"),self.current_line_Bayesian,1)
        self.generalLayoutBayesian.addWidget(btnNew3,self.current_line_Bayesian,2)
        self.current_line_Bayesian +=1
    def _createSaveBox(self):
        """Create the bool box for the save segmentation combo box"""
        btnNew = self._createBoolBox()
        btnNew.setChecked(self.parameters.SaveSegm)
        btnNew.stateChanged.connect(partial(self.set_value_checked_SaveSegm,btnNew))
        btnNew.setToolTip("Save the resulting segmentations. If set to False, the segmentations' results will not be kept and will be lost.")
        btnNew2 = self._createBoolBox()
        btnNew2.setChecked(self.parameters.SaveSegm)
        btnNew2.stateChanged.connect(partial(self.set_value_checked_SaveSegm,btnNew))
        btnNew2.setToolTip("Save the resulting segmentations. If set to False, the segmentations' results will not be kept and will be lost.")
        btnNew3 = self._createBoolBox()
        btnNew3.setChecked(self.parameters.SaveSegm)
        btnNew3.stateChanged.connect(partial(self.set_value_checked_SaveSegm,btnNew))
        btnNew3.setToolTip("Save the resulting segmentations. If set to False, the segmentations' results will not be kept and will be lost.")
        self.generalLayoutSegm.addWidget(QLabel("Save"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.SaveSegm}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
        #self.generalLayoutError.addWidget(QLabel("Save"),self.current_line_Error,0)
        #self.generalLayoutError.addWidget(QLabel(f"{self.parameters.SaveSegm}"),self.current_line_Error,1)
        #self.generalLayoutError.addWidget(btnNew2,self.current_line_Error,2)
        #self.current_line_Error +=1
        #self.generalLayoutBayesian.addWidget(QLabel("Save"),self.current_line_Bayesian,0)
        #self.generalLayoutBayesian.addWidget(QLabel(f"{self.parameters.SaveSegm}"),self.current_line_Bayesian,1)
        #self.generalLayoutBayesian.addWidget(btnNew3,self.current_line_Bayesian,2)
        #self.current_line_Bayesian +=1
    def _createStatsBox(self):
        """Create the bool box for the stats of the segmentation combo box"""
        btnNew = self._createBoolBox()
        btnNew.setChecked(self.parameters.doStats)
        btnNew.stateChanged.connect(partial(self.set_value_checked_doStats,btnNew))
        btnNew.setToolTip("Compute the averages of the segmentations. Also computes the second moment.")
        self.generalLayoutSegm.addWidget(QLabel("Stats"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.doStats}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createCurvesBox(self):
        """Create the bool box for the TAC computation combo box"""
        btnNew = self._createBoolBox()
        btnNew.setChecked(self.parameters.doCurves)
        btnNew.stateChanged.connect(partial(self.set_value_checked_doCurves,btnNew))
        btnNew.setToolTip("Compute the TACs of the segmentations.")
        self.generalLayoutSegm.addWidget(QLabel("Curves"),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.doCurves}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createCoefficientsBox(self):
        """Create the bool box for the coefficients combo box"""
        btnNew = self._createBoolBox()
        btnNew.setChecked(self.parameters.doCoefficients)
        btnNew.stateChanged.connect(partial(self.set_value_checked_doCoefficients,btnNew))
        btnNew.setToolTip("Compute the Dice and Jaccard coefficients for the segmentations.")
        self.generalLayoutSegm.addWidget(QLabel("Coeff."),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.doCoefficients}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(btnNew,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createThresholdBox(self):
        """Create the slider and the line edit for the thresholding"""
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
        self.generalLayoutSegm.addWidget(QLabel("Thresh."),self.current_line_Segm,0)
        self.generalLayoutSegm.addWidget(QLabel(f"{self.parameters.doThreshold}, {self.parameters.threshold}"),self.current_line_Segm,1)
        self.generalLayoutSegm.addWidget(subWidget,self.current_line_Segm,2)
        self.current_line_Segm +=1
    def _createParamList(self):
        """Create all the parameters, depending on the segmentation, error, and Dynesty types"""
        self.generalLayoutSegm.addWidget(QLabel("Parameter"),1,0)
        self.generalLayoutSegm.addWidget(QLabel("Values"),1,1)
        self.generalLayoutSegm.addWidget(QLabel("New Values"),1,2)
        self.generalLayoutDefor.addWidget(QLabel("Parameter"),1,0)
        self.generalLayoutDefor.addWidget(QLabel("Values"),1,1)
        self.generalLayoutDefor.addWidget(QLabel("New Values"),1,2)
        self.generalLayoutError.addWidget(QLabel("Parameter"),1,0)
        self.generalLayoutError.addWidget(QLabel("Values"),1,1)
        self.generalLayoutError.addWidget(QLabel("New Values"),1,2)
        self.generalLayoutBayesian.addWidget(QLabel("Parameter"),1,0)
        self.generalLayoutBayesian.addWidget(QLabel("Values"),1,1)
        self.generalLayoutBayesian.addWidget(QLabel("New Values"),1,2)
        self.generalLayoutNoise.addWidget(QLabel("Parameter"),1,0)
        self.generalLayoutNoise.addWidget(QLabel("Values"),1,1)
        self.generalLayoutNoise.addWidget(QLabel("New Values"),1,2)

        #Segmentation Specific
        self._createSegmType()
        self._createSubImageSliders()
        self._createAcqValue()
        if self.parameters.SegmType in ["Canny Filled","Canny Contour"]:
            self._createMethodCannyType()
            self._createSigmaCanny()
            self._createCombCanny()
            self._createSigmaThreshCanny()
            if self.parameters.SegmType in ["Canny Filled"]:
                self._createCombPostCanny()
        elif self.parameters.SegmType == "ICM":
            self._createAlphaICM()
            self._createMaxiIterICM()
            self._createMaxiIterKMeanICM()
        elif self.parameters.SegmType == "FCM":
            self._createAlphaFCM()
            self._createmFCM()
            self._createClassNumberFCM()
            self._createMaxiIterFCM()
            self._createMaxiIterConvergenceFCM()
            self._createConvergenceDeltaFCM()
            self._createConvergenceStepFCM()
        elif self.parameters.SegmType == "k Mean":
            self._createMaxiIterKMeanICM
        elif self.parameters.SegmType in ["Filling (very slow)","Filling f (very slow)"]:
            self._createSeedSliders()
            self._createVerboseGraphFill()
            self._createStepsFilling()
            self._createMaxIterFilling()
            self._createFactorFillingRange()
            self._createThresholdLimitFilling()
            if self.parameters.SegmType == "Filling (very slow)":
                self._createFactorFFilling()
        elif self.parameters.SegmType == "Ellipsoid":
            self._createCenterEllipsoidSliders()
            self._createAxesEllipsoidSliders()
        #Deformation Specific
        self._createDeformationType()
        self._createDeformationSeg()
        if self.parameters.deformationType == "Linear Shift":
            self._createDShiftDeformation()
        if self.parameters.deformationType == "Rotation":
            self._createAngleDeformation()
        if self.parameters.deformationType == "Expansion":
            self._createFactorDeformation()
        if self.parameters.deformationType == "Reflection":
            self._createAxisReflectionDeformation()
        if self.parameters.deformationType == "Flip All":
            self._createAxisFlipDeformation()
        if self.parameters.deformationType == "Switch Two":
            self._createAxesSwitchDeformation()
        if self.parameters.deformationType in ["Union", "Intersection"]:
            pass
        self._createDeleteAfterDeformation()
        #Error Specific
        self._createErrorType()
        if self.parameters.ErrorType != "None":
            self._createErrorValue()
        if self.parameters.ErrorType == "Linear Shift":
            self._createOrderShiftError()
            self._createDShiftError()
        if self.parameters.ErrorType == "Rotation":
            self._createOrderShiftError()
            self._createAngleError()
        if self.parameters.ErrorType == "Expansion":
            self._createOrderShiftError()
            self._createExpansionError()
        if self.parameters.ErrorType == "FCM":
            self._createIterationsFCMError()
        #Bayesian Specific
        self._createBayesianType()
        if self.parameters.CurveTypeBayesian == "Errors":
            self._createThreshBaySliders()
        self._createBayesianValue()
        #Noise Specific
        self._createNoiseGraphs()
        self._createNoiseType()
        self._createNoiseFormulaeDisplay()
        if self.parameters.NoiseType == "Gaussian":
            self._createNoiseMu()
            self._createNoiseSigma()
        elif self.parameters.NoiseType == "Rayleigh":
            self._createNoiseRayleighA()
            self._createNoiseRayleighB()
        elif self.parameters.NoiseType == "Erlang (Gamma)":
            self._createNoiseErlangA()
            self._createNoiseErlangB()
        elif self.parameters.NoiseType == "Uniform":
            self._createNoiseUnifA()
            self._createNoiseUnifB()
        elif self.parameters.NoiseType == "Exponential":
            self._createNoiseExponential()
        #Erase Specific
        self._createHeadersErase()
        #self._createEraseButton()
        #Utilities
        self._createSaveBox()
        self._createVerbose()
        self._createStatsBox()
        self._createCurvesBox()
        self._createCoefficientsBox()
        self._createThresholdBox()
        #Exit
        self._createExitButtons()
        self.generalLayoutNoise.setColumnStretch(0,1)
        self.generalLayoutNoise.setColumnStretch(1,5)
        self.generalLayoutNoise.setColumnStretch(2,5)

    def MethCombo_Changed(self):
        """Links the method of distance computation and the combo box in the parameters (Canny)"""
        self.parameters.methodCanny = self.MethCombo.currentText()
        self.refresh_app()
    def SegmCombo_Changed(self):
        """Links the method of segmentation and the combo box in the parameters"""
        self.parameters.SegmType = self.SegmCombo.currentText()
        self.refresh_app()
    def DeformationMethodCombo_Changed(self):
        """Links the method of deformation method and the combo box in the parameters"""
        self.parameters.deformationType = self.DeformationCombo.currentText()
        self.refresh_app()
    def ErrorMethodCombo_Changed(self):
        """Links the method of error computation and the combo box in the parameters"""
        self.parameters.ErrorType = self.ErrorCombo.currentText()
        self.refresh_app()
    def BayesianMethodCombo_Changed(self):
        """Links the model of Bayesian analysis and the combo box in the parameters"""
        self.parameters.BayesianType = self.BayesianCombo.currentText()
        self.refresh_app()
    def NoiseMethodCombo_Changed(self):
        """Links the model of Noise and the combo box in the parameters"""
        self.parameters.NoiseType = self.NoiseCombo.currentText()
        self.refresh_app()
    def ModelBayesianMethodCombo_Changed(self):
        """Links the method of error and the combo box in the parameters"""
        self.parameters.ModelBayesian = self.ModelCombo.currentText()
        self.refresh_app()
    def CurvesBayesianMethodCombo_Changed(self):
        """Links the method of error and the combo box in the parameters"""
        self.parameters.CurveTypeBayesian = self.CurvesCombo.currentText()
        self.refresh_app()
    def set_value_checked_doCoefficients(self,box:QCheckBox):
        """Links the compute coefficient bool and the combo box in the parameters"""
        self.parameters.doCoefficients = box.isChecked()
        self.refresh_app()
    def set_value_checked_doThreshold(self,box:QCheckBox):
        """Links the compute threshold bool and the combo box in the parameters"""
        self.parameters.doThreshold = box.isChecked()
        self.refresh_app()
    def set_value_checked_doStats(self,box:QCheckBox):
        """Links the compute stats bool and the combo box in the parameters"""
        self.parameters.doStats = box.isChecked()
        self.refresh_app()
    def set_value_checked_SaveSegm(self,box:QCheckBox):
        """Links the save segmentations bool and the combo box in the parameters"""
        self.parameters.SaveSegm = box.isChecked()
        self.refresh_app()
    def set_value_checked_VerboseGraphFill(self,box:QCheckBox):
        """Links the verbose graph bool and the combo box in the parameters (filling)"""
        self.parameters.verbose_graph_fill = box.isChecked()
        self.refresh_app()
    def set_value_checked_Verbose(self,box:QCheckBox):
        """Links the verbose bool and the combo box in the parameters"""
        self.parameters.verbose = box.isChecked()
        self.refresh_app()
    def set_value_checked_doCurves(self,box:QCheckBox):
        """Links the compute curves (TACs) bool and the combo box in the parameters"""
        self.parameters.doCurves = box.isChecked()
        self.refresh_app()
    def set_value_checked_DeleteAfterDeformation(self,box:QCheckBox):
        """Links the verbose graph bool and the combo box in the parameters (filling)"""
        self.parameters.deleteAfterDeformation = box.isChecked()
        self.refresh_app()
    def set_value_slider(self,slider:QSlider,lineedit:QLineEdit):
        """Links the slider and the line edit together"""
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
            slider.setValue(int(lineedit.text()))
        except:
            slider.setValue(0)
        try:
            lineedit.setText(f"{int(lineedit.text())}")
        except:
            lineedit.setText("0")
        try: self.update_seed()
        except: pass
        try: self.update_center_ellipsoid()
        except: pass
        try: self.update_axes_ellipsoid()
        except: pass
    def set_value_line_edit_noSlider(self,lineedit:QLineEdit):
        """
        Updates the parameters accoding to the lineedit
        """
        try:
            lineedit.setText(f"{int(lineedit.text())}")
        except:
            lineedit.setText("0")
        self.update_subImage()
    def update_center_ellipsoid(self):
        """
        When a part of the center of the ellipsoid is changed, updates the parameters
        """
        self.parameters.centerEllipsoid[0] = self.sliderAxialValueCenter.text()
        self.parameters.centerEllipsoid[1] = self.sliderCoronalValueCenter.text()
        self.parameters.centerEllipsoid[2] = self.sliderSagittalValueCenter.text()
    def update_axes_ellipsoid(self):
        """
        When a part of the axes of the ellipsoid is changed, updates the parameters
        """
        self.parameters.axesEllipsoid[0] = self.sliderAxialValueAxes.text()
        self.parameters.axesEllipsoid[1] = self.sliderCoronalValueAxes.text()
        self.parameters.axesEllipsoid[2] = self.sliderSagittalValueAxes.text()
    def update_seed(self):
        """
        When a part of the seed is changed, updates the parameters
        """
        self.parameters.seed[0] = self.sliderAxialValueSeed.text()
        self.parameters.seed[1] = self.sliderCoronalValueSeed.text()
        self.parameters.seed[2] = self.sliderSagittalValueSeed.text()
    def update_subImage(self):
        """
        When a part of the subimage is changed, updates the parameters
        """
        self.parameters.subImage[0,0] = self.sliderAcqValueSubImMin.text()
        self.parameters.subImage[0,1] = self.sliderAcqValueSubImMax.text()
        self.parameters.subImage[1,0] = self.sliderAxialValueSubImMin.text()
        self.parameters.subImage[1,1] = self.sliderAxialValueSubImMax.text()
        self.parameters.subImage[2,0] = self.sliderCoronalValueSubImMin.text()
        self.parameters.subImage[2,1] = self.sliderCoronalValueSubImMax.text()
        self.parameters.subImage[3,0] = self.sliderSagittalValueSubImMin.text()
        self.parameters.subImage[3,1] = self.sliderSagittalValueSubImMax.text()
    def update_int(self):
        """
        Updates all the int parameters when the slider or the associated QLineEdit is changed
        """
        try:
            self.parameters.SegmAcq = self.sliderSegmAcq.value()
        except: pass
        try:
            self.parameters.alphaICM = self.sliderAlpha.value()/1000
        except: pass
        try:
            self.parameters.alphaFCM = self.sliderAlphaFCM.value()/100 + 1
        except: pass
        try:
            self.parameters.mFCM = self.slidermFCM.value()/100 + 1
        except: pass
        try:
            self.parameters.classNumberFCM = self.sliderClassNumberFCM.value()
        except: pass
        try:
            self.parameters.convergenceDeltaFCM = float(self.ConvergenceDeltaFCMLine.text())
        except: pass
        try:
            self.parameters.convergenceStepFCM = float(self.ConvergenceStepFCMLine.text())
        except: pass
        try:
            self.parameters.sigmaCanny = self.sliderSigma.value()/1000
        except: pass
        try:
            self.parameters.combinationCanny = self.sliderComb.value()
        except: pass
        try:
            self.parameters.combinationCannyPost = self.sliderCombPost.value()
        except: pass
        try:
            self.parameters.sigmaThreshLowCanny = self.sliderThreshLow.value()/100
        except: pass
        try:
            self.parameters.sigmaThreshHighCanny = self.sliderThreshHigh.value()/100
        except: pass
        try:
            self.parameters.max_iter_ICM = self.sliderMaxIter.value()
        except: pass
        try:
            self.parameters.max_iter_kmean_ICM = self.sliderMaxIterKmean.value()
        except: pass
        try:
            self.parameters.maxIterFCM = self.sliderMaxIterFCM.value()
        except: pass
        try:
            self.parameters.maxIterConvergenceFCM = self.sliderMaxIterConvFCM.value()
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
            self.parameters.BayesianAcq = self.sliderBayesianAcq.value()
        except: pass
        try:
            self.parameters.orderShift = self.sliderErrorOrderShift.value()
        except: pass
        try:
            self.parameters.distanceShift = self.sliderErrorDistanceShift.value()
        except: pass
        try:
            self.parameters.angleError = self.sliderErrorAngle.value()
        except: pass
        try:
            self.parameters.factorError = self.sliderErrorFactor.value()/100
        except:
            pass
        try:
            self.parameters.iterationError = self.sliderErrorIteration.value()*10
        except:
            pass
        try:
            self.parameters.threshold = self.sliderThresh.value()/100
        except: pass
        try:
            self.parameters.factor_fill_f = self.sliderFactorF.value()/100
        except: pass
        try:
            self.parameters.Bayesian_thresh_perc = self.sliderBayesianThreshPerc.value()/100
        except: pass
        try:
            self.parameters.Bayesian_thresh_value = self.sliderBayesianThreshValue.value()/100
        except: pass
        try:
            self.parameters.factor_Fill_range[0] = float(self.FactorFRangeValueMin.text())
        except: pass
        try:
            self.parameters.factor_Fill_range[1] = float(self.FactorFRangeValueMax.text())
        except: pass
        try:
            self.parameters.threshold_fill = float(self.ThresholdFillingLimit.text())
        except: pass
        try:
            self.parameters.deformationSegm = self.sliderDeforSeg.value()
        except:
            pass
        try:
            self.parameters.deformationDistanceShift[0] = self.sliderDeformationDistanceShift1.value()
            self.parameters.deformationDistanceShift[1] = self.sliderDeformationDistanceShift2.value()
            self.parameters.deformationDistanceShift[2] = self.sliderDeformationDistanceShift3.value()
        except:
            pass
        try:
            self.parameters.deformationRotate[0] = self.sliderDeformationRotate1.value()
            self.parameters.deformationRotate[1] = self.sliderDeformationRotate2.value()
            self.parameters.deformationRotate[2] = self.sliderDeformationRotate3.value()
        except:
            pass
        try:
            self.parameters.deformationExpansion[0] = self.sliderDeformationExpansion1.value()/100
            self.parameters.deformationExpansion[1] = self.sliderDeformationExpansion2.value()/100
            self.parameters.deformationExpansion[2] = self.sliderDeformationExpansion3.value()/100
        except:
            pass

        try:
            self.parameters.deformationReflectionAxis = self.sliderDeformationAxisReflection.value()
        except:
            pass
        try:
            self.parameters.switchAxes[0] = self.sliderDeformationAxesSwitch1.value()
        except:
            pass
        try:
            self.parameters.switchAxes[1] = self.sliderDeformationAxesSwitch2.value()
        except:
            pass
        if self.parameters.switchAxes[1] < self.parameters.switchAxes[0]:
            tmp = self.parameters.switchAxes[1]
            self.parameters.switchAxes[0] = self.parameters.switchAxes[1]
            self.parameters.switchAxes[1] = tmp
        try:
            self.parameters.flipAxis = self.sliderDeformationAxisFlip.value()
        except:
            pass

    def update_EraseValues(self):
        """Updates the parameters for the erase values"""
        try:
            self.parameters.EraseSegm = int(self.sliderEraseSegm.value())
        except:
            self.parameters.EraseSegm = -1
        try:
            self.parameters.EraseError = int(self.sliderEraseError.value())
        except:
            self.parameters.EraseError = -1
        try:
            self.parameters.EraseBayesian = int(self.sliderEraseBayesian.value())
        except:
            self.parameters.EraseBayesian = -1
    def update_QLines(self):
        """
        Updates all the float parameters the QLineEdit is changed
        """   
        try:
            self.parameters.NoiseMu = float(self.btnMuNoise.text())
        except: 
            self.parameters.NoiseMu = 0.0
        try:
            self.parameters.NoiseSigma = float(self.btnSigmaNoise.text())
        except: 
            self.parameters.NoiseSigma = 1.0
        try:
            self.parameters.NoiseARayleigh = float(self.btnNoiseRayleighA.text())
        except: 
            self.parameters.NoiseARayleigh = 0.0
        try:
            if float(self.btnNoiseRayleighB.text()) > 0:
                self.parameters.NoiseBRayleigh = float(self.btnNoiseRayleighB.text())
            else:
                self.parameters.NoiseBRayleigh = 1.0
        except: 
            self.parameters.NoiseBRayleigh = 1.0
        try:
            if float(self.btnNoiseErlangA.text()) > 0:
                self.parameters.NoiseAErlang = float(self.btnNoiseErlangA.text())
            else:
                self.parameters.NoiseAErlang = 1.0
        except: 
            self.parameters.NoiseAErlang = 1.0
        try:
            if float(self.btnNoiseErlangB.text()) > 0:
                self.parameters.NoiseBErlang = int(self.btnNoiseErlangB.text())
            else:
                self.parameters.NoiseBErlang = 1
        except: 
            self.parameters.NoiseBErlang = 1
        try:
            self.parameters.NoiseAUniform = float(self.btnNoiseUnifA.text())
        except: 
            self.parameters.NoiseAUniform = 0.0
        try:
            self.parameters.NoiseBUniform = float(self.btnNoiseUnifB.text())
        except: 
            self.parameters.NoiseBUniform = 1.0
        try:
            self.parameters.NoiseExponential = float(self.btnNoiseExponential.text())
        except: 
            self.parameters.NoiseExponential = 1.0
        self.refresh_app()
    def EraseChoiceComboChanged(self):
        """Changes the Type of Erasure to do"""
        self.parameters.EraseType = self.EraseTypeChoice.currentText()
        self.refresh_app()
    def EraseButtonClicked(self):
        """Activate the Erase Button"""
        
        self.refresh_app()
    def refresh_app(self):
        """
        When a different segmentation, error or Dynesty scheme is chosen, update the whole window and only display the parameters of interest
        """
        if self.generalLayoutSegm is not None:
            while self.generalLayoutSegm.count():
                item = self.generalLayoutSegm.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        if self.generalLayoutDefor is not None:
            while self.generalLayoutDefor.count():
                item = self.generalLayoutDefor.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        if self.generalLayoutError is not None:
            while self.generalLayoutError.count():
                item = self.generalLayoutError.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        if self.generalLayoutBayesian is not None:
            while self.generalLayoutBayesian.count():
                item = self.generalLayoutBayesian.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        if self.generalLayoutNoise is not None:
            while self.generalLayoutNoise.count():
                item = self.generalLayoutNoise.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        if self.generalLayoutErase is not None:
            while self.generalLayoutErase.count():
                item = self.generalLayoutErase.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        self.initialize_param_window()


class MplCanvas(FigureCanvasQTAgg):
    """Class for the images and the graphs as a widget"""
    def __init__(self, parent=None, width:float=5, height:float=4, dpi:int=75):
        """Creates an empty figure with axes and fig as parameters"""
        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout= True)
        self.axes = fig.add_subplot(111)
        self.fig = fig
        super(MplCanvas, self).__init__(fig)
