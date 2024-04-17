from re import sub
import numpy as np
try:
    import os
except:
    pass
#os.environ['KMP_DUPLICATE_LIB_OK']='True'
import matplotlib.pyplot as plt
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.Pickle_Functions as PF
import MyFunctions.Extract_Images_R as Extract_r
import MyFunctions.Extract_Images as Extract
from GUI_parts.GUIParam import GUIParameters
from GUI_parts.ParamWindow import ParamWindow
from GUI_parts.ExportWindow import ExportWindow
import time
import MyFunctions.Batch_Segmentations
import MyFunctions.Batch_Errors
import MyFunctions.Batch_Deform
###
import numpy as np
import time
import scipy.integrate
###
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt5 import QtGui
from functools import partial
###
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
###
import markdown

size_Image = 200

class MainWindow(QMainWindow):
    """
    Main window of the GUI.
    """    
    def __init__(self):
        """Initializes the GUI Window"""
        self.tabs = QTabWidget()
        self.BUTTON_SIZE = 40
        self.DISPLAY_HEIGHT = 35
        self.current_line = 0
        #self.displayImageLine = 0
        self.first_pass = True
        self.lineImage1D = -1
        super().__init__(parent=None)
        self.setMinimumSize(1200, 775)
        self.setWindowTitle("TRU-IMP")
        self.generalLayout = QGridLayout()
        self.generalLayoutLog = QGridLayout()
        self.generalLayoutReadMe = QGridLayout()
        self.generalLayoutContributing = QGridLayout()
        self.generalLayoutLicense = QGridLayout()
        self.generalLayoutCodeOfConduct = QGridLayout()
        centralWidget = QWidget(self)
        self.centralWidget = centralWidget
        centralWidgetLog = QWidget(self)
        centralWidgetReadMe = QWidget(self)
        centralWidgetContributing = QWidget(self)
        centralWidgetLicense = QWidget(self)
        centralWidgetCodeOfConduct = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        centralWidgetLog.setLayout(self.generalLayoutLog)
        centralWidgetReadMe.setLayout(self.generalLayoutReadMe)
        centralWidgetContributing.setLayout(self.generalLayoutContributing)
        centralWidgetLicense.setLayout(self.generalLayoutLicense)
        centralWidgetCodeOfConduct.setLayout(self.generalLayoutCodeOfConduct)
        self.tabs.addTab(centralWidget,"Main")
        self.tabs.addTab(centralWidgetLog,"Log")
        self.tabs.addTab(centralWidgetReadMe,"Read Me")
        self.tabs.addTab(centralWidgetContributing,"Contributing")
        self.tabs.addTab(centralWidgetLicense,"License")
        self.tabs.addTab(centralWidgetCodeOfConduct,"Code of Conduct")

        self.setCentralWidget(self.tabs)
        #First Line
        self._createExtractDock()
        self._createNoiseButtons()
        #Next Line
        #Second Line
        self._createSavingDock()
        self._createInfoParam()
        self._createImageDisplayType()
        #self._createImageDisplayBars()
        #Line 4
        self._createImageDisplay()
        #Next Line
        self._createTACImage()
        #Next Line
        self._create1DImage()
        #Last Line
        self._createExitButton() 
        ##Creates the Log Tab
        self._createLog()
        ##Creates the ReadMe Tab
        self._createReadMe()
        self._createContributing()
        self._createLicense()
        self._createCodeOfConduct()
        #Status Bar
        self._createStatusBar()
        self._createProgressBar()

        #self.setGeometry(0,0,100,100)

        self.generalLayout.setColumnStretch(1,1)
        self.generalLayout.setColumnStretch(2,1)
        self.generalLayout.setColumnStretch(3,1)
        self.generalLayout.setRowStretch(0,1)
        self.generalLayout.setRowStretch(1,1)
        self.generalLayout.setRowStretch(2,3)
        self.generalLayout.setRowStretch(3,3)
        self.showMaximized()
        
    def _createLog(self):
        """Create a Log tab to keep track of the processes"""
        self.logText = QTextEdit()
        self.logText.setReadOnly(True)
        try:
            self.logText.setText(self.Image.progress_log)
        except:
            self.logText.setText("Nothing started")
        self.generalLayoutLog.addWidget(self.logText)
        self.exit3 = QPushButton("Exit")
        self.exit3.setToolTip("Closes the GUI and its dependencies")
        self.exit3.clicked.connect(self.closing_button)
        self.exit3.setShortcut("Ctrl+Shift+E")
        self.generalLayoutLog.addWidget(self.exit3)  
    def _createReadMe(self):
        """Creates a ReadMe tab with the ReadMe file infos"""
        basedir = os.path.dirname(__file__)
        self.ReadMeText = QTextEdit()
        self.ReadMeText.setReadOnly(True)
        try:
            f = open(f'{basedir}/ReadMe.md', 'r')
            htmlmarkdown = markdown.markdown( f.read() )
            self.ReadMeText.setText(htmlmarkdown)
        except: pass
        self.generalLayoutReadMe.addWidget(self.ReadMeText)
        self.exit2 = QPushButton("Exit")
        self.exit2.setToolTip("Closes the GUI and its dependencies")
        self.exit2.clicked.connect(self.closing_button)
        self.exit2.setShortcut("Ctrl+Shift+E")
        self.generalLayoutReadMe.addWidget(self.exit2)  
    def _createContributing(self):
        """Creates a Contributing tab with the Contributing file infos"""
        basedir = os.path.dirname(__file__)
        self.ContributingText = QTextEdit()
        self.ContributingText.setReadOnly(True)
        try:
            f = open(f'{basedir}/Contributing.md', 'r')
            htmlmarkdown = markdown.markdown( f.read() )
            self.ContributingText.setText(htmlmarkdown)
        except: pass
        self.generalLayoutContributing.addWidget(self.ContributingText)
        self.exit4 = QPushButton("Exit")
        self.exit4.setToolTip("Closes the GUI and its dependencies")
        self.exit4.clicked.connect(self.closing_button)
        self.exit4.setShortcut("Ctrl+Shift+E")
        self.generalLayoutContributing.addWidget(self.exit4)
    def _createLicense(self):
        """Creates a License tab with the License file infos"""
        basedir = os.path.dirname(__file__)
        self.LicenseText = QTextEdit()
        self.LicenseText.setReadOnly(True)
        try:
            f = open(f'{basedir}/License', 'r')
            htmlmarkdown = markdown.markdown( f.read() )
            self.LicenseText.setText(htmlmarkdown)
        except: pass
        self.generalLayoutLicense.addWidget(self.LicenseText)
        self.exit5 = QPushButton("Exit")
        self.exit5.setToolTip("Closes the GUI and its dependencies")
        self.exit5.clicked.connect(self.closing_button)
        self.exit5.setShortcut("Ctrl+Shift+E")
        self.generalLayoutLicense.addWidget(self.exit5)
    def _createCodeOfConduct(self):
        """Creates a Code of Conduct tab with the Code of Conduct file infos"""
        basedir = os.path.dirname(__file__)
        self.CodeOfConductText = QTextEdit()
        self.CodeOfConductText.setReadOnly(True)
        try:
            f = open(f'{basedir}/CODE_OF_CONDUCT.md', 'r')
            htmlmarkdown = markdown.markdown( f.read() )
            self.CodeOfConductText.setText(htmlmarkdown)
        except: pass
        self.generalLayoutCodeOfConduct.addWidget(self.CodeOfConductText)
        self.exit6 = QPushButton("Exit")
        self.exit6.setToolTip("Closes the GUI and its dependencies")
        self.exit6.clicked.connect(self.closing_button)
        self.exit6.setShortcut("Ctrl+Shift+E")
        self.generalLayoutCodeOfConduct.addWidget(self.exit6)
    def _createStatusBar(self):
        """Create a status bar at the bottom of the GUI"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)      
        self.statusBar.showMessage("Nothing started")
    def _createProgressBar(self):
        """Creates a Progress Bar at the bottom of the GUI"""
        self.progressBar = QProgressBar(self.centralWidget)
        self.progressBar.setValue(0)
        self.generalLayout.addWidget(self.progressBar,self.current_line-2,2)

    def _createNoiseButtons(self):
        """Create the Noise button at the top of the GUI"""
        subWidget = QWidget()
        layout = QHBoxLayout()
        subWidget.setLayout(layout)

        self.btn_noise = QPushButton("Noise")
        self.btn_noise.setShortcut("Ctrl+N")
        self.btn_noise.setToolTip("Adds the noise to the images according to the selected parameters (Ctrl+N)")
        self.btn_noise.clicked.connect(self.run_noise)

        self.btn_deform = QPushButton("Deform.")
        self.btn_deform.setShortcut("Ctrl+D")
        self.btn_deform.setToolTip("Makes a deformation on a segmentation according to the selected parameters (Ctrl+D)")
        self.btn_deform.clicked.connect(self.run_deform)

        self.btn_erase = QPushButton("Erase")
        self.btn_erase.setToolTip("Danger! Will erase a calculated aspect as specified")
        self.btn_erase.clicked.connect(self.run_erase)

        layout.addWidget(self.btn_noise)
        layout.addWidget(self.btn_deform)
        layout.addWidget(self.btn_erase)
        self.generalLayout.addWidget(subWidget,self.current_line,3,1,1)    
        self.current_line += 1
    def _createInfoParam(self):
        """Create the dock at the top from where the parameters, the infos and the lauch buttons are"""
        subWidget = QWidget()
        layout = QHBoxLayout()
        subWidget.setLayout(layout)
        
        self.btn_segm = QPushButton("Segment")
        self.btn_segm.setShortcut("Ctrl+S")
        self.buttonErrors = QPushButton("ErrorBars")
        self.buttonErrors.setShortcut("Ctrl+R")
        self.buttonBayesian = QPushButton("Bayesian")
        self.buttonBayesian.setShortcut("Ctrl+Y")

        self.btn_segm.setToolTip("Runs the segmentations according to the selected parameters (Ctrl+S)")
        self.buttonErrors.setToolTip("Runs the error bars according to the selected parameters (Ctrl+R)")
        self.buttonBayesian.setToolTip("Runs the Bayesian analyses according to the selected parameters (Ctrl+Y)")

        self.buttonErrors.clicked.connect(self.run_errors)
        self.buttonBayesian.clicked.connect(self.run_Bayesian)
        self.btn_segm.clicked.connect(self.run_segm)

        layout.addWidget(self.btn_segm)
        layout.addWidget(self.buttonErrors)
        layout.addWidget(self.buttonBayesian)
        self.generalLayout.addWidget(subWidget,self.current_line,3)    
    def _createExitButton(self):
        """Create an exit button"""
        self.exit = QPushButton("Exit")
        self.exit.setToolTip("Closes the GUI and its dependencies (Ctrl+Shift+E)")
        self.exit.setShortcut("Ctrl+Shift+E")
        self.exit.clicked.connect(self.closing_button)
        self.generalLayout.addWidget(self.exit,self.current_line,3)  
        self.current_line += 2
    def closing_button(self):
        try:
            self.generalLayout.removeWidget(self.GraphRunPlot)
            self.generalLayout.removeWidget(self.GraphTracePlot)
            self.generalLayout.removeWidget(self.GraphCornerPlot)
            self.GraphRunPlot.deleteLater()
            self.GraphTracePlot.deleteLater()
            self.GraphCornerPlot.deleteLater()
            self.GraphRunPlot = None
            self.GraphTracePlot = None
            self.GraphCornerPlot = None
            del self.GraphRunPlot
            del self.GraphTracePlot
            del self.GraphCornerPlot
        except: pass
        self.close()
    def _createExtractDock(self):
        """Create the dock to enter a line and the buttons to extract, load and, browse the origin of the acquisition"""
        subWidget = QWidget()
        msg_extract = QLabel("Path: ")
        source = QLineEdit()
        self.btn_extr = QPushButton("Extract")
        self.btn_extr.setShortcut("Ctrl+E")
        self.btn_load = QPushButton("Load")
        self.btn_load.setShortcut("Ctrl+L")
        btn_browse = QPushButton("Browse")
        btn_browse.setShortcut("Ctrl+B")

        self.btn_extr.setToolTip("Extracts the relevant information from a folder containing .dcm files (Ctrl+E)")
        self.btn_load.setToolTip("Loads the selected .pkl file (Ctrl+L)")
        btn_browse.setToolTip("Opens a local browser to select a file (Ctrl+B)")
        
        self.btn_extr.clicked.connect(partial(self.extract_button,source))
        self.btn_load.clicked.connect(partial(self.load_button,source))
        btn_browse.clicked.connect(partial(self.browse_button_file,source))

        layout = QHBoxLayout()
        subWidget.setLayout(layout)
        layout.addWidget(btn_browse)
        layout.addWidget(self.btn_extr)
        layout.addWidget(self.btn_load)

        self.generalLayout.addWidget(msg_extract,self.current_line,0)  
        self.generalLayout.addWidget(source,self.current_line,1)           
        self.generalLayout.addWidget(subWidget,self.current_line,2)  
    def _createSavingDock(self):
        """Create a button and a dock to save the image directly (removed)"""
        subWidget1 = QWidget()
        subWidget2 = QWidget()
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        subWidget1.setLayout(layout1)
        subWidget2.setLayout(layout2)
        self.btn_param = QPushButton("Parameters")
        self.btn_param.setShortcut("Ctrl+P")
        self.btn_param.setToolTip("Opens a window to select the paremeters used for segmentations, error bars, and Bayesian analyses (Ctrl+P)")
        self.btn_param.clicked.connect(self.open_parameters)
          
        self.btn = QPushButton("Info")
        self.btn.setShortcut("Ctrl+I")
        self.btn.clicked.connect(self.on_button_clicked_infos)
        self.btn.setToolTip("Displays the infos of the current loaded acquisition (Ctrl+I)")
        path = QLineEdit()
        path_name = QLineEdit()
        path.setText("")
        btn_export = QPushButton("Export")
        btn_export.setToolTip("Opens an window to decide what to export (Ctrl+T)")
        btn_export.clicked.connect(self.open_export)
        btn_export.setShortcut("Ctrl+T")
        layout1.addWidget(path)
        layout1.addWidget(path_name)
        layout2.addWidget(btn_export)
        layout2.addWidget(self.btn)
        layout2.addWidget(self.btn_param)
        self.generalLayout.addWidget(subWidget2,self.current_line,2)  
    def _createImageDisplay(self):
        """Create the docks for the 2D images to be shown"""
        self.showFocus = False
        self.showSubImage = False
        self.showLog = False
        self.showSuperpose = False
        msg_Image = QLabel("View: ")
        msg_Axial = QLabel("Axial")
        msg_Sagittal = QLabel("Sagittal")
        msg_Coronal = QLabel("Coronal")
        self.axial = MplCanvas(self)
        self.sagittal = MplCanvas(self)
        self.coronal = MplCanvas(self)
        self.axial_cid = self.axial.fig.canvas.mpl_connect('button_press_event', partial(self.onClick, which = self.axial))
        self.sagittal_cid = self.sagittal.fig.canvas.mpl_connect('button_press_event', partial(self.onClick, which = self.sagittal))
        self.coronal_cid = self.coronal.fig.canvas.mpl_connect('button_press_event', partial(self.onClick, which = self.coronal))
        self.axial_cod = self.axial.fig.canvas.mpl_connect('scroll_event', partial(self.onRoll, which = self.axial))
        self.sagittal_cod = self.sagittal.fig.canvas.mpl_connect('scroll_event', partial(self.onRoll, which = self.sagittal))
        self.coronal_cod = self.coronal.fig.canvas.mpl_connect('scroll_event', partial(self.onRoll, which = self.coronal))

        try:
            self.axial.axes.pcolormesh(self.Image.Image[0,0,:,:])  
            self.sagittal.axes.pcolormesh(self.Image.Image[0,:,0,:])  
            self.coronal.axes.pcolormesh(self.Image.Image[0,:,:,0])
        except:
            self.axialGraph = self.axial.axes.pcolormesh(np.zeros((100,100)))
            self.sagittal.axes.pcolormesh(np.zeros((100,100)))
            self.coronal.axes.pcolormesh(np.zeros((100,100)))
        try:
            if self.first_pass:
                self.displayImageLine = self.current_line+2
        except: pass
        self.axial.setMinimumSize(size_Image,size_Image)
        self.coronal.setMinimumSize(size_Image,size_Image)
        self.sagittal.setMinimumSize(size_Image,size_Image)
        self.generalLayout.addWidget(msg_Image,self.displayImageLine,0)  
        self.generalLayout.addWidget(msg_Axial,self.displayImageLine-1,1)
        self.generalLayout.addWidget(msg_Sagittal,self.displayImageLine-1,3)
        self.generalLayout.addWidget(msg_Coronal,self.displayImageLine-1,2)
        self.generalLayout.addWidget(self.axial,self.displayImageLine,1)
        self.generalLayout.addWidget(self.sagittal,self.displayImageLine,3)
        self.generalLayout.addWidget(self.coronal,self.displayImageLine,2)
        try:
            if self.first_pass == True:
                self.current_line += 3
                self.first_pass = False
        except: pass
    def _createImageDisplayType(self):
        """Create the button for the combo box of the images\nAlso create the combo box for the choice of the result"""
        subWidget = QWidget()
        layout = QHBoxLayout()
        subWidget.setLayout(layout)
        self.ImageViewCombo = QComboBox()
        self.view = "Slice"
        self.view_range = "All"
        self.ImageViewCombo.addItem("Slice")
        self.ImageViewCombo.addItem("Flat")
        self.ImageViewCombo.addItem("Sub. Slice")
        self.ImageViewCombo.addItem("Sub. Flat")
        self.ImageViewCombo.addItem("Segm. Slice")
        self.ImageViewCombo.addItem("Segm. Flat")
        self.ImageViewCombo.addItem("Segm. Sub. Slice")
        self.ImageViewCombo.addItem("Segm. Sub. Flat")
        self.ImageViewCombo.activated[str].connect(self.combo_box_changed)

        self.ResultViewCombo = QComboBox()
        self.resultView = "TAC"
        self.ResultViewCombo.addItem("TAC")
        self.ResultViewCombo.addItem("TAC Total")
        self.ResultViewCombo.addItem("TAC Cumulative")
        self.ResultViewCombo.addItem("TAC Cumulative Total")
        self.ResultViewCombo.addItem("TAC Slice")
        self.ResultViewCombo.addItem("Dice")
        self.ResultViewCombo.addItem("Jaccard")
        self.ResultViewCombo.addItem("Energy")
        self.ResultViewCombo.addItem("Mus")
        self.ResultViewCombo.addItem("Factor f")
        self.ResultViewCombo.addItem("Bayesian")
        self.ResultViewCombo.addItem("Center of Mass")
        self.ResultViewCombo.addItem("Moments")
        self.ResultViewCombo.addItem("Ratio TAC/Error")
        self.ResultViewCombo.activated[str].connect(self.combo_box_result_changed)

        self.ResultImageTypeCombo = QComboBox()
        self.resultImageType = "Array: Base Image"
        self.ResultImageTypeCombo.addItem("Array: Base Image")
        self.ResultImageTypeCombo.addItem("Physical: Base Image")
        self.ResultImageTypeCombo.addItem("Array: CT")
        self.ResultImageTypeCombo.addItem("Physical: CT")
        self.ResultImageTypeCombo.addItem("Physical: Combined")
        self.ResultImageTypeCombo.activated[str].connect(self.combo_box_ImageType_changed)

        layout.addWidget(self.ImageViewCombo)
        layout.addWidget(self.ResultViewCombo)
        layout.addWidget(self.ResultImageTypeCombo)
        self.generalLayout.addWidget(subWidget,self.current_line,1)
        self.current_line += 1
    def _createImageDisplayBars(self):
        """Create the sliders for the 2D images, the 1D images and the TAC."""
        try:
            self.generalLayout.removeWidget(self.slider_widget)
            self.slider_widget.setParent(None)
        except:
            pass
        sizeText = 30
        self.slider_widget = QWidget()
        subWidget = QWidget()
        layout = QGridLayout()
        sublayout = QGridLayout()
        self.slider_widget.setLayout(layout)
        subWidget.setLayout(sublayout)
        self.sliderAcq = QSlider(Qt.Horizontal)
        self.sliderAxial = QSlider(Qt.Horizontal)
        self.sliderSagittal = QSlider(Qt.Horizontal)
        self.sliderCoronal = QSlider(Qt.Horizontal)
        self.sliderSegm = QSlider(Qt.Horizontal)
        self.sliderSegmStats = QSlider(Qt.Horizontal)
        self.sliderBayesian = QSlider(Qt.Horizontal)
        self.sliderFitted = QSlider(Qt.Horizontal)
        try:
            self.sliderAcq.setMinimum(0);self.sliderAcq.setMaximum(self.Image.nb_acq-1)
            self.sliderAxial.setMinimum(0);self.sliderAxial.setMaximum(self.Image.nb_slice-1)
            self.sliderSagittal.setMinimum(0);self.sliderSagittal.setMaximum(self.Image.width-1)
            self.sliderCoronal.setMinimum(0);self.sliderCoronal.setMaximum(self.Image.length-1)
            self.sliderSegm.setMinimum(-1);self.sliderSegm.setMaximum(self.Image.voi_counter-1)
            self.sliderSegmStats.setMinimum(-1);self.sliderSegmStats.setMaximum(self.Image.voi_statistics_counter-1)
            try:
                self.sliderBayesian.setMinimum(-1);self.sliderBayesian.setMaximum(self.Image.bayesian_results_avg.shape[1]-1)
            except: pass
            try:
                self.sliderFitted.setMinimum(-1);self.sliderFitted.setMaximum(self.Image.bayesian_results_avg.shape[0]-1)
            except: 
                self.sliderFitted.setMinimum(-1);self.sliderFitted.setMaximum(-1)
        except:
            pass
        self.sliderSegm.setValue(-1)
        self.sliderSegmStats.setValue(-1)
        self.sliderBayesian.setValue(-1)
        self.sliderFitted.setValue(-1)
        self.sliderAcq.setTickPosition(QSlider.TicksBothSides)
        self.sliderAxial.setTickPosition(QSlider.TicksBothSides)
        self.sliderSagittal.setTickPosition(QSlider.TicksBothSides)
        self.sliderCoronal.setTickPosition(QSlider.TicksBothSides)
        self.sliderSegm.setTickPosition(QSlider.TicksBothSides)
        self.sliderSegmStats.setTickPosition(QSlider.TicksBothSides)
        self.sliderBayesian.setTickPosition(QSlider.TicksBothSides)
        self.sliderFitted.setTickPosition(QSlider.TicksBothSides)
        self.sliderAcq.setSingleStep(1)
        self.sliderAxial.setSingleStep(1)
        self.sliderSagittal.setSingleStep(1)
        self.sliderCoronal.setSingleStep(1)
        self.sliderSegm.setSingleStep(1)
        self.sliderSegmStats.setSingleStep(1)
        self.sliderBayesian.setSingleStep(1)
        self.sliderFitted.setSingleStep(1)
        layout.addWidget(self.sliderAcq,0,1)
        layout.addWidget(self.sliderAxial,1,1)
        layout.addWidget(self.sliderSagittal,3,1)
        layout.addWidget(self.sliderCoronal,2,1)

        self.AcqValueHeader = QLabel("Acq:")
        self.AxialValueHeader = QLabel("Ax:")
        self.SagittalValueHeader = QLabel("Sag:")
        self.CoronalValueHeader = QLabel("Cor:")
        self.SegmValueHeader = QLabel("Segm:")
        SegmStatsValueHeader = QLabel("Segm. Errors:")
        BayesianValueHeader = QLabel("Bay. Values:")
        FittedValueHeader = QLabel("Fit Bay.:")
        self.checkBoxMsgSubImage = QLabel("Sub Image:")
        self.checkBoxMsgFocus = QLabel("Focus:")
        self.checkBoxMsgSuperpose = QLabel("Sup:")

        self.sliderAcqValue = QLineEdit()
        self.sliderAxialValue = QLineEdit()
        self.sliderSagittalValue = QLineEdit()
        self.sliderCoronalValue = QLineEdit()
        self.sliderSegmValue = QLineEdit()
        self.sliderSegmStatsValue = QLineEdit()
        self.sliderBayesianValue = QLineEdit()
        self.sliderFittedValue = QLineEdit()
        self.checkBoxFocus = QCheckBox()
        self.checkBoxSubImage = QCheckBox()
        self.checkBoxLog = QCheckBox()
        self.checkBoxSuperpose = QCheckBox()
        self.sliderAcqValue.setFixedWidth(sizeText)
        self.sliderAxialValue.setFixedWidth(sizeText)
        self.sliderSagittalValue.setFixedWidth(sizeText)
        self.sliderCoronalValue.setFixedWidth(sizeText)
        self.sliderSegmValue.setFixedWidth(sizeText)
        self.sliderSegmStatsValue.setFixedWidth(sizeText)
        self.sliderBayesianValue.setFixedWidth(sizeText)
        self.sliderFittedValue.setFixedWidth(sizeText)
        try:
            self.sliderAcqValue.setText(f"{self.set_value_slider(self.sliderAcq,self.sliderAcqValue)}")
            self.sliderAxialValue.setText(f"{self.set_value_slider(self.sliderAxial,self.sliderAxialValue)}")
            self.sliderSagittalValue.setText(f"{self.set_value_slider(self.sliderSagittal,self.sliderSagittalValue)}")
            self.sliderCoronalValue.setText(f"{self.set_value_slider(self.sliderCoronal,self.sliderCoronalValue)}")
            self.sliderSegmValue.setText(f"{self.set_value_slider(self.sliderSegm,self.sliderSegmValue)}")
            self.sliderSegmStatsValue.setText(f"{self.set_value_slider(self.sliderSegmStats,self.sliderSegmStatsValue)}")
            self.sliderBayesianValue.setText(f"{self.set_value_slider(self.sliderBayesian,self.sliderBayesianValue)}")
            self.sliderFittedValue.setText(f"{self.set_value_slider(self.sliderFitted,self.sliderFittedValue)}")
            self.sliderAcqValue.editingFinished.connect(partial(self.set_value_line_edit,self.sliderAcq,self.sliderAcqValue))
            self.sliderAxialValue.editingFinished.connect(partial(self.set_value_line_edit,self.sliderAxial,self.sliderAxialValue))
            self.sliderSagittalValue.editingFinished.connect(partial(self.set_value_line_edit,self.sliderSagittal,self.sliderSagittalValue))
            self.sliderCoronalValue.editingFinished.connect(partial(self.set_value_line_edit,self.sliderCoronal,self.sliderCoronalValue))
            self.sliderSegmValue.editingFinished.connect(partial(self.set_value_line_edit,self.sliderSegm,self.sliderSegmValue))
            self.sliderSegmStatsValue.editingFinished.connect(partial(self.set_value_line_edit,self.sliderSegmStats,self.sliderSegmStatsValue))
            self.sliderBayesianValue.editingFinished.connect(partial(self.set_value_line_edit,self.sliderBayesian,self.sliderBayesianValue))
            self.sliderFittedValue.editingFinished.connect(partial(self.set_value_line_edit,self.sliderFitted,self.sliderFittedValue))
            self.sliderAcq.valueChanged.connect(partial(self.set_value_slider,self.sliderAcq,self.sliderAcqValue))
            self.sliderAxial.valueChanged.connect(partial(self.set_value_slider,self.sliderAxial,self.sliderAxialValue))
            self.sliderSagittal.valueChanged.connect(partial(self.set_value_slider,self.sliderSagittal,self.sliderSagittalValue))
            self.sliderCoronal.valueChanged.connect(partial(self.set_value_slider,self.sliderCoronal,self.sliderCoronalValue))
            self.sliderSegm.valueChanged.connect(partial(self.set_value_slider,self.sliderSegm,self.sliderSegmValue))
            self.sliderSegmStats.valueChanged.connect(partial(self.set_value_slider,self.sliderSegmStats,self.sliderSegmStatsValue))
            self.sliderBayesian.valueChanged.connect(partial(self.set_value_slider,self.sliderBayesian,self.sliderBayesianValue))
            self.sliderFitted.valueChanged.connect(partial(self.set_value_slider,self.sliderFitted,self.sliderFittedValue))
            self.checkBoxFocus.stateChanged.connect(self.set_value_focus)
            self.checkBoxSubImage.stateChanged.connect(self.set_value_subImage)
            self.checkBoxLog.stateChanged.connect(self.set_value_log)
            self.checkBoxSuperpose.stateChanged.connect(self.set_value_superpose)
        except:
            pass
        checkBoxMsglog = QLabel("log:")

        sublayout.addWidget(self.checkBoxMsgFocus,0,0)
        sublayout.addWidget(self.checkBoxFocus,0,1)
        sublayout.addWidget(self.checkBoxMsgSubImage,0,2)
        sublayout.addWidget(self.checkBoxSubImage,0,3)
        sublayout.addWidget(checkBoxMsglog,0,4)
        sublayout.addWidget(self.checkBoxLog,0,5)
        sublayout.addWidget(self.checkBoxMsgSuperpose,0,6)
        sublayout.addWidget(self.checkBoxSuperpose,0,7)
        subWidget.setMinimumHeight(40)
        subWidget.setContentsMargins(0,0,0,0)

        sublayout.addWidget(self.SegmValueHeader,2,0)
        sublayout.addWidget(self.sliderSegm,2,1)
        sublayout.addWidget(self.sliderSegmValue,2,2)

        sublayout.addWidget(SegmStatsValueHeader,3,0)
        sublayout.addWidget(self.sliderSegmStats,3,1)
        sublayout.addWidget(self.sliderSegmStatsValue,3,2)

        sublayout.addWidget(BayesianValueHeader,4,0)
        sublayout.addWidget(self.sliderFitted,4,1)
        sublayout.addWidget(self.sliderFittedValue,4,2)

        sublayout.addWidget(FittedValueHeader,5,0)
        sublayout.addWidget(self.sliderBayesian,5,1)
        sublayout.addWidget(self.sliderBayesianValue,5,2)

        layout.addWidget(self.AcqValueHeader,0,0)
        layout.addWidget(self.AxialValueHeader,1,0)
        layout.addWidget(self.SagittalValueHeader,3,0)
        layout.addWidget(self.CoronalValueHeader,2,0) 
        
        layout.addWidget(self.sliderAcqValue,0,2)
        layout.addWidget(self.sliderAxialValue,1,2)
        layout.addWidget(self.sliderCoronalValue,2,2)
        layout.addWidget(self.sliderSagittalValue,3,2)
        
        self.generalLayout.addWidget(subWidget,self.displayImageLine+1,3)
        self.generalLayout.addWidget(self.slider_widget,self.displayImageLine+1,1)
        self.slider_widget.resize(500,500)
    def _createTACImage(self):
        """Create an empty image for where the TAC and the results will be"""
        self.TACImage = MplCanvas(self)
        self.TAC_cid = self.TACImage.fig.canvas.mpl_connect('button_press_event', partial(self.onClick, which = self.TACImage))
        self.TAC_cod = self.TACImage.fig.canvas.mpl_connect('scroll_event', partial(self.onRoll, which = self.TACImage))
        self.TACImage.setMinimumSize(size_Image,size_Image)
        self.base_TAC_axes()
        self.generalLayout.addWidget(self.TACImage,self.current_line,2)
        self.current_line += 1
    def _create1DImage(self):
        """Create the dock for the 1D Image (i.e. the slices)"""
        label = QLabel("Slices")
        self.AxialImage1D = MplCanvas(self)
        self.SagittalImage1D = MplCanvas(self)
        self.CoronalImage1D = MplCanvas(self)
        self.axial1D_cid = self.AxialImage1D.fig.canvas.mpl_connect('button_press_event', partial(self.onClick, which = self.AxialImage1D))
        self.sagittal1D_cid = self.SagittalImage1D.fig.canvas.mpl_connect('button_press_event', partial(self.onClick, which = self.SagittalImage1D))
        self.coronal1D_cid = self.CoronalImage1D.fig.canvas.mpl_connect('button_press_event', partial(self.onClick, which = self.CoronalImage1D))
        self.axial1D_cod = self.AxialImage1D.fig.canvas.mpl_connect('scroll_event', partial(self.onRoll, which = self.AxialImage1D))
        self.sagittal1D_cod = self.SagittalImage1D.fig.canvas.mpl_connect('scroll_event', partial(self.onRoll, which = self.SagittalImage1D))
        self.coronal1D_cod = self.CoronalImage1D.fig.canvas.mpl_connect('scroll_event', partial(self.onRoll, which = self.CoronalImage1D))
        self.AxialImage1D.setMinimumSize(size_Image,size_Image)
        self.SagittalImage1D.setMinimumSize(size_Image,size_Image)
        self.CoronalImage1D.setMinimumSize(size_Image,size_Image)

        self.base_1D_axes()

        if self.lineImage1D == -1:
            self.generalLayout.addWidget(label,self.current_line,0)
            self.generalLayout.addWidget(self.AxialImage1D,self.current_line,1)
            self.generalLayout.addWidget(self.CoronalImage1D,self.current_line,2)
            self.generalLayout.addWidget(self.SagittalImage1D,self.current_line,3)
            self.lineImage1D = self.current_line
            self.current_line += 1
        else: 
            self.generalLayout.addWidget(label,self.lineImage1D,0)
            self.generalLayout.addWidget(self.AxialImage1D,self.lineImage1D,1)
            self.generalLayout.addWidget(self.CoronalImage1D,self.lineImage1D,2)
            self.generalLayout.addWidget(self.SagittalImage1D,self.lineImage1D,3)
        self.BayesianShown = False
    def _createErrorMessage(self,message:str=""):
        """Create an error message and displays it"""
        alert = QMessageBox()
        if message =="":
            alert.setText("An error occurred")
        else:
            alert.setText(message)
        alert.exec()
    def set_value_slider(self,slider:QSlider,lineedit:QLineEdit):
        """Link the slider and the lineedit to the same value"""
        lineedit.setText(str(slider.value()))
        self.update_all()
        return slider.value()
    def set_value_focus(self):
        """Switch the focus of the image when the box is checked"""
        if self.checkBoxFocus.isChecked() == True:
            self.showFocus = True
        else:
            self.showFocus = False
        self.update_all()
    def set_value_subImage(self):
        """Switch the subImage view of the image when the box is checked"""
        if self.checkBoxSubImage.isChecked() == True:
            self.showSubImage = True
        else:
            self.showSubImage = False
        self.update_all()
    def set_value_log(self):
        """Switch the log of the image when the box is checked"""
        if self.checkBoxLog.isChecked() == True:
            self.showLog = True
        else:
            self.showLog = False
        self.update_all()
    def set_value_superpose(self):
        """Switch the superpose of the image when the box is checked"""
        if self.checkBoxSuperpose.isChecked() == True:
            self.showSuperpose = True
        else:
            self.showSuperpose = False
        self.update_all()
    def set_value_line_edit(self,slider:QSlider,lineedit:QLineEdit):
        """Link the slider and the lineedit to the same value"""
        try:
            slider.setValue(int(lineedit.text()))
        except:
            slider.setValue(0)
        try:
            lineedit.setText(f"{int(lineedit.text())}")
        except:
            lineedit.setText("0")
        self.update_all()
    def combo_box_changed(self):
        """Change the parameters with respect to the view of the acquisition"""
        self.view = self.ImageViewCombo.currentText()
        if self.view in ["Slice","Flat","Segm. Slice","Segm. Flat"]:
            self.view_range = "All"
        else:
            self.view_range = "Sub"
        try:
            self.update_all()
        except: pass
    def combo_box_result_changed(self):
        """Update the view between partial and full"""
        self.resultView = self.ResultViewCombo.currentText()
        try:
            self.update_all()
        except: pass
    def combo_box_ImageType_changed(self):
        """Update the view between partial and full"""
        self.resultImageType = self.ResultImageTypeCombo.currentText()
        try:
            self.update_all()
        except: pass
    def open_parameters(self):
        try:
            window = ParamWindow(self.parameters,self)
            window.setWindowModality(Qt.ApplicationModal)
            window.signalClosed.connect(self.updateRadioNuclide)
            window.signalClosed.connect(self.update_all)
            window.show()
        except:
            self._createErrorMessage("No acquisition loaded yet")
    def updateRadioNuclide(self):
        self.Image.radioNuclide = self.parameters._radioNuclide


    def open_export(self):
        """
        Opens a new window to decide what to export and what to save
        """
        try:
            window = ExportWindow(self.parameters,self.Image,self)
            window.setWindowModality(Qt.ApplicationModal)
            window.show()
        except:
            self._createErrorMessage()
    def run_segm(self):
        """
        Function to run the segmentations based on the input parameters
        """
        try:
            self.threadSegmentation = QThread()
            self.workerSegmentation = WorkerSegmentation(Image = self.Image, parameters = self.parameters)
            self.workerSegmentation.moveToThread(self.threadSegmentation)

            self.threadSegmentation.started.connect(self.workerSegmentation.segment)
            self.workerSegmentation.finished.connect(self.threadSegmentation.quit)
            self.workerSegmentation.finished.connect(self.workerSegmentation.deleteLater)
            self.threadSegmentation.finished.connect(self.threadSegmentation.deleteLater)
            self.workerSegmentation.progress.connect(self.workerDisplayStatus)
            self.workerSegmentation.error.connect(self._createErrorMessage)
            #self.workerSegmentation.completed.connect(self.WorkerTaskDone)

            self.threadSegmentation.start()

            self.btn_segm.setEnabled(False)
            self.threadSegmentation.finished.connect(
                lambda: self.btn_segm.setEnabled(True)
            )
            self.workerSegmentation.finished.connect(self.update_all)
 
        except: pass

    def run_errors(self):
        """
        Function to run the errors based on the input parameters
        """
        if True:
            self.threadErrors = QThread()
            self.workerErrors = WorkerErrors(Image = self.Image, parameters = self.parameters)
            self.workerErrors.moveToThread(self.threadErrors)

            self.threadErrors.started.connect(self.workerErrors.errors)
            self.workerErrors.finished.connect(self.threadErrors.quit)
            self.workerErrors.finished.connect(self.workerErrors.deleteLater)
            self.threadErrors.finished.connect(self.threadErrors.deleteLater)
            self.workerErrors.progress.connect(self.workerDisplayStatus)
            self.workerErrors.error.connect(self._createErrorMessage)
            #self.workerErrors.completed.connect(self.WorkerTaskDone)

            self.threadErrors.start()

            self.buttonErrors.setEnabled(False)
            self.threadErrors.finished.connect(
                lambda: self.buttonErrors.setEnabled(True)
            )
            self.workerErrors.finished.connect(self.update_all)
 
        else: pass

    def run_Bayesian(self):
        """
        Function to run the Bayesian Analyses to extract the coefficients based on the input parameters
        """

        if True:
            self.threadBayesian = QThread()
            self.workerBayesian = WorkerBayesian(Image = self.Image, parameters = self.parameters)
            self.workerBayesian.moveToThread(self.threadBayesian)

            self.threadBayesian.started.connect(self.workerBayesian.bayesian)
            self.workerBayesian.finished.connect(self.threadBayesian.quit)
            self.workerBayesian.finished.connect(self.workerBayesian.deleteLater)
            self.threadBayesian.finished.connect(self.threadBayesian.deleteLater)
            self.workerBayesian.progress.connect(self.workerDisplayStatus)
            self.workerBayesian.error.connect(self._createErrorMessage)
            #self.workerBayesian.completed.connect(self.WorkerTaskDone)

            self.threadBayesian.start()

            self.buttonBayesian.setEnabled(False)
            self.threadBayesian.finished.connect(
                lambda: self.buttonBayesian.setEnabled(True)
            )
            self.workerBayesian.finished.connect(self.update_all)
 
        else: pass

    def run_noise(self):
        """
        Function to add noise to the image.
        For now, the resulting image will overwrite the previous (or basic) one
        """   
        if True:
            self.threadNoise = QThread()
            self.workerNoise = WorkerNoise(Image = self.Image, parameters = self.parameters)
            self.workerNoise.moveToThread(self.threadNoise)

            self.threadNoise.started.connect(self.workerNoise.noise)
            self.workerNoise.finished.connect(self.threadNoise.quit)
            self.workerNoise.finished.connect(self.workerNoise.deleteLater)
            self.threadNoise.finished.connect(self.threadNoise.deleteLater)
            self.workerNoise.progress.connect(self.workerDisplayStatus)
            self.workerNoise.error.connect(self._createErrorMessage)
            #self.workerNoise.completed.connect(self.WorkerTaskDone)

            self.threadNoise.start()

            self.btn_noise.setEnabled(False)
            self.threadNoise.finished.connect(
                lambda: self.btn_noise.setEnabled(True)
            )
            self.workerNoise.finished.connect(self.update_all)
 
        else: pass

    def run_deform(self):
        """
        Function to deform segmentations.
        """
        if True:
            self.threadDeform = QThread()
            self.workerDeform = WorkerDeformation(Image = self.Image, parameters = self.parameters)
            self.workerDeform.moveToThread(self.threadDeform)

            self.threadDeform.started.connect(self.workerDeform.deformation)
            self.workerDeform.finished.connect(self.threadDeform.quit)
            self.workerDeform.finished.connect(self.workerDeform.deleteLater)
            self.threadDeform.finished.connect(self.threadDeform.deleteLater)
            self.workerDeform.progress.connect(self.workerDisplayStatus)
            self.workerDeform.error.connect(self._createErrorMessage)
            #self.workerDeform.completed.connect(self.WorkerTaskDone)

            self.threadDeform.start()

            self.btn_deform.setEnabled(False)
            self.threadDeform.finished.connect(
                lambda: self.btn_deform.setEnabled(True)
            )
            self.workerDeform.finished.connect(self.workerDeformFinished)
            self.workerDeform.finished.connect(self.update_all)
 
        else: pass

    def run_erase(self):
        """
        Function to erase computations
        """
        if True:
            self.threadErase = QThread()
            self.workerErase = WorkerErase(Image = self.Image, parameters = self.parameters)
            self.workerErase.moveToThread(self.threadErase)

            self.threadErase.started.connect(self.workerErase.erase)
            self.workerErase.finished.connect(self.threadErase.quit)
            self.workerErase.finished.connect(self.workerErase.deleteLater)
            self.threadErase.finished.connect(self.threadErase.deleteLater)
            self.workerErase.progress.connect(self.workerDisplayStatus)
            self.workerErase.error.connect(self._createErrorMessage)
            #self.workerErase.completed.connect(self.WorkerTaskDone)

            self.threadErase.start()

            self.btn_erase.setEnabled(False)
            self.threadErase.finished.connect(
                lambda: self.btn_erase.setEnabled(True)
            )
            self.workerErase.finished.connect(self.update_all)
 
        else: pass

    def update_all(self):
        """Main function when something is changed to update all the views"""
        self.update_Result()
        if self.resultView != "TAC Slice":
            self.update_1D()
        else:
            try:
                self.update_TAC_slice()
            except:
                pass
        self.update_view()
        self.update_segm()
    def update_segm(self):
        """Update the segmentation and segmentation error sliders"""
        self.sliderSegm.setMaximum(self.Image.voi_counter-1)
        self.sliderSegmStats.setMaximum(self.Image.voi_statistics_counter-1)
        try:
            self.sliderFitted.setMaximum(self.Image.bayesian_results_avg.shape[0]-1)
        except:
            self.sliderFitted.setMaximum(-1)
        self.sliderBayesian.setMaximum(self.Image.bayesian_counter-1)
    def update_Result(self):
        """Update the middle image according to the type of result to be displayed"""
        try: self.cb.remove()
        except: pass
        if self.resultView in ["TAC", "TAC Slice", "TAC Total", "TAC Cumulative", "TAC Cumulative Total"]:
            self.update_TAC()
        elif self.resultView == "Dice":
            self.update_Dice()
        elif self.resultView == "Jaccard":
            self.update_Jaccard()
        elif self.resultView == "Energy":
            self.update_Energy_View()
        elif self.resultView == "Mus":
            self.update_Mus_View()
        elif self.resultView == "Factor f":
            self.update_FactorF_View()
        elif self.resultView == "Bayesian":
            try:
                self.update_Bayesian(self.sliderBayesian.value())
                self.update_BayesianPlots()
            except: pass
        elif self.resultView == "Center of Mass":
            self.update_centerMass()
        elif self.resultView == "Moments":
            self.update_MomentSeg()
        elif self.resultView == "Ratio TAC/Error":
            self.update_RatioTACError()
    def update_Dice(self):
        """Shows the Dice coefficients in the middle image"""
        try:
            try:
                self.TACImage.fig.delaxes(self.axTAC)
            except:
                pass
            self.TACImage.axes.cla()
            im = self.TACImage.axes.pcolormesh(self.Image.dice_all)
            self.base_coeff_axes(im)
            self.TACImage.draw() 
            self.switch_bottom_view()
        except:
            pass
    def update_Jaccard(self):
        """Shows the Jaccard coefficients in the middle image"""
        try:
            try:
                self.TACImage.fig.delaxes(self.axTAC)
            except:
                pass
            self.TACImage.axes.cla()
            im = self.TACImage.axes.pcolormesh(self.Image.jaccard_all)
            self.base_coeff_axes(im)
            self.TACImage.draw() 
            self.switch_bottom_view()
        except:
            pass
    def update_Energy_View(self):
        """Shows the Energy of the segmentations in the middle image"""
        try:
            try:
                self.TACImage.fig.delaxes(self.axTAC)
            except:
                pass
            self.TACImage.axes.cla()
            if self.sliderSegm.value() >= 0:
                self.TACImage.axes.plot(self.Image.energies[f"{self.sliderSegm.value()}"])
            else:
                for i in range(self.Image.voi_counter):
                    self.TACImage.axes.plot(self.Image.energies[f"{i}"])
            self.TACImage.axes.set_title("Energy of the Segmentation");self.TACImage.axes.grid()
            self.TACImage.axes.set_xlabel("Iteration");self.TACImage.axes.set_ylabel("Energy")
            self.TACImage.axes.set_yscale("log")
            self.TACImage.draw() 
            self.switch_bottom_view()
        except:
            pass
    def update_Mus_View(self):
        """Shows the Convergence of the Average of the segmentations in the middle image"""
        try:
            try:
                self.TACImage.fig.delaxes(self.axTAC)
            except:
                pass
            self.TACImage.axes.cla()
            if self.sliderSegm.value() >= 0:
                for j in range(self.Image.mus[f"{self.sliderSegm.value()}"].shape[0]):
                    self.TACImage.axes.plot(self.Image.mus[f"{self.sliderSegm.value()}"][j,:,-1])
            else:
                for i in range(self.Image.voi_counter):
                    for j in range(self.Image.mus[f"{i}"].shape[0]):
                        self.TACImage.axes.plot(self.Image.mus[f"{i}"][j,:,-1])
            self.TACImage.axes.set_title("Centers of Mass of the Segmentation");self.TACImage.axes.grid()
            self.TACImage.axes.set_xlabel("Iteration");self.TACImage.axes.set_ylabel("Centers of Mass")
            self.TACImage.draw() 
            self.switch_bottom_view()
        except:
            pass
    def update_FactorF_View(self):
        """Shows the factor f graph used in the filling algorithm"""
        try:
            try:
                self.TACImage.fig.delaxes(self.axTAC)
            except:
                pass
            self.TACImage.axes.cla()
            if self.sliderSegm.value() >= 0:
                self.TACImage.axes.plot(self.Image.fFactorsFillingAxisX[f"{self.sliderSegm.value()}"],
                                        self.Image.fFactorsFillingAxisY[f"{self.sliderSegm.value()}"])
            tmp = f"{self.sliderSegm.value()}"
            self.TACImage.axes.set_title(f"Segmented volume as a function of the f factor\nwith f* = {(self.Image.fFactorsFillingAxisX[tmp][-2]):.2f}");self.TACImage.axes.grid()
            self.TACImage.axes.set_xlabel("f");self.TACImage.axes.set_ylabel("Segmented ratio")
            self.TACImage.axes.set_yscale("log")
            self.TACImage.draw() 
            self.switch_bottom_view()
        except:
            pass        
    def update_centerMass(self):
        """Shows the Center of Mass in the middle image"""
        try:
            try:
                self.TACImage.fig.delaxes(self.axTAC)
            except:
                pass
            self.TACImage.axes.cla()
            voi_center_of_mass = np.array(self.Image.voi_center_of_mass)
            voi_center_of_mass = voi_center_of_mass[~np.all(voi_center_of_mass == 0, axis=1)]
            self.axTAC = self.TACImage.fig.add_subplot(1,1,1,projection='3d')
            self.axTAC.scatter(voi_center_of_mass[:,0],
                                        voi_center_of_mass[:,1],
                                        voi_center_of_mass[:,2])
            self.TACImage.draw()
            self.switch_bottom_view()
        except:
            pass
    def update_MomentSeg(self):
        """Shows the Moments of the segmentations in the middle image"""
        try:
            try:
                self.TACImage.fig.delaxes(self.axTAC)
            except:
                pass
            self.TACImage.axes.cla()
            voi_moment_of_inertia = np.array(self.Image.voi_moment_of_inertia)
            voi_moment_of_inertia = voi_moment_of_inertia[~np.all(voi_moment_of_inertia == 0, axis=1)]
            self.axTAC = self.TACImage.fig.add_subplot(1,1,1,projection='3d')
            self.axTAC.scatter(voi_moment_of_inertia[:,0],
                                        voi_moment_of_inertia[:,1],
                                        voi_moment_of_inertia[:,2])
            self.TACImage.draw()
            self.switch_bottom_view()
        except:
            pass
    def update_RatioTACError(self):
        """Shows the Moments of the segmentations in the middle image"""
        try:
            try:
                self.TACImage.fig.delaxes(self.axTAC)
            except:
                pass
            self.TACImage.axes.cla()
            values = [self.sliderAcq.value(),self.sliderAxial.value(),self.sliderCoronal.value(),self.sliderSagittal.value()]
            subI = self.parameters.subImage[0,:]

            if self.view_range == "All":
                x_axis = self.Image.time
                if self.sliderSegm.value() >= 0 or self.sliderSegmStats.value() >= 0 or self.sliderFitted.value() >= 0:
                    if self.sliderSegmStats.value() >= 0:
                        y_axis = self.Image.voi_statistics_avg[self.sliderSegmStats.value()]
                        error = self.Image.voi_statistics_std[self.sliderSegmStats.value()]
            else:
                x_axis = self.Image.time[subI[0]:subI[1]]
                if self.sliderSegm.value() >= 0 or self.sliderSegmStats.value() >= 0:
                    if self.sliderSegmStats.value() >= 0:
                        y_axis = self.Image.voi_statistics_avg[self.sliderSegmStats.value()][subI[0]:subI[1]]
                        error = self.Image.voi_statistics_std[self.sliderSegmStats.value()][subI[0]:subI[1]]
            if self.showFocus:
                self.TACImage.axes.axvline(self.Image.time[values[0]],color='r')
            if self.showSubImage:
                self.TACImage.axes.axvline(x_axis[self.parameters.subImage[0,0]],color='y')
                try:
                    self.TACImage.axes.axvline(self.Image.time[self.parameters.subImage[0,1]],color='y')
                except:
                    self.TACImage.axes.axvline(self.Image.time[-1],color='y')
            try:
                self.TACImage.axes.plot(x_axis,error/y_axis*100,color='b',label="Ratio")
            except: pass
            self.base_Ratio_axes()
            self.TACImage.draw()
            self.switch_bottom_view()
        except:
            pass
    def update_Bayesian(self,param:int=0):
        """Shows the Bayesian coefficients in the middle image"""
        try:
            if param == -1:
                k = np.arange(self.Image.bayesian_results_avg.shape[1])
            else:
                k = np.array([param])
            try:
                self.TACImage.fig.delaxes(self.axTAC)
            except:
                pass
            self.TACImage.axes.cla()
            for i in range(k.shape[0]):
                self.TACImage.axes.errorbar(np.arange(self.Image.bayesian_results_avg.shape[0]),
                                                self.Image.bayesian_results_avg[:,k[i]],
                                                yerr=[self.Image.bayesian_results_e_down[:,k[i]],self.Image.bayesian_results_e_up[:,k[i]]])
            self.base_Bayesian_axes()
            self.TACImage.draw() 
        except:
            pass
    def update_BayesianPlots(self):
        """Shows the Summary Plots of the Dynesty analyses"""
        try:
            key = int(self.sliderFitted.value())
            if key < 0 or key >= self.Image.bayesian_dynesty_counter:
                key = 0
            try: 
                del self.GraphRunPlot
                del self.GraphTracePlot
                del self.GraphRunPlot
            except: pass
            if self.Image.bayesian_dynesty_counter != 0:
                self.switch_bottom_view(current = "Bayesian")

                figRun = self.Image.bayesian_graphs_runplot[f"{key}"]
                self.GraphRunPlot = FigureCanvasQTAgg(figRun)
                self.GraphRunPlot.setMinimumSize(size_Image,size_Image)
                del figRun

                figTrace = self.Image.bayesian_graphs_traceplot[f"{key}"]
                self.GraphTracePlot = FigureCanvasQTAgg(figTrace)
                self.GraphTracePlot.setMinimumSize(size_Image,size_Image)
                del figTrace

                figCorner = self.Image.bayesian_graphs_cornerplot[f"{key}"]
                self.GraphCornerPlot = FigureCanvasQTAgg(figCorner)
                self.GraphCornerPlot.setMinimumSize(size_Image,size_Image)
                del figCorner

                self.generalLayout.addWidget(self.GraphCornerPlot,self.lineImage1D,3)
                self.generalLayout.addWidget(self.GraphRunPlot,self.lineImage1D,1)
                self.generalLayout.addWidget(self.GraphTracePlot,self.lineImage1D,2)

                self.BayesianShown = True
                del key
        except: pass
 
    def switch_bottom_view(self,current:str=""):
        """Changes the bottom view to line signal or Bayesian results.\n
        This part removes the current images, leaving the space empty"""
        if current == "Bayesian":
            try: 
                self.generalLayout.removeWidget(self.GraphRunPlot)
                self.generalLayout.removeWidget(self.GraphTracePlot)
                self.generalLayout.removeWidget(self.GraphCornerPlot)
                self.GraphRunPlot.deleteLater()
                self.GraphTracePlot.deleteLater()
                self.GraphCornerPlot.deleteLater()
                self.GraphRunPlot = None
                self.GraphTracePlot = None
                self.GraphCornerPlot = None
            except: pass
            if not self.BayesianShown:
                self.generalLayout.removeWidget(self.AxialImage1D)
                self.generalLayout.removeWidget(self.CoronalImage1D)
                self.generalLayout.removeWidget(self.SagittalImage1D)
                self.AxialImage1D.deleteLater()
                self.CoronalImage1D.deleteLater()
                self.SagittalImage1D.deleteLater()
                self.AxialImage1D = None
                self.CoronalImage1D = None
                self.SagittalImage1D = None
        else:
            if self.BayesianShown:
                self.generalLayout.removeWidget(self.GraphRunPlot)
                self.generalLayout.removeWidget(self.GraphTracePlot)
                self.generalLayout.removeWidget(self.GraphCornerPlot)
                self.GraphRunPlot.deleteLater()
                self.GraphTracePlot.deleteLater()
                self.GraphCornerPlot.deleteLater()
                self.GraphRunPlot = None
                self.GraphTracePlot = None
                self.GraphCornerPlot = None  
                del self.GraphRunPlot
                del self.GraphTracePlot
                del self.GraphCornerPlot

                self._create1DImage()              
    def update_TAC_slice(self):
        """
        Update the 1D TAC image, in the bottom of the GUI, according to the position of the sliders sliders.\n
        This TAC will only be for a slice of the image, each image being for a spatial dimension.\n
        If a subimage view is selected, it will zoom upon the subregion.\n
        These views are 1D and go along 1 spatial axis.\n
        For the 1D spatial axes, see update_1D function.
        """
        try:
            self.AxialImage1D.axes.cla()
            self.SagittalImage1D.axes.cla()
            self.CoronalImage1D.axes.cla()
            values = [self.sliderAcq.value(),self.sliderAxial.value(),self.sliderCoronal.value(),self.sliderSagittal.value()]
            key = self.sliderSegm.value()

            x_axis = self.Image.time
            self.AxialImage1D.axes.plot(x_axis,np.sum(self.Image.Image[:,:,values[2],
                                                        values[3]]*self.Image.voi[f"{key}"][:,values[2],values[3]]/np.sum(self.Image.voi[f"{key}"][:,values[2],values[3]]),axis = 1))
            self.SagittalImage1D.axes.plot(x_axis,np.sum(self.Image.Image[:,values[1],
                                                        values[2],:]*self.Image.voi[f"{key}"][values[1],values[2],:]/np.sum(self.Image.voi[f"{key}"][values[1],values[2],:]),axis=1))
            self.CoronalImage1D.axes.plot(x_axis,np.sum(self.Image.Image[:,values[1],:,
                                            values[3]]*self.Image.voi[f"{key}"][values[1],:,values[3]]/np.sum(self.Image.voi[f"{key}"][values[1],:,values[3]]),axis=1))

            if self.showFocus:
                self.AxialImage1D.axes.axvline(self.Image.time[values[0]],color='r')
                self.SagittalImage1D.axes.axvline(self.Image.time[values[0]],color='r')
                self.CoronalImage1D.axes.axvline(self.Image.time[values[0]],color='r')
            if self.showSubImage:
                self.AxialImage1D.axes.axvline(x_axis[self.parameters.subImage[0,0]],color='y')
                try:
                    self.AxialImage1D.axes.axvline(self.Image.time[self.parameters.subImage[0,1]],color='y')
                except:
                    self.AxialImage1D.axes.axvline(self.Image.time[-1],color='y')
                self.SagittalImage1D.axes.axvline(x_axis[self.parameters.subImage[0,0]],color='y')
                try: 
                    self.SagittalImage1D.axes.axvline(self.Image.time[self.parameters.subImage[0,1]],color='y')
                except: 
                    self.SagittalImage1D.axes.axvline(self.Image.time[-1],color='y')
                self.CoronalImage1D.axes.axvline(x_axis[self.parameters.subImage[0,0]],color='y')
                try:
                    self.CoronalImage1D.axes.axvline(self.Image.time[self.parameters.subImage[0,1]],color='y')
                except:
                    self.CoronalImage1D.axes.axvline(self.Image.time[-1],color='y')

            self.base_1D_TACs_axes()
            self.AxialImage1D.draw()
            self.SagittalImage1D.draw()
            self.CoronalImage1D.draw()

        except:
            pass
    def update_TAC(self):
        """
        Update the 1D TAC image, in the middle of the GUI, according to the position of the sliders sliders.\n
        If a subimage view is selected, it will zoom upon the subregion.\n
        These views are 1D and go along 1 spatial axis.\n
        For the 1D spatial axes, see update_1D function.
        """
        try:
            if self.resultView in ["TAC Total","TAC Cumulative Total"]:
                factorSeg = self.Image.voi_voxels[self.sliderSegm.value()]
                factorErr = self.Image.voi_voxels[self.sliderSegmStats.value()]
                factorBay = self.Image.voi_voxels[self.sliderFitted.value()]
            else:
                factorSeg = 1
                factorErr = 1
                factorBay = 1
            try:
                if self.sliderFitted.value() > 0:
                    if self.parameters.ModelBayesian == "2_Comp_A1":
                        model = self.Image.model_three_compartment_A1
                    elif self.parameters.ModelBayesian == "2_Comp_A2":
                        model = self.Image.model_three_compartment_A2
                    elif self.parameters.ModelBayesian == "2_Comp_A2_Pause":
                        model = self.Image.model_three_compartment_A2_pause
                    else:
                        model = self.Image.model_three_compartment_A2
            except: pass
            try:
                self.TACImage.fig.delaxes(self.axTAC)
            except:
                pass
            self.TACImage.axes.cla()
            values = [self.sliderAcq.value(),self.sliderAxial.value(),self.sliderCoronal.value(),self.sliderSagittal.value()]
            subI = self.parameters.subImage[0,:]
            if self.view_range == "All":
                x_axis = self.Image.time
                if self.sliderSegm.value() >= 0 or self.sliderSegmStats.value() >= 0 or self.sliderFitted.value() >= 0:
                    if self.sliderSegm.value() >= 0:
                        y_axis = self.Image.voi_statistics[self.sliderSegm.value()] * factorSeg
                    if self.sliderSegmStats.value() >= 0:
                        y_axis2 = self.Image.voi_statistics_avg[self.sliderSegmStats.value()] * factorErr
                        error = self.Image.voi_statistics_std[self.sliderSegmStats.value()] * factorErr
                    if self.sliderFitted.value() > 0:
                        y_axis3 = model(x_axis,self.Image.bayesian_results_avg[self.sliderFitted.value(),:]) * factorBay
                else:
                    y_axis = self.Image.Image[:,values[1],values[2],values[3]]
            else:
                x_axis = self.Image.time[subI[0]:subI[1]]
                if self.sliderSegm.value() >= 0 or self.sliderSegmStats.value() >= 0:
                    if self.sliderSegm.value() >= 0:
                        y_axis = self.Image.voi_statistics[self.sliderSegm.value()][subI[0]:subI[1]] * factorSeg
                    if self.sliderSegmStats.value() >= 0:
                        y_axis2 = self.Image.voi_statistics_avg[self.sliderSegmStats.value()][subI[0]:subI[1]] * factorErr
                        error = self.Image.voi_statistics_std[self.sliderSegmStats.value()][subI[0]:subI[1]] * factorErr
                    if self.sliderFitted.value() > 0:
                        y_axis3 = model(x_axis,self.Image.bayesian_results_avg[self.sliderFitted.value(),:])[subI[0]:subI[1]] * factorBay
                else:
                    y_axis = self.Image.Image[:,values[1],values[2],values[3]][subI[0]:subI[1]]
            if self.showFocus:
                self.TACImage.axes.axvline(self.Image.time[values[0]],color='r')
            if self.showSubImage:
                self.TACImage.axes.axvline(x_axis[self.parameters.subImage[0,0]],color='y')
                try:
                    self.TACImage.axes.axvline(self.Image.time[self.parameters.subImage[0,1]],color='y')
                except:
                    self.TACImage.axes.axvline(self.Image.time[-1],color='y')
            try:
                if self.resultView in ["TAC Cumulative","TAC Cumulative Total"]:
                    tmp = np.zeros(x_axis.shape[0])
                    for i in range(tmp.shape[0]):
                        tmp[i] = scipy.integrate.trapezoid(y_axis[:i],x = x_axis[:i])
                    y_axis = tmp
                self.TACImage.axes.plot(x_axis,y_axis,color='b',label="TAC")
            except: pass
            try:
                if self.resultView in ["TAC Cumulative","TAC Cumulative Total"]:
                    tmp = np.zeros(x_axis.shape[0])
                    tmp_err = np.zeros(x_axis.shape[0])
                    for i in range(tmp.shape[0]):
                        tmp[i] = scipy.integrate.trapezoid(y_axis2[:i],x = x_axis[:i])
                        tmp_err[i] = scipy.integrate.trapezoid(error[:i],x = x_axis[:i])
                    y_axis2 = tmp
                    error = tmp_err
                self.TACImage.axes.errorbar(x_axis,y_axis2,error,color='r',label="Error TAC")
            except: pass
            try:
                if self.resultView in ["TAC Cumulative","TAC Cumulative Total"]:
                    tmp = np.zeros(x_axis.shape[0])
                    for i in range(tmp.shape[0]):
                        tmp[i] = scipy.integrate.trapezoid(y_axis3[:i],x = x_axis[:i])
                    y_axis3 = tmp
                self.TACImage.axes.plot(x_axis,y_axis3,color='g',label="Fit")
            except: pass
            self.base_TAC_axes()
            self.TACImage.draw()    
            self.switch_bottom_view()            
        except:
            pass
    def update_1D(self):
        """
        Update the 1D images, at the bottom of the GUI, according to the position of the three sliders.\n
        If a subimage view is selected, it will zoom upon the subregion.\n
        These views are 1D and go along 1 spatial axis.\n
        For the 1D temporal axis, see update_TAC function.
        """

        try:
            self.AxialImage1D.axes.cla()
            self.SagittalImage1D.axes.cla()
            self.CoronalImage1D.axes.cla()

            if self.resultImageType in ["Physical: Base Image"]:
                sliceAxis = self.Image.sliceAxis
                widthAxis = self.Image.widthAxis
                lengthAxis = self.Image.lengthAxis
            else:
                sliceAxis = np.arange(self.Image.nb_slice)
                widthAxis = np.arange(self.Image.width)
                lengthAxis = np.arange(self.Image.length)

            values = [self.sliderAcq.value(),self.sliderAxial.value(),self.sliderCoronal.value(),self.sliderSagittal.value()]
            if self.view_range == "All":
                self.AxialImage1D.axes.plot(sliceAxis,self.Image.Image[values[0],:,values[2],values[3]])
                self.SagittalImage1D.axes.plot(lengthAxis,self.Image.Image[values[0],values[1],values[2],:])
                self.CoronalImage1D.axes.plot(widthAxis,self.Image.Image[values[0],values[1],:,values[3]])
                if self.showSuperpose:
                    S1 = np.where(self.Image.voi[f"{self.sliderSegm.value()}"][:,values[2],values[3]]>0.5,1,np.nan)
                    S2 = np.where(self.Image.voi[f"{self.sliderSegm.value()}"][values[1],values[2],:]>0.5,1,np.nan)
                    S3 = np.where(self.Image.voi[f"{self.sliderSegm.value()}"][values[1],:,values[3]]>0.5,1,np.nan)
                    self.AxialImage1D.axes.fill_between(sliceAxis,
                                                        self.Image.Image[values[0],:,values[2],values[3]]*S1)
                    self.SagittalImage1D.axes.fill_between(lengthAxis,
                                                        self.Image.Image[values[0],values[1],values[2],:]*S2)
                    self.CoronalImage1D.axes.fill_between(widthAxis,
                                                        self.Image.Image[values[0],values[1],:,values[3]]*S3)
            else:
                subI = self.parameters.subImage
                self.AxialImage1D.axes.plot(sliceAxis[int(subI[1,0]):int(subI[1,1]+1)],self.Image.Image[values[0],subI[1,0]:subI[1,1]+1,values[2],values[3]])
                self.SagittalImage1D.axes.plot(lengthAxis[int(subI[3,0]):int(subI[3,1]+1)],self.Image.Image[values[0],values[1],values[2],subI[3,0]:subI[3,1]+1])
                self.CoronalImage1D.axes.plot(widthAxis[int(subI[2,0]):int(subI[2,1]+1)],self.Image.Image[values[0],values[1],subI[2,0]:subI[2,1]+1,values[3]])
                if self.showSuperpose:
                    S1 = np.where(self.Image.voi[f"{self.sliderSegm.value()}"][subI[1,0]:subI[1,1]+1,values[2],values[3]]>0.5,1,np.nan)
                    S2 = np.where(self.Image.voi[f"{self.sliderSegm.value()}"][values[1],values[2],subI[3,0]:subI[3,1]+1]>0.5,1,np.nan)
                    S3 = np.where(self.Image.voi[f"{self.sliderSegm.value()}"][values[1],subI[2,0]:subI[2,1]+1,values[3]]>0.5,1,np.nan)
                    #A1 = self.Image.Image[values[0],subI[1,0]:subI[1,1]+1,values[2],values[3]]
                    self.AxialImage1D.axes.fill_between(sliceAxis[int(subI[1,0]):int(subI[1,1]+1)],
                                                        self.Image.Image[values[0],subI[1,0]:subI[1,1]+1,values[2],values[3]]*S1)
                    self.SagittalImage1D.axes.fill_between(lengthAxis[int(subI[3,0]):int(subI[3,1]+1)],
                                                        self.Image.Image[values[0],values[1],values[2],subI[3,0]:subI[3,1]+1]*S2)
                    self.CoronalImage1D.axes.fill_between(widthAxis[int(subI[2,0]):int(subI[2,1]+1)],
                                                        self.Image.Image[values[0],values[1],subI[2,0]:subI[2,1]+1,values[3]]*S3) 
            if self.showFocus:
                self.AxialImage1D.axes.axvline(sliceAxis[int(values[1])],color='r')
                self.SagittalImage1D.axes.axvline(lengthAxis[int(values[3])],color='r')
                self.CoronalImage1D.axes.axvline(widthAxis[int(values[2])],color='r')
            if self.showSubImage:
                self.AxialImage1D.axes.axvline(sliceAxis[int(self.parameters.subImage[1,0])],color='y')
                self.AxialImage1D.axes.axvline(sliceAxis[int(self.parameters.subImage[1,1])],color='y')
                self.SagittalImage1D.axes.axvline(lengthAxis[int(self.parameters.subImage[3,0])],color='y')
                self.SagittalImage1D.axes.axvline(lengthAxis[int(self.parameters.subImage[3,1])],color='y')
                self.CoronalImage1D.axes.axvline(widthAxis[int(self.parameters.subImage[2,0])],color='y')
                self.CoronalImage1D.axes.axvline(widthAxis[int(self.parameters.subImage[2,1])],color='y')

            self.base_1D_axes()
            self.AxialImage1D.draw()
            self.SagittalImage1D.draw()
            self.CoronalImage1D.draw()
        except:
            pass
    def update_sliders(self):
        """Updates the size of the sliders for the image depending on the view type and the size of the subImage parameters"""
        if self.view_range == "All":
            self.sliderAcq.setMinimum(0);self.sliderAcq.setMaximum(self.Image.nb_acq-1)
            self.sliderAxial.setMinimum(0);self.sliderAxial.setMaximum(self.Image.nb_slice-1)
            self.sliderSagittal.setMinimum(0);self.sliderSagittal.setMaximum(self.Image.length-1)
            self.sliderCoronal.setMinimum(0);self.sliderCoronal.setMaximum(self.Image.width-1)
        else:
            subI = self.parameters.subImage
            self.sliderAcq.setMinimum(subI[0,0]);self.sliderAcq.setMaximum(subI[0,1])
            self.sliderAxial.setMinimum(subI[1,0]);self.sliderAxial.setMaximum(subI[1,1])
            self.sliderSagittal.setMinimum(subI[3,0]);self.sliderSagittal.setMaximum(subI[3,1])
            self.sliderCoronal.setMinimum(subI[2,0]);self.sliderCoronal.setMaximum(subI[2,1])
    def base_TAC_axes(self):
        """Gives the basic axes details for the result image (center) when they are updated when it is a TAC (error or not)"""
        try:
            self.cb.remove()
        except: pass
        self.TACImage.axes.set_title("TAC");self.TACImage.axes.grid()
        self.TACImage.axes.set_xlabel("Time");self.TACImage.axes.set_ylabel("Signal")
        try:
            if self.sliderSegm.value() >= 0 and self.sliderSegmStats.value() >= 0:
                self.TACImage.axes.legend()
        except: pass
    def base_Ratio_axes(self):
        """Gives the basic axes details for the result image (center) when they are updated when it is a ratio for the error"""
        try:
            self.cb.remove()
        except: pass
        self.TACImage.axes.set_title("Ratio of Error/TAC");self.TACImage.axes.grid()
        self.TACImage.axes.set_xlabel("Time");self.TACImage.axes.set_ylabel("Ratio")
        try:
            if self.sliderSegm.value() >= 0 and self.sliderSegmStats.value() >= 0:
                self.TACImage.axes.legend()
        except: pass

    def base_coeff_axes(self,mappable):
        """Gives the basic axes details for the result image (center) when they are updated when it is Dice or Jaccard"""
        try:
            self.cb.remove()
        except: pass
        self.TACImage.axes.set_title(self.resultView)
        self.cb = self.TACImage.fig.colorbar(mappable)
    def base_Bayesian_axes(self):
        """Gives the basic axes details for the result image (center) when they are updated for the Bayesian analyses"""
        try:
            self.cb.remove()
        except: pass
        self.TACImage.axes.set_title(self.resultView)
        self.TACImage.axes.grid()
    def base_1D_axes(self):
        """Sets the basic axes of the 1D slices images (at the bottom)"""
        self.AxialImage1D.axes.set_title("Axial Slice");self.AxialImage1D.axes.grid()
        self.AxialImage1D.axes.set_xlabel("Voxel");self.AxialImage1D.axes.set_ylabel("Signal")
        self.SagittalImage1D.axes.set_title("Sagittal Slice");self.SagittalImage1D.axes.grid()
        self.SagittalImage1D.axes.set_xlabel("Voxel");self.SagittalImage1D.axes.set_ylabel("Signal")
        self.CoronalImage1D.axes.set_title("Coronal Slice");self.CoronalImage1D.axes.grid()
        self.CoronalImage1D.axes.set_xlabel("Voxel");self.CoronalImage1D.axes.set_ylabel("Signal")
    def base_1D_TACs_axes(self):
        """Sets the basic axes of the 1D slices TACs (at the bottom"""
        self.AxialImage1D.axes.set_title("Axial TAC");self.AxialImage1D.axes.grid()
        self.AxialImage1D.axes.set_xlabel("Time");self.AxialImage1D.axes.set_ylabel("Signal")
        self.SagittalImage1D.axes.set_title("Sagittal TAC");self.SagittalImage1D.axes.grid()
        self.SagittalImage1D.axes.set_xlabel("Time");self.SagittalImage1D.axes.set_ylabel("Signal")
        self.CoronalImage1D.axes.set_title("Coronal TAC");self.CoronalImage1D.axes.grid()
        self.CoronalImage1D.axes.set_xlabel("Time");self.CoronalImage1D.axes.set_ylabel("Signal")        
    def update_view(self):
        """Updates the top images (2D views) according to the parameters input and the determined view requested"""
        try:
            values = [self.sliderAcq.value(),self.sliderAxial.value(),self.sliderCoronal.value(),self.sliderSagittal.value()]
        except: pass
        try: SubI = self.parameters.subImage
        except: pass
        if self.resultImageType in ["Physical: Base Image", "Physical: Combined","Physical: CT"]:
            sliceAxis = self.Image.sliceAxis
            widthAxis = self.Image.widthAxis
            lengthAxis = self.Image.lengthAxis
        else:
            sliceAxis = np.arange(self.Image.nb_slice)
            widthAxis = np.arange(self.Image.width)
            lengthAxis = np.arange(self.Image.length)

        if self.resultImageType == "Physical: Combined":
            alphaValueImage = self.parameters.AlphaCombined
        else:
            alphaValueImage = 1

        if self.showLog:
            def a(x):
                return np.log(x+1)
        else:
            def a(x):
                return x
        func = a

        #if SubI[0,0] >= SubI[0,1] or SubI[1,0] >= SubI[1,1] or SubI[2,0] >= SubI[2,1] or SubI[3,0] >= SubI[3,1]:
        #    self._createErrorMessage("Wrong subimage. Check to be sure that the values are in the good order")
        key = self.sliderSegm.value()
        try:
            self.axial.axes.cla()
            self.sagittal.axes.cla()
            self.coronal.axes.cla()
        except: pass
        try:
            if self.showFocus:
                self.axial.axes.plot(lengthAxis[int(values[3])],widthAxis[values[2]],'*',markersize = 6,color='y')
                self.sagittal.axes.plot(widthAxis[values[2]],sliceAxis[values[1]],'*',markersize = 6,color='y')
                self.coronal.axes.plot(lengthAxis[int(values[3])],sliceAxis[values[1]],'*',markersize = 6,color='y')
                self.axial.axes.axhline(widthAxis[values[2]],color='r')
                self.axial.axes.axvline(lengthAxis[int(values[3])],color='r')
                self.sagittal.axes.axhline(sliceAxis[values[1]],color='r')
                self.sagittal.axes.axvline(widthAxis[values[2]],color='r')
                self.coronal.axes.axhline(sliceAxis[values[1]],color='r')
                self.coronal.axes.axvline(lengthAxis[int(values[3])],color='r')
        except: pass
        try:
            if self.showSubImage:
                self.axial.axes.axhline(widthAxis[int(self.parameters.subImage[2,0])],color='y')
                self.axial.axes.axhline(widthAxis[int(self.parameters.subImage[2,1])],color='y')
                self.sagittal.axes.axhline(sliceAxis[int(self.parameters.subImage[1,0])],color='y')
                self.sagittal.axes.axhline(sliceAxis[int(self.parameters.subImage[1,1])],color='y')
                self.coronal.axes.axhline(sliceAxis[int(self.parameters.subImage[1,0])],color='y')
                self.coronal.axes.axhline(sliceAxis[int(self.parameters.subImage[1,1])],color='y')
                self.axial.axes.axvline(lengthAxis[int(self.parameters.subImage[3,0])],color='y')
                self.axial.axes.axvline(lengthAxis[int(self.parameters.subImage[3,1])],color='y')
                self.sagittal.axes.axvline(widthAxis[int(self.parameters.subImage[2,0])],color='y')
                self.sagittal.axes.axvline(widthAxis[int(self.parameters.subImage[2,1])],color='y')
                self.coronal.axes.axvline(lengthAxis[int(self.parameters.subImage[3,0])],color='y')
                self.coronal.axes.axvline(lengthAxis[int(self.parameters.subImage[3,1])],color='y')
        except: pass

        #Second Image to be Seen
        try:
            if self.resultImageType in ["Physical: CT","Physical: Combined","Array: CT"]:
                if self.resultImageType == "Array: CT":
                    sliceAxis2 = np.arange(self.Image2.nb_slice)
                    widthAxis2 = np.arange(self.Image2.width)
                    lengthAxis2 = np.arange(self.Image2.length)
                else:
                    sliceAxis2 = self.Image2.sliceAxis
                    widthAxis2 = self.Image2.widthAxis
                    lengthAxis2 = self.Image2.lengthAxis                
                #Find closest index for each point on the axis:
                value1 = (np.abs(self.Image2.sliceAxis - sliceAxis[values[1]])).argmin()
                value2 = (np.abs(self.Image2.widthAxis - widthAxis[values[2]])).argmin()
                value3 = (np.abs(self.Image2.lengthAxis - lengthAxis[values[3]])).argmin()
                if self.view == "Slice":
                    LAxis2 = lengthAxis2
                    WAxis2 = widthAxis2
                    SAxis2 = sliceAxis2
                    if self.parameters.ImagesCombinedMethod == "Closest Neighbour":
                        LWImage2 = func(self.Image2.Image[0,value1,:,:])
                        WSImage2 = func(self.Image2.Image[0,:,:,value2])
                        LSImage2 = func(self.Image2.Image[0,:,value3,:])
                    elif self.parameters.ImagesCombinedMethod == "Linear Interpolation":
                        if self.Image2.sliceAxis[value1] > sliceAxis[values[1]]:
                            fraction1_under = np.abs(self.Image2.sliceAxis[value1] - sliceAxis[values[1]])/(self.Image2.sliceAxis[1]-self.Image2.sliceAxis[0])
                            fraction1_over = np.abs(self.Image2.sliceAxis[value1+1] - sliceAxis[values[1]])/(self.Image2.sliceAxis[1]-self.Image2.sliceAxis[0])
                            LWImage2 = fraction1_under * func(self.Image2.Image[0,value1,:,:]) + fraction1_over * func(self.Image2.Image[0,value1+1,:,:])
                        else:
                            fraction1_over = np.abs(self.Image2.sliceAxis[value1] - sliceAxis[values[1]])/(self.Image2.sliceAxis[1]-self.Image2.sliceAxis[0])
                            fraction1_under = np.abs(self.Image2.sliceAxis[value1-1] - sliceAxis[values[1]])/(self.Image2.sliceAxis[1]-self.Image2.sliceAxis[0])
                            LWImage2 = fraction1_under * func(self.Image2.Image[0,value1-1,:,:]) + fraction1_over * func(self.Image2.Image[0,value1,:,:])
                        if self.Image2.widthAxis[value1] > widthAxis[values[1]]:
                            fraction2_under = np.abs(self.Image2.widthAxis[value1] - widthAxis[values[1]])/(self.Image2.widthAxis[1]-self.Image2.widthAxis[0])
                            fraction2_over = np.abs(self.Image2.widthAxis[value1+1] - widthAxis[values[1]])/(self.Image2.widthAxis[1]-self.Image2.widthAxis[0])
                            WSImage2 = fraction2_under * func(self.Image2.Image[0,:,:,value2]) + fraction2_over * func(self.Image2.Image[0,:,:,value2+1])
                        else:
                            fraction2_over = np.abs(self.Image2.widthAxis[value1] - widthAxis[values[1]])/(self.Image2.widthAxis[1]-self.Image2.widthAxis[0])
                            fraction2_under = np.abs(self.Image2.widthAxis[value1-1] - widthAxis[values[1]])/(self.Image2.widthAxis[1]-self.Image2.widthAxis[0])
                            WSImage2 = fraction2_under * func(self.Image2.Image[0,:,:,value2-1]) + fraction2_over * func(self.Image2.Image[0,:,:,value2])
                        if self.Image2.lengthAxis[value1] > lengthAxis[values[1]]:
                            fraction3_under = np.abs(self.Image2.lengthAxis[value1] - lengthAxis[values[1]])/(self.Image2.lengthAxis[1]-self.Image2.lengthAxis[0])
                            fraction3_over = np.abs(self.Image2.lengthAxis[value1+1] - lengthAxis[values[1]])/(self.Image2.lengthAxis[1]-self.Image2.lengthAxis[0])
                            LSImage2 = fraction3_under * func(self.Image2.Image[0,:,value3,:]) + fraction3_over * func(self.Image2.Image[0,:,value3+1,:])
                        else:
                            fraction3_over = np.abs(self.Image2.lengthAxis[value1] - lengthAxis[values[1]])/(self.Image2.lengthAxis[1]-self.Image2.lengthAxis[0])
                            fraction3_under = np.abs(self.Image2.lengthAxis[value1-1] - lengthAxis[values[1]])/(self.Image2.lengthAxis[1]-self.Image2.lengthAxis[0])
                            LSImage2 = fraction3_under * func(self.Image2.Image[0,:,value3-1,:]) + fraction3_over * func(self.Image2.Image[0,:,value3,:])


                elif self.view == "Sub. Slice":
                    subImage2 = np.zeros_like(SubI)
                    subImage2[1,0] = (np.abs(self.Image2.sliceAxis - sliceAxis[SubI[1,0]])).argmin()
                    subImage2[1,1] = (np.abs(self.Image2.sliceAxis - sliceAxis[SubI[1,1]])).argmin()
                    subImage2[2,0] = (np.abs(self.Image2.widthAxis - widthAxis[SubI[2,0]])).argmin()
                    subImage2[2,1] = (np.abs(self.Image2.widthAxis - widthAxis[SubI[2,1]])).argmin()
                    subImage2[3,0] = (np.abs(self.Image2.lengthAxis - lengthAxis[SubI[3,0]])).argmin()
                    subImage2[3,1] = (np.abs(self.Image2.lengthAxis - lengthAxis[SubI[3,1]])).argmin()
                    subCopy = np.copy(subImage2)
                    try:
                        while sliceAxis2[subImage2[1,0]] > sliceAxis[SubI[1,0]]: subImage2[1,0] += 1
                        while sliceAxis2[subImage2[1,1]] < sliceAxis[SubI[1,1]]: subImage2[1,1] -= 1
                        while widthAxis2[subImage2[2,0]] > widthAxis[SubI[2,0]]: subImage2[2,0] += 1
                        while widthAxis2[subImage2[2,1]] < widthAxis[SubI[2,1]]: subImage2[2,1] -= 1
                        while lengthAxis2[subImage2[3,0]] > lengthAxis[SubI[3,0]]: subImage2[3,0] += 1
                        while lengthAxis2[subImage2[3,1]] < lengthAxis[SubI[3,1]]: subImage2[3,1] -= 1
                    except:
                        subImage2 = np.copy(subCopy)
                        while sliceAxis2[subImage2[1,0]] < sliceAxis[SubI[1,0]]: subImage2[1,0] += 1
                        while sliceAxis2[subImage2[1,1]] > sliceAxis[SubI[1,1]]: subImage2[1,1] -= 1
                        while widthAxis2[subImage2[2,0]] < widthAxis[SubI[2,0]]: subImage2[2,0] += 1
                        while widthAxis2[subImage2[2,1]] > widthAxis[SubI[2,1]]: subImage2[2,1] -= 1
                        while lengthAxis2[subImage2[3,0]] < lengthAxis[SubI[3,0]]: subImage2[3,0] += 1
                        while lengthAxis2[subImage2[3,1]] > lengthAxis[SubI[3,1]]: subImage2[3,1] -= 1
                    LAxis2 = lengthAxis2[int(subImage2[3,0]):int(subImage2[3,1])]
                    WAxis2 = widthAxis2[int(subImage2[2,0]):int(subImage2[2,1])]
                    SAxis2 = sliceAxis2[int(subImage2[1,0]):int(subImage2[1,1])]
                    if self.parameters.ImagesCombinedMethod == "Closest Neighbour":
                        LWImage2 = func(self.Image2.Image[0,value1,subImage2[2,0]:subImage2[2,1],subImage2[3,0]:subImage2[3,1]])
                        WSImage2 = func(self.Image2.Image[0,subImage2[1,0]:subImage2[1,1],subImage2[2,0]:subImage2[2,1],value2])
                        LSImage2 = func(self.Image2.Image[0,subImage2[1,0]:subImage2[1,1],value3,subImage2[3,0]:subImage2[3,1]])
                    elif self.parameters.ImagesCombinedMethod == "Linear Interpolation":
                        if self.Image2.sliceAxis[value1] > sliceAxis[values[1]]:
                            fraction1_under = np.abs(self.Image2.sliceAxis[value1] - sliceAxis[values[1]])/(self.Image2.sliceAxis[1]-self.Image2.sliceAxis[0])
                            fraction1_over = np.abs(self.Image2.sliceAxis[value1+1] - sliceAxis[values[1]])/(self.Image2.sliceAxis[1]-self.Image2.sliceAxis[0])
                            LWImage2 = fraction1_under * func(self.Image2.Image[0,value1,subImage2[2,0]:subImage2[2,1],subImage2[3,0]:subImage2[3,1]]) + fraction1_over * func(self.Image2.Image[0,value1+1,subImage2[2,0]:subImage2[2,1],subImage2[3,0]:subImage2[3,1]])
                        else:
                            fraction1_over = np.abs(self.Image2.sliceAxis[value1] - sliceAxis[values[1]])/(self.Image2.sliceAxis[1]-self.Image2.sliceAxis[0])
                            fraction1_under = np.abs(self.Image2.sliceAxis[value1-1] - sliceAxis[values[1]])/(self.Image2.sliceAxis[1]-self.Image2.sliceAxis[0])
                            LWImage2 = fraction1_under * func(self.Image2.Image[0,value1-1,subImage2[2,0]:subImage2[2,1],subImage2[3,0]:subImage2[3,1]]) + fraction1_over * func(self.Image2.Image[0,value1,subImage2[2,0]:subImage2[2,1],subImage2[3,0]:subImage2[3,1]])
                        if self.Image2.widthAxis[value1] > widthAxis[values[1]]:
                            fraction2_under = np.abs(self.Image2.widthAxis[value1] - widthAxis[values[1]])/(self.Image2.widthAxis[1]-self.Image2.widthAxis[0])
                            fraction2_over = np.abs(self.Image2.widthAxis[value1+1] - widthAxis[values[1]])/(self.Image2.widthAxis[1]-self.Image2.widthAxis[0])
                            WSImage2 = fraction2_under * func(self.Image2.Image[0,subImage2[1,0]:subImage2[1,1],subImage2[2,0]:subImage2[2,1],value2]) + fraction2_over * func(self.Image2.Image[0,subImage2[1,0]:subImage2[1,1],subImage2[2,0]:subImage2[2,1],value2+1])
                        else:
                            fraction2_over = np.abs(self.Image2.widthAxis[value1] - widthAxis[values[1]])/(self.Image2.widthAxis[1]-self.Image2.widthAxis[0])
                            fraction2_under = np.abs(self.Image2.widthAxis[value1-1] - widthAxis[values[1]])/(self.Image2.widthAxis[1]-self.Image2.widthAxis[0])
                            WSImage2 = fraction2_under * func(self.Image2.Image[0,subImage2[1,0]:subImage2[1,1],subImage2[2,0]:subImage2[2,1],value2-1]) + fraction2_over * func(self.Image2.Image[0,subImage2[1,0]:subImage2[1,1],subImage2[2,0]:subImage2[2,1],value2])
                        if self.Image2.lengthAxis[value1] > lengthAxis[values[1]]:
                            fraction3_under = np.abs(self.Image2.lengthAxis[value1] - lengthAxis[values[1]])/(self.Image2.lengthAxis[1]-self.Image2.lengthAxis[0])
                            fraction3_over = np.abs(self.Image2.lengthAxis[value1+1] - lengthAxis[values[1]])/(self.Image2.lengthAxis[1]-self.Image2.lengthAxis[0])
                            LSImage2 = fraction3_under * func(self.Image2.Image[0,subImage2[1,0]:subImage2[1,1],value3,subImage2[3,0]:subImage2[3,1]]) + fraction3_over * func(self.Image2.Image[0,subImage2[1,0]:subImage2[1,1],value3+1,subImage2[3,0]:subImage2[3,1]])
                        else:
                            fraction3_over = np.abs(self.Image2.lengthAxis[value1] - lengthAxis[values[1]])/(self.Image2.lengthAxis[1]-self.Image2.lengthAxis[0])
                            fraction3_under = np.abs(self.Image2.lengthAxis[value1-1] - lengthAxis[values[1]])/(self.Image2.lengthAxis[1]-self.Image2.lengthAxis[0])
                            LSImage2 = fraction3_under * func(self.Image2.Image[0,subImage2[1,0]:subImage2[1,1],value3-1,subImage2[3,0]:subImage2[3,1]]) + fraction3_over * func(self.Image2.Image[0,subImage2[1,0]:subImage2[1,1],value3,subImage2[3,0]:subImage2[3,1]])

        except: pass

        if self.resultImageType in ["Array: Base Image","Physical: Base Image","Physical: Combined"]:
            if self.view == "Slice":
                try:
                    LAxis = lengthAxis
                    WAxis = widthAxis
                    SAxis = sliceAxis
                    LWImage = func(self.Image.Image[values[0],values[1],:,:])
                    WSImage = func(self.Image.Image[values[0],:,:,values[3]])
                    LSImage = func(self.Image.Image[values[0],:,values[2],:])
                    if self.showSuperpose:
                        top_value = np.max([np.max(self.Image.Image[values[0],:,:,:]*self.Image.voi[f"{key}"]),5])
                        A = np.where(self.Image.voi[f"{key}"]>0.5,top_value,np.nan)
                        LWSegmImage = A[values[1],:,:]
                        WSSegmImage = A[:,:,values[3]]
                        LSSegmImage = A[:,values[2],:]
                except:
                    pass
            elif self.view == "Flat":
                try:
                    LAxis = lengthAxis
                    WAxis = widthAxis
                    SAxis = sliceAxis
                    LWImage = func(self.Image.axial_flats[int(values[0]),:,:])
                    WSImage = func(self.Image.sagittal_flats[int(values[0]),:,:])
                    LSImage = func(self.Image.coronal_flats[int(values[0]),:,:])
                except:
                    self._createErrorMessage("Can't perform this. No image is loaded or the flats are not done")
            elif self.view == "Segm. Slice":
                try:
                    LAxis = lengthAxis
                    WAxis = widthAxis
                    SAxis = sliceAxis
                    LWImage = func(self.Image.voi[f"{key}"][values[1],:,:])
                    WSImage = func(self.Image.voi[f"{key}"][:,:,values[3]])
                    LSImage = func(self.Image.voi[f"{key}"][:,values[2],:])
                except:
                    self._createErrorMessage("Can't perform this. No segmentations are present")
            elif self.view == "Segm. Flat":
                try:
                    LAxis = lengthAxis
                    WAxis = widthAxis
                    SAxis = sliceAxis
                    LWImage = func(self.Image.axial_flat(counter=key))
                    WSImage = func(self.Image.sagittal_flat(counter=key))
                    LSImage = func(self.Image.coronal_flat(counter=key))
                except:
                    self._createErrorMessage("Can't perform this. No segmentations are present")
            elif self.view == "Sub. Slice":
                try:
                    LAxis = lengthAxis[int(SubI[3,0]):int(SubI[3,1])]
                    WAxis = widthAxis[int(SubI[2,0]):int(SubI[2,1])]
                    SAxis = sliceAxis[int(SubI[1,0]):int(SubI[1,1])]
                    LWImage = func(self.Image.Image[values[0],values[1],SubI[2,0]:SubI[2,1],SubI[3,0]:SubI[3,1]])
                    WSImage = func(self.Image.Image[values[0],SubI[1,0]:SubI[1,1],SubI[2,0]:SubI[2,1],values[3]])
                    LSImage = func(self.Image.Image[values[0],SubI[1,0]:SubI[1,1],values[2],SubI[3,0]:SubI[3,1]])
                    if self.showSuperpose: 
                        top_value = np.max([np.max(self.Image.Image[values[0],SubI[1,0]:SubI[1,1],SubI[2,0]:SubI[2,1],SubI[3,0]:SubI[3,1]]*self.Image.voi[f"{key}"][SubI[1,0]:SubI[1,1],SubI[2,0]:SubI[2,1],SubI[3,0]:SubI[3,1]]),5])
                        A = np.where(self.Image.voi[f"{key}"]>0.5,top_value,np.nan)
                        LWSegmImage = A[values[1],SubI[2,0]:SubI[2,1],SubI[3,0]:SubI[3,1]]
                        WSSegmImage = A[SubI[1,0]:SubI[1,1],SubI[2,0]:SubI[2,1],values[3]]
                        LSSegmImage = A[SubI[1,0]:SubI[1,1],values[2],SubI[3,0]:SubI[3,1]]
                except:
                    self._createErrorMessage("Can't perform this. No SubImage selected")
            elif self.view == "Sub. Flat":
                try:
                    LAxis = lengthAxis[int(SubI[3,0]):int(SubI[3,1])]
                    WAxis = widthAxis[int(SubI[2,0]):int(SubI[2,1])]
                    SAxis = sliceAxis[int(SubI[1,0]):int(SubI[1,1])]
                    LWImage = func(self.Image.axial_flat(acq=values[0])[SubI[2,0]:SubI[2,1],SubI[3,0]:SubI[3,1]])
                    WSImage = func(self.Image.sagittal_flat(acq=values[0])[SubI[1,0]:SubI[1,1],SubI[2,0]:SubI[2,1]])
                    LSImage = func(self.Image.coronal_flat(acq=values[0])[SubI[1,0]:SubI[1,1],SubI[3,0]:SubI[3,1]])
                except:
                    self._createErrorMessage("Can't perform this. No SubImage selected")
            elif self.view == "Segm. Sub. Slice":
                try:
                    LAxis = lengthAxis[int(SubI[3,0]):int(SubI[3,1])]
                    WAxis = widthAxis[int(SubI[2,0]):int(SubI[2,1])]
                    SAxis = sliceAxis[int(SubI[1,0]):int(SubI[1,1])]
                    LWImage = func(self.Image.voi[f"{key}"][values[1],SubI[2,0]:SubI[2,1],SubI[3,0]:SubI[3,1]])
                    WSImage = func(self.Image.voi[f"{key}"][SubI[1,0]:SubI[1,1],SubI[2,0]:SubI[2,1],values[3]])
                    LSImage = func(self.Image.voi[f"{key}"][SubI[1,0]:SubI[1,1],values[2],SubI[3,0]:SubI[3,1]])
                except:
                    self._createErrorMessage("Can't perform this. No SubImage selected or no segmentation done")
            elif self.view == "Segm. Sub. Flat":
                try:
                    LAxis = lengthAxis[int(SubI[3,0]):int(SubI[3,1])]
                    WAxis = widthAxis[int(SubI[2,0]):int(SubI[2,1])]
                    SAxis = sliceAxis[int(SubI[1,0]):int(SubI[1,1])]
                    LWImage = func(self.Image.axial_flat(counter=key)[SubI[2,0]:SubI[2,1],SubI[3,0]:SubI[3,1]])
                    WSImage = func(self.Image.sagittal_flat(counter=key)[SubI[1,0]:SubI[1,1],SubI[2,0]:SubI[2,1]])
                    LSImage = func(self.Image.coronal_flat(counter=key)[SubI[1,0]:SubI[1,1],SubI[3,0]:SubI[3,1]])
                except:
                    self._createErrorMessage("Can't perform this. No SubImage selected or no segmentation done")
        #Show 2nd Image
        try:
                    self.axial.axes.pcolormesh(LAxis2,WAxis2,LWImage2,shading='gouraud',cmap='gray')
                    self.sagittal.axes.pcolormesh(WAxis2,SAxis2,WSImage2,shading='gouraud',cmap='gray')
                    self.coronal.axes.pcolormesh(LAxis2,SAxis2,LSImage2,shading='gouraud',cmap='gray')
        except: pass
        #Show 1st Image
        try:
            self.axial.axes.pcolormesh(LAxis, WAxis, LWImage, shading = 'gouraud', alpha = alphaValueImage, cmap = self.parameters.ColourBaseImage)
            self.sagittal.axes.pcolormesh(WAxis, SAxis, WSImage, shading = 'gouraud', alpha = alphaValueImage, cmap = self.parameters.ColourBaseImage)
            self.coronal.axes.pcolormesh(LAxis, SAxis, LSImage, shading = 'gouraud', alpha = alphaValueImage, cmap = self.parameters.ColourBaseImage)
        except: pass
        #Show Segmentation
        try:
            self.axial.axes.pcolormesh(LAxis, WAxis, LWSegmImage,shading='gouraud',
                                       cmap= self.parameters.ColourSegmentationImage, vmin=0,vmax=top_value,
                                       alpha = self.parameters.AlphaSegmentation)
            self.sagittal.axes.pcolormesh(WAxis, SAxis, WSSegmImage,shading='gouraud',
                                          cmap= self.parameters.ColourSegmentationImage, vmin=0,vmax=top_value,
                                          alpha = self.parameters.AlphaSegmentation)
            self.coronal.axes.pcolormesh(LAxis, SAxis, LSSegmImage,shading='gouraud',
                                         cmap= self.parameters.ColourSegmentationImage, vmin=0,vmax=top_value,
                                         alpha = self.parameters.AlphaSegmentation)
        except:
            pass

        try:
            self.axial.draw()
            self.sagittal.draw()
            self.coronal.draw()
        except:
            pass
        self.update_sliders()

    def setDisplayText(self, text:str):
        """Set the display's text (unused, part of the basic model used)."""
        self.display.setText(text)
        self.display.setFocus()

    def workerDisplayStatus(self,update:list):
        """X"""
        try:
            try:
                self.displayStatus(action = update[0],time_i = update[1],what = update[2],perc = update[3])
            except:
                self.displayStatus(action = update[0],time_i = update[1],what = update[2])
        except:
            self.displayStatus(action = update[0],time_i = update[1])
        try:
            if update[4]:
                self.update_all()
        except: pass

    def workerDeformFinished(self):
        """Updates the sliders if necessary after a deformation"""
        if self.parameters.deformationType == "Switch Two":
            tmp = [self.sliderAxial.value(),self.sliderCoronal.value(),self.sliderSagittal.value()]
            if self.parameters.switchAxes == [1,2]:
                self.sliderAxial.setValue(int(tmp[1]))
                self.sliderCoronal.setValue(int(tmp[0]))
            elif self.parameters.switchAxes == [1,3]:
                self.sliderAxial.setValue(int(tmp[2]))
                self.sliderSagittal.setValue(int(tmp[0]))
            elif self.parameters.switchAxes == [2,3]:
                self.sliderCoronal.setValue(int(tmp[2]))
                self.sliderSagittal.setValue(int(tmp[1]))
            self.sliderAxial.setMinimum(0);self.sliderAxial.setMaximum(self.Image.nb_slice-1)
            self.sliderSagittal.setMinimum(0);self.sliderSagittal.setMaximum(self.Image.width-1)
            self.sliderCoronal.setMinimum(0);self.sliderCoronal.setMaximum(self.Image.length-1)

    def displayStatus(self,action:str="",time_i=time.time(),what:str = 'done', perc : float = 0):
        """Updates the display bar (far bottom)"""
        try:
            self.Image.progress_log = self.backupLogText
        except:
            pass
        if action != "":
            if what == 'done' or what == "":
                new_status = f"{action} done in {(time.time()-time_i):.2f} s at {time.strftime('%H:%M:%S')}"
            else:
                new_status = f"{action} started at {time.strftime('%H:%M:%S')}"
            self.statusBar.showMessage(new_status)
            try:
                if self.Image.progress_log == "":
                    self.Image.progress_log += new_status
                else:
                    self.Image.progress_log += "\n" + new_status
                self.logText.textCursor().insertHtml(new_status + '<br>')
            except: pass
        try:
            self.logText.setText(self.Image.progress_log)
        except: pass
        self.progressBar.setValue(int(perc))
        try:
            self.backupLogText = self.Image.progress_log
        except: 
            self.backupLogText = ""
    def displayText(self):
        """Get the display's text (unused, part of the basic model used)."""
        return self.display.text()

    def clearDisplay(self):
        """Clear the display (unused, part of the basic model used)."""
        self.setDisplayText("")
    def show_infos_acq(self):
        """Information showed when the info button is pressed"""
        a = f"""Name: {self.Image.name}<br>
                Description: {self.Image.Description}<br>
                Total Time: {self.Image.time[-1]:.2f}<br>
                Version: {self.Image.version}<br>
                Number of timeframes: {self.Image.nb_acq}<br>
                Number of slices: {self.Image.nb_slice}<br>
                Width: {self.Image.width}<br>
                Length: {self.Image.length}<br>
                Slice Thickness: {self.Image.voxel_thickness}<br>
                Pixel Width: {self.Image.voxel_width}<br>
                Pixel Length: {self.Image.voxel_length}<br>
                Mass: {self.Image.mass}<br>
                Units: {self.Image.units}<br>
                Radionucleide: {self.Image.radionuclide}<br>
                Radiopharmaceutical: {self.Image.radiopharmaceutical}<br>
                Dose: {self.Image.dose}<br>
                Segm.: {self.Image.voi_counter}<br>
                Segm. with Errors: {len(self.Image.voi_statistics_avg)}<br>
                Bayesian analyses: {self.Image.bayesian_counter}<br>
                """
        return a
    def on_button_clicked_infos(self):
        """Button to show the information if an image has been loaded"""
        try:
            self._createErrorMessage(self.show_infos_acq())
        except:
            self._createErrorMessage("No file uploaded")
    def extract_button(self,source:QLineEdit):
        """Extract command when the button is pressed according to the QLineEdit. 
            Will try both methods of extraction to see which one works.
            Fails if an image is already loaded."""
        initial = time.time()
        self.displayStatus("File extraction",what = 'starting' ,time_i = initial)

        try:
            a = self.Image.version
            which = "second"
        except:
            which = "first"
        try:
            self.threadExtract = QThread()
            self.workerExtract = WorkerExtraction(source = source, which = which)
            self.workerExtract.moveToThread(self.threadExtract)

            self.threadExtract.started.connect(self.workerExtract.extract)
            self.workerExtract.finished.connect(self.threadExtract.quit)
            self.workerExtract.finished.connect(self.workerExtract.deleteLater)
            self.threadExtract.finished.connect(self.threadExtract.deleteLater)
            self.workerExtract.progress.connect(self.workerDisplayStatus)
            self.workerExtract.error.connect(self._createErrorMessage)

            self.threadExtract.start()

            self.btn_extr.setEnabled(False)
            self.threadExtract.finished.connect(
                lambda: self.btn_extr.setEnabled(True)
            )
            self.workerExtract.extracted.connect(self.ImageExtracted)
        except: pass

    def ImageExtracted(self,GivenList:list):
        """Creates the Display and places things once the Image is extracted"""
        if GivenList[2] == "first":
            self.Image = GivenList[0]
            self.parameters = GivenList[1]
            self._createImageDisplay()
            self._createImageDisplayBars()
            self.displayStatus("Interface initialization", initial)
        elif GivenList[2] == "second":
            self.Image2 = GivenList[0]
        elif GivenList[2] == "param":
            self.parameters = GivenList[1]

    def WorkerTaskDone(self,GivenList:list):
        """Reupdates the Image and the parameters once the task is done,
        i.e. segmentation, noise, Bayesian, errors, or other"""
        self.Image = GivenList[0]
        self.parameters = GivenList[1]

    def load_button(self,source:QLineEdit):
        """Loads the image according to the given QLineEdit.
            Will fail if an image is already loaded."""
        initial = time.time()
        self.displayStatus("File loading",what = 'starting' ,time_i = initial)

        try:
            a = self.Image.version
            which = "second"
        except:
            which = "first"
        try:
            self.threadLoad = QThread()
            self.workerLoad = WorkerLoad(source = source, which = which)
            self.workerLoad.moveToThread(self.threadLoad)

            self.threadLoad.started.connect(self.workerLoad.load)
            self.workerLoad.finished.connect(self.threadLoad.quit)
            self.workerLoad.finished.connect(self.workerLoad.deleteLater)
            self.threadLoad.finished.connect(self.threadLoad.deleteLater)
            self.workerLoad.progress.connect(self.workerDisplayStatus)
            self.workerLoad.error.connect(self._createErrorMessage)

            self.threadLoad.start()

            self.btn_load.setEnabled(False)
            self.threadLoad.finished.connect(
                lambda: self.btn_load.setEnabled(True)
            )
            self.workerLoad.extracted.connect(self.ImageExtracted)
        except: pass

    def browse_button_directory(self,source:QLineEdit):
        """Depleted"""
        text =  QFileDialog.getExistingDirectory()
        source.setText(text+"/")
    def browse_button_file(self,source:QLineEdit):
        """Opens a browsing system and keeps the selected file (cannot select a folder)"""
        text = QFileDialog.getOpenFileName(self)
        try:
            if text[0][-4:] not in [".pkl",".nii"] and text[0][-7:] not in [".nii.gz"]:
                for i in range(len(text[0])-1,0,-1):
                    if text[0][i] == "/":
                        path = text[0][:i+1]
                        break
            else:
                path = text[0]
            source.setText(path)
        except: 
            pass
    def save_button(self,path:QLineEdit,path_name:QLineEdit):
        """Depleted"""
        initial = time.time()
        self.displayStatus("File saved", what = 'starting' ,time_i = initial)
        if path.text() == "" or path_name.text()=="":
            self._createErrorMessage("Empty path. Please specify where to save.")
        else:
            try:
                if path_name.text()[-4:] == ".pkl":
                    PF.pickle_save(self.Image,path.text()+path_name.text())
                else:
                    PF.pickle_save(self.Image,path.text()+path_name.text()+".pkl")
                self._createErrorMessage(f"Save successfull")
            except:
                self._createErrorMessage(f"Impossible to save to the desired folder")
        self.displayStatus("File saved", initial)  
    def onClick(self,event,which):
        if self.resultImageType in ["Physical: Base Image","Physical: CT","Physical: Combined"]:
            sliceAxis = self.Image.sliceAxis
            widthAxis = self.Image.widthAxis
            lengthAxis = self.Image.lengthAxis
        else:
            sliceAxis = np.arange(self.Image.nb_slice)
            widthAxis = np.arange(self.Image.width)
            lengthAxis = np.arange(self.Image.length)
        ix, iy = event.xdata, event.ydata
        #print (f'x = {ix}, y = {iy}')
        which.coords = []
        which.coords.append((ix, iy))
        if len(which.coords) == 2:
            which.fig.canvas.mpl_disconnect(self.cid)
        
        if which == self.axial:
            ix = int((np.abs(lengthAxis - ix)).argmin())
            iy = int((np.abs(widthAxis - iy)).argmin())
            self.sliderCoronalValue.setText(f"{int(iy)}")
            self.sliderSagittalValue.setText(f"{int(ix)}")
            self.sliderCoronal.setValue(int(iy))
            self.sliderSagittal.setValue(int(ix))
        elif which == self.sagittal:
            ix = int((np.abs(widthAxis - ix)).argmin())
            iy = int((np.abs(sliceAxis - iy)).argmin())
            self.sliderAxialValue.setText(f"{int(iy)}")
            self.sliderCoronalValue.setText(f"{int(ix)}")
            self.sliderAxial.setValue(int(iy))
            self.sliderCoronal.setValue(int(ix))
        elif which == self.coronal:
            ix = int((np.abs(lengthAxis - ix)).argmin())
            iy = int((np.abs(sliceAxis - iy)).argmin())
            self.sliderAxialValue.setText(f"{int(iy)}")
            self.sliderSagittalValue.setText(f"{int(ix)}")
            self.sliderAxial.setValue(int(iy))
            self.sliderSagittal.setValue(int(ix))
        elif which == self.TACImage and self.resultView not in ["Dice","Jaccard","Energy","Mus","Factor f","Bayesian","Center of Mass","Moments"]:
            idx = (np.abs(self.Image.time - ix)).argmin()
            ix = self.Image.time[idx]
            self.sliderAcq.setValue(int(idx))
            self.sliderAcqValue.setText(f"{int(idx)}")
        elif which == self.AxialImage1D and self.resultView not in ["Bayesian"]:
            ix = int((np.abs(sliceAxis - ix)).argmin())
            self.sliderAxialValue.setText(f"{int(ix)}")
            self.sliderAxial.setValue(int(ix))
        elif which == self.SagittalImage1D and self.resultView not in ["Bayesian"]:
            ix = int((np.abs(lengthAxis - ix)).argmin())
            self.sliderSagittalValue.setText(f"{int(ix)}")
            self.sliderSagittal.setValue(int(ix))
        elif which == self.CoronalImage1D and self.resultView not in ["Bayesian"]:
            ix = int((np.abs(widthAxis - ix)).argmin())
            self.sliderCoronalValue.setText(f"{int(ix)}")
            self.sliderCoronal.setValue(int(ix))
    def onRoll(self,event,which):
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1
            #print("+")
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = -1
            #print("-")
        if which == self.axial:
            actual = int(self.sliderAxialValue.text())
            self.sliderAxialValue.setText(f"{int(actual+scale_factor)}")
            self.sliderAxial.setValue(int(actual)+scale_factor)
        elif which == self.sagittal:
            actual = int(self.sliderSagittalValue.text())
            self.sliderSagittalValue.setText(f"{int(actual+scale_factor)}")
            self.sliderSagittal.setValue(int(actual+scale_factor))
        elif which == self.coronal:
            actual = int(self.sliderCoronalValue.text())
            self.sliderCoronalValue.setText(f"{int(actual+scale_factor)}")
            self.sliderCoronal.setValue(int(actual+scale_factor))
        elif which == self.TACImage and self.resultView not in ["Dice","Jaccard","Energy","Mus","Factor f","Bayesian","Center of Mass","Moments"]:
            actual = int(self.sliderAcqValue.text())
            self.sliderAcqValue.setText(f"{int(actual+scale_factor)}")
            self.sliderAcq.setValue(int(actual+scale_factor))
        elif which == self.AxialImage1D and self.resultView not in ["Bayesian"]:
            actual = int(self.sliderAxialValue.text())
            self.sliderAxialValue.setText(f"{int(actual + scale_factor)}")
            self.sliderAxial.setValue(int(actual + scale_factor))
        elif which == self.SagittalImage1D and self.resultView not in ["Bayesian"]:
            actual = int(self.sliderSagittalValue.text())
            self.sliderSagittalValue.setText(f"{int(actual + scale_factor)}")
            self.sliderSagittal.setValue(int(actual + scale_factor))
        elif which == self.CoronalImage1D and self.resultView not in ["Bayesian"]:
            actual = int(self.sliderCoronalValue.text())
            self.sliderCoronalValue.setText(f"{int(actual + scale_factor)}")
            self.sliderCoronal.setValue(int(actual + scale_factor))

class MplCanvas(FigureCanvasQTAgg):
    """Class for the images and the graphs as a widget"""
    def __init__(self, parent=None, width:float=5, height:float=5, dpi:int=75):
        """Creates an empty figure with axes and fig as parameters"""
        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout= True)
        self.axes = fig.add_subplot(111)
        self.fig = fig
        super(MplCanvas, self).__init__(fig)

class WorkerExtraction(QObject):
    def __init__(self,source:str, which:str):
        QObject.__init__(self)
        self.source = source
        self.which = which
    finished = pyqtSignal()
    progress = pyqtSignal(list)
    error = pyqtSignal(str)

    extracted = pyqtSignal(list)
    def extract(self):
        """Extracts the Acquistion from files"""
        initial = time.time()
        if self.which == "second":
            try:
                self.Image = Extract.Extract_Images(self.source.text(),name = self.source.text(), verbose=True,save=False)
                self.progress.emit(["Second file extracted", initial])
                self.error.emit("An image is already loaded, loading the second for superposition")
            except:
                try:
                    self.Image = Extract_r.Extract_Images(self.source.text(),name = self.source.text(),verbose=True,save=False)
                    self.progress.emit(["Second file extracted", initial])
                    self.error.emit("An image is already loaded, loading the second for superposition")
                except:
                    self.error.emit("Second extraction is not possible")
            self.parameters = 0
        elif self.which == "first":
            try:
                self.Image = Extract.Extract_Images(self.source.text(),name = self.source.text(), verbose=True,save=False)
                self.progress.emit(["File extracted", initial])
                self.parameters = GUIParameters(self.Image)
            except:
                self.progress.emit(["Initial method not working, looking for adjacent folders", initial])
                try:
                    self.Image = Extract_r.Extract_Images(self.source.text(),name = self.source.text(),verbose=True,save=False)
                    self.progress.emit(["File extracted", initial])
                    self.parameters = GUIParameters(self.Image)
                except:
                    self.error.emit("Extraction is not possible")
        try:
            values = [self.Image,self.parameters,self.which]
            self.extracted.emit(values)
        except:
            pass
        self.finished.emit()


class WorkerLoad(QObject):
    def __init__(self,source:str, which:str):
        QObject.__init__(self)
        self.source = source
        self.which = which
    finished = pyqtSignal()
    progress = pyqtSignal(list)
    error = pyqtSignal(str)

    extracted = pyqtSignal(list)
    
    def load(self):
        """Extracts the Acquistion from files"""
        initial = time.time()
        try:
            tmp = PF.pickle_open(self.source.text())
            a = tmp.SegmAcq
            self.parameters = tmp
            self.Image = 0
            self.which = "param"
            self.progress.emit(["Parameter file loaded", initial])
        except:
            try:
                self.Image = PF.pickle_open(self.source.text())
                self.parameters = GUIParameters(self.Image)
                if self.which == "first":
                    self.progress.emit(["File loaded", initial])
                elif self.which == "second":
                    self.progress.emit(["Second file loaded", initial])
                    self.error.emit("An image is already loaded, loading the second for superposition")
            except: 
                self.error.emit("Loading is not possible")
        try:
            values = [self.Image,self.parameters,self.which]
            self.extracted.emit(values)
        except: pass
        self.finished.emit()

class WorkerSegmentation(QObject):
    def __init__(self,Image:DicomImage, parameters:GUIParameters):
        QObject.__init__(self)
        self.Image = Image
        self.parameters = parameters

    finished = pyqtSignal()
    progress = pyqtSignal(list)
    error = pyqtSignal(str)
    completed = pyqtSignal(list)

    def segment(self):
        initial = time.time()
        try:
            self.progress.emit([f"{self.parameters.SegmType} segmentation(s)",initial,'starting'])
            if self.parameters.SegmAcq >= 0:
                k = np.array([self.parameters.SegmAcq])
            else:
                k = np.arange(self.Image.nb_acq)
            if self.parameters.subImage[0,0] != 0:
                k = np.arange(self.parameters.subImage[0,0], self.parameters.subImage[0,1])
            for i in range(k.shape[0]):
                MyFunctions.Batch_Segmentations.Batch_Segmentations(segmentation_type=self.parameters.SegmType,Image=self.Image,
                                                            seed = self.parameters.seed,k=np.array([k[i]]),
                                                            subimage=self.parameters.subImage[1:,:],
                                                            sigma_Canny=self.parameters.sigmaCanny,combinationCanny=self.parameters.combinationCanny,
                                                            CannyThreshLow=self.parameters.sigmaThreshLowCanny,CannyThreshHigh=self.parameters.sigmaThreshHighCanny,
                                                            methodCanny=self.parameters.methodCanny,
                                                            alpha=self.parameters.alphaICM,max_iter_ICM=self.parameters.max_iter_ICM,
                                                            max_iter_kmean_ICM=self.parameters.max_iter_kmean_ICM,
                                                            steps_Fill = self.parameters.steps_filling,
                                                            max_iter_Fill = self.parameters.max_iter_fill,
                                                            factor_Fill_range = self.parameters.factor_Fill_range,
                                                            factor_fill= self.parameters.factor_fill_f,
                                                            growth = self.parameters.growth,
                                                            min_f_growth = self.parameters.min_f_growth,
                                                            threshold_fill=self.parameters.threshold_fill,
                                                            verbose_graph_fill = self.parameters.verbose_graph_fill,
                                                            classNumberFCM = self.parameters.classNumberFCM, alphaFCM = self.parameters.alphaFCM, 
                                                            mFCM = self.parameters.mFCM, 
                                                            maxIterFCM = self.parameters.maxIterFCM, maxIterConvergenceFCM = self.parameters.maxIterConvergenceFCM, 
                                                            convergenceDeltaFCM = self.parameters.convergenceDeltaFCM, convergenceStepFCM = self.parameters.convergenceStepFCM,
                                                            centerEllipsoid=self.parameters.centerEllipsoid,
                                                            axesEllipsoid=self.parameters.axesEllipsoid,
                                                            save=False,
                                                            do_Thresh=self.parameters.doThreshold,threshold=self.parameters.threshold,
                                                            do_coefficients=False,
                                                            SaveSegm=self.parameters.SaveSegm,do_moments=self.parameters.doMoments,
                                                            do_stats=self.parameters.doStats,verbose=self.parameters.verbose,
                                                            verboseNotGUI = False)
                self.progress.emit([f"Part done: {i+1} of {k.shape[0]}: {((i+1)/k.shape[0]*100):.2f} %, key = {k[i]} ",
                                    initial,
                                    "",((i+1)/k.shape[0]*100),
                                    True])   
            if self.parameters.doCoefficients:
                self.progress.emit([f"Dice and Jaccard coefficients computation",initial,'starting',100])
                self.Image.Dice_all()         
                self.Image.Jaccard_all()         
            if self.parameters.SegmType != "None":
                if isinstance(k,int):
                    if k == -1 and self.parameters.SegmType != "Ellipsoid":
                        self.parameters._nbSeg += self.parameters._size[0]
                else:
                    self.parameters._nbSeg += k.shape[0]
            self.progress.emit([f"{self.parameters.SegmType} segmentation(s)",initial])
            self.parameters.SegmType = "None" #Avoid running twice
            results = [self.Image, self.parameters]
            self.completed.emit(results)
        except:
            self.error.emit("Unable to run the segmentation")

        self.finished.emit()

class WorkerErrors(QObject):
    def __init__(self,Image:DicomImage, parameters:GUIParameters):
        QObject.__init__(self)
        self.Image = Image
        self.parameters = parameters

    finished = pyqtSignal()
    progress = pyqtSignal(list)
    error = pyqtSignal(str)
    completed = pyqtSignal(list)

    def errors(self):
        """
        Function to run the errors based on the input parameters
        """
        initial = time.time()
        if True:        
            self.progress.emit([f"{self.parameters.ErrorType} errors",initial,'starting'])
            if self.parameters.ErrorSegm >= 0:
                k = np.array([self.parameters.ErrorSegm])
            else: #(if k == -1)
                k = np.arange(self.parameters._nbSeg)        
            for i in range(k.shape[0]):            
                MyFunctions.Batch_Errors.Batch_Errors(Image=self.Image,error_type=self.parameters.ErrorType,k=np.array([k[i]]),
                                                    order=self.parameters.orderShift,d=self.parameters.distanceShift,
                                                    angle = self.parameters.angleError*2*np.pi/360,
                                                    factor= self.parameters.factorError,
                                                    iterations = self.parameters.iterationError,
                                                    verbose=self.parameters.verbose,
                                                    verboseNotGUI = False)
                self.progress.emit([f"Part done: {i+1} of {k.shape[0]}: {((i+1)/k.shape[0]*100):.2f} % ",initial,"",((i+1)/k.shape[0]*100),True])            

            if self.parameters.ErrorType != "None":
                self.parameters._nbError = self.Image.voi_statistics_counter
                self.progress.emit([f"{self.parameters.ErrorType} Errors",initial])
                self.parameters.ErrorType = "None" #Avoid running twice
            results = [self.Image, self.parameters]
            self.completed.emit(results)
        else:
            self.error.emit("Unable to run the errors")
        self.finished.emit()

class WorkerBayesian(QObject):
    def __init__(self,Image:DicomImage, parameters:GUIParameters):
        QObject.__init__(self)
        self.Image = Image
        self.parameters = parameters

    finished = pyqtSignal()
    progress = pyqtSignal(list)
    error = pyqtSignal(str)
    completed = pyqtSignal(list)
    def bayesian(self):
        """
        Function to run the Bayesian analyses based on the input parameters
        """
        initial = time.time()
        if True:
            self.progress.emit([f"{self.parameters.BayesianType} Bayesian analyses",initial,'starting'])
            if self.parameters.BayesianAcq >= 0:
                k = np.array([self.parameters.BayesianAcq])
            else: #(if k == -1)
                k = np.arange(self.parameters._nbError)   
            for i in range(k.shape[0]):            
                self.Image.Bayesian_analyses(key=np.array([k[i]]),
                                        curves = self.parameters.CurveTypeBayesian,
                                        method=self.parameters.BayesianType,
                                        model = self.parameters.ModelBayesian,
                                        thresh_perc=self.parameters.Bayesian_thresh_perc,
                                        thresh_value=self.parameters.Bayesian_thresh_value,
                                        verbose = False,
                                        save=True)
                self.progress.emit([f"Part done: {i+1} of {k.shape[0]}: {((i+1)/k.shape[0]*100):.2f} % ",initial,"",((i+1)/k.shape[0]*100),True])            
            if self.parameters.BayesianType != "None":
                self.parameters._nbBayesian = self.Image.bayesian_dynesty_counter
                self.progress.emit([f"{self.parameters.BayesianType} Bayesian",initial])
                self.parameters.BayesianType = "None" #Avoid running twice
            results = [self.Image, self.parameters]
            self.completed.emit(results)
        else:
            self.error.emit("Unable to run the Bayesian analyses")
        self.finished.emit()

class WorkerNoise(QObject):
    def __init__(self,Image:DicomImage, parameters:GUIParameters):
        QObject.__init__(self)
        self.Image = Image
        self.parameters = parameters

    finished = pyqtSignal()
    progress = pyqtSignal(list)
    error = pyqtSignal(str)
    completed = pyqtSignal(list)

    def noise(self):
        """
        Function to run the noise based on the input parameters
        """
        initial = time.time()
        if True:
            self.progress.emit([f"{self.parameters.NoiseType} noise",initial,'starting'])
            self.Image.add_noise(noiseType= self.parameters.NoiseType,
                                    noiseMu = self.parameters.NoiseMu,
                                    noiseSigma= self.parameters.NoiseSigma,
                                    Rayleigh_a= self.parameters.NoiseARayleigh,
                                    Rayleigh_b= self.parameters.NoiseBRayleigh,
                                    Erlang_a= self.parameters.NoiseAErlang,
                                    Erlang_b= self.parameters.NoiseBErlang,
                                    Unif_a= self.parameters.NoiseAUniform,
                                    Unif_b= self.parameters.NoiseBUniform,
                                    Exponential= self.parameters.NoiseExponential
                                    )
            if self.parameters.NoiseType != "None":
                self.progress.emit([f"{self.parameters.NoiseType} noise added",initial])
                self.parameters.NoiseType = "None" #Avoid running twice
            else:
                self.progress.emit(["",initial])
            results = [self.Image, self.parameters]
            self.completed.emit(results)
        else:
            self.error.emit("Unable to run the noise")
        self.finished.emit()

class WorkerDeformation(QObject):
    def __init__(self,Image:DicomImage, parameters:GUIParameters):
        QObject.__init__(self)
        self.Image = Image
        self.parameters = parameters

    finished = pyqtSignal()
    progress = pyqtSignal(list)
    error = pyqtSignal(str)
    completed = pyqtSignal(list)
    def deformation(self):
        """
        Function to run the deformations based on the input parameters
        """
        initial = time.time()
        if True:
            self.progress.emit([f"{self.parameters.deformationType} deformations",initial,'starting'])
            if self.parameters.deformationSegm >= 0:
                k = np.array([self.parameters.deformationSegm])
            else: #(if k == -1)
                k = np.arange(self.parameters._nbSeg)   
            for i in range(k.shape[0]):   
                MyFunctions.Batch_Deform.Batch_Deform(Image = self.Image, deform_type= self.parameters.deformationType,
                                                    k = np.array([k[i]]),
                                                    linear_d= self.parameters.deformationDistanceShift,
                                                    rotate_angle= self.parameters.deformationRotate*2*np.pi/360,
                                                    factors_exp= self.parameters.deformationExpansion,
                                                    reflection_axis = self.parameters.deformationReflectionAxis,
                                                    flipAxis = self.parameters.flipAxis,
                                                    switchAxes = self.parameters.switchAxes,
                                                    verbose= False,
                                                    do_coefficients = self.parameters.doCoefficients,
                                                    delete_after = self.parameters.deleteAfterDeformation,
                                                    verboseNotGUI= False)
                self.progress.emit([f"Part done: {i+1} of {k.shape[0]}: {((i+1)/k.shape[0]*100):.2f} % ",initial,"",((i+1)/k.shape[0]*100),True])            


            if self.parameters.deformationType != "None" and not self.parameters.deleteAfterDeformation:

                self.progress.emit([f"{self.parameters.deformationType} deformations ",initial])
                if self.parameters.deformationSegm == -1:
                    self.parameters._nbSeg += self.parameters._size[0]
                else:
                    self.parameters._nbSeg += 1
            else:
                self.progress.emit(["",initial])
        else:
            self.error.emit("Unable to run the deformations")
        self.finished.emit()

class WorkerErase(QObject):
    def __init__(self,Image:DicomImage, parameters:GUIParameters):
        QObject.__init__(self)
        self.Image = Image
        self.parameters = parameters

    finished = pyqtSignal()
    progress = pyqtSignal(list)
    error = pyqtSignal(str)
    completed = pyqtSignal(list)
    def erase(self):
        """
        Function to run the deformations based on the input parameters
        """
        initial = time.time()
        if True:
            self.progress.emit([f"{self.parameters.EraseType} removal",initial,'starting'])
            if self.parameters.EraseType == "Segmentation":
                self.Image.remove_VOI(self.parameters.EraseSegm)
                self.parameters._nbSeg = self.Image.voi_counter
            elif self.parameters.EraseType == "Error":
                self.Image.remove_Error(self.parameters.EraseError)                                
                self.parameters._nbError = self.Image.voi_statistics_counter
            elif self.parameters.EraseType == "Bayesian":
                self.Image.remove_Bayesian(self.parameters.EraseBayesian)
                self.parameters._nbBayesian = self.Image.bayesian_dynesty_counter
            if self.parameters.EraseType != "None":
                self.progress.emit([f"{self.parameters.EraseType} removal ",initial])
                self.parameters.EraseType = "None" #Avoids erasing twice
            else:
                self.progress.emit(["",initial])
        else:
            self.error.emit("Unable to erase the selected computation")
        self.finished.emit()

###
if __name__ == "__main__":
    cls = lambda: os.system('cls' if os.name=='nt' else 'clear')
    cls()
    print(f"Starting program at {time.strftime('%H:%M:%S')}")
    initial = time.time()
    app = QApplication([])
    window=MainWindow()
    window.show()
    sys.exit(app.exec())