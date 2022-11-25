from re import sub
from inflection import parameterize
import numpy as np
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import matplotlib.pyplot as plt
from sympy import Q
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
import markdown

size_Image = 200

class Window(QMainWindow):
    """
    Main window of the GUI.
    """    
    def _createLog(self):
        """Create a Log tab to keep track of the processes"""
        self.logText = QTextEdit()
        self.logText.setReadOnly(True)
        try:
            self.logText.setText(self.Image.progress_log)
        except:
            self.logText.setText("Nothing started")
        self.generalLayoutLog.addWidget(self.logText)
    def _createReadMe(self):
        """Creates a ReadMe tab with the ReadMe file infos"""
        self.ReadMeText = QTextEdit()
        self.ReadMeText.setReadOnly(True)
        f = open('ReadMe.md', 'r')
        htmlmarkdown = markdown.markdown( f.read() )
        self.ReadMeText.setText(htmlmarkdown)
        self.generalLayoutReadMe.addWidget(self.ReadMeText)
    def _createStatusBar(self):
        """Create a status bar at the bottom of the GUI"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)      
        self.statusBar.showMessage("Nothing started")
    def _createNoiseButtons(self):
        """Create the Noise button at the top of the GUI"""
        subWidget = QWidget()
        layout = QHBoxLayout()
        subWidget.setLayout(layout)

        btn_noise = QPushButton("Noise")
        btn_noise.setToolTip("Adds the noise to the images according to the selected parameters")
        btn_noise.clicked.connect(self.run_noise)

        layout.addWidget(btn_noise)
        self.generalLayout.addWidget(subWidget,self.current_line,3)    
        self.current_line += 1
    def _createInfoParam(self):
        """Create the dock at the top from where the parameters, the infos and the lauch buttons are"""
        subWidget = QWidget()
        layout = QHBoxLayout()
        subWidget.setLayout(layout)
        
        btn_segm = QPushButton("Segment")
        buttonErrors = QPushButton("ErrorBars")
        buttonBayesian = QPushButton("Bayesian")

        btn_segm.setToolTip("Runs the segmentations according to the selected parameters")
        buttonErrors.setToolTip("Runs the error bars according to the selected parameters")
        buttonBayesian.setToolTip("Runs the Bayesian analyses according to the selected parameters")

        buttonErrors.clicked.connect(self.run_errors)
        buttonBayesian.clicked.connect(self.run_Bayesian)
        btn_segm.clicked.connect(self.run_segm)

        layout.addWidget(btn_segm)
        layout.addWidget(buttonErrors)
        layout.addWidget(buttonBayesian)
        self.generalLayout.addWidget(subWidget,self.current_line,3)    
    def _createExitButton(self):
        """Create an exit button"""
        self.exit = QPushButton("Exit")
        self.exit.setToolTip("Closes the GUI and its dependencies")
        self.exit.clicked.connect(self.close)
        self.generalLayout.addWidget(self.exit,self.current_line+1,3)  
        self.current_line += 2
    def _createExtractDock(self):
        """Create the dock to enter a line and the buttons to extract, load and, browse the origin of the acquisition"""
        subWidget = QWidget()
        msg_extract = QLabel("Path: ")
        source = QLineEdit()
        btn_extr = QPushButton("Extract")
        btn_load = QPushButton("Load")
        btn_browse = QPushButton("Browse")

        btn_extr.setToolTip("Extracts the relevant information from a folder containing .dcm files")
        btn_load.setToolTip("Loads the selected .pkl file")
        btn_browse.setToolTip("Opens a local browser to select a file")

        source.setText("/Users/philippelaporte/Desktop/Programmation/Python/Data/Fantome_6_1min_comp_2_I_k_all.pkl")
        source.setText("/Users/philippelaporte/Desktop/FantDYN9/PET-AC-DYN-1-MIN/")
        source.setText("/Users/philippelaporte/Desktop/Fantome_9_1min.pkl")
        source.setText("/Users/philippelaporte/Desktop/Test/Fan9_Dyn_DicomImage.pkl")
        
        btn_extr.clicked.connect(partial(self.extract_button,source))
        btn_load.clicked.connect(partial(self.load_button,source))
        btn_browse.clicked.connect(partial(self.browse_button_file,source))

        layout = QHBoxLayout()
        subWidget.setLayout(layout)
        layout.addWidget(btn_browse)
        layout.addWidget(btn_extr)
        layout.addWidget(btn_load)

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
        btn_param = QPushButton("Parameters")
        btn_param.setToolTip("Opens a window to select the paremeters used for segmentations, error bars, and Bayesian analyses")
        btn_param.setToolTip("Displays the parameters to resize the acquisition or to set up for the segmentations")
        btn_param.clicked.connect(self.open_parameters)
          
        self.btn = QPushButton("Info")
        self.btn.clicked.connect(self.on_button_clicked_infos)
        self.btn.setToolTip("Displays the infos of the current loaded acquisition")
        path = QLineEdit()
        path_name = QLineEdit()
        path.setText("")
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(partial(self.save_button,path,path_name))
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(partial(self.browse_button_directory,path))
        btn_export = QPushButton("Export")
        btn_export.setToolTip("Opens an window to decide what to export")
        btn_export.clicked.connect(self.open_export)
        layout1.addWidget(path)
        layout1.addWidget(path_name)
        layout2.addWidget(btn_export)
        layout2.addWidget(self.btn)
        layout2.addWidget(btn_param)
        self.generalLayout.addWidget(subWidget2,self.current_line,2)  
    def _createImageDisplay(self):
        """Create the docks for the 2D images to be shown"""
        self.showFocus = False
        self.showSubImage = False
        self.showLog = False
        msg_Image = QLabel("View: ")
        msg_Axial = QLabel("Axial")
        msg_Sagittal = QLabel("Sagittal")
        msg_Coronal = QLabel("Coronal")
        self.axial = MplCanvas(self, width=1, height=1, dpi=75)
        self.sagittal = MplCanvas(self, width=1, height=1, dpi=75)
        self.coronal = MplCanvas(self, width=1, height=1, dpi=75)
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
        self.ResultViewCombo.addItem("Dice")
        self.ResultViewCombo.addItem("Jaccard")
        self.ResultViewCombo.addItem("Bayesian")
        self.ResultViewCombo.activated[str].connect(self.combo_box_result_changed)

        layout.addWidget(self.ImageViewCombo)
        layout.addWidget(self.ResultViewCombo)
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
        except:
            pass
        checkBoxMsglog = QLabel("log:")

        sublayout.addWidget(self.checkBoxMsgFocus,0,0)
        sublayout.addWidget(self.checkBoxFocus,0,1)
        sublayout.addWidget(self.checkBoxMsgSubImage,0,2)
        sublayout.addWidget(self.checkBoxSubImage,0,3)
        sublayout.addWidget(checkBoxMsglog,0,4)
        sublayout.addWidget(self.checkBoxLog,0,5)
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
        self.TACImage = MplCanvas(self, width=5, height=4, dpi=75)
        self.TACImage.setMinimumSize(size_Image,size_Image)
        self.base_TAC_axes()
        self.generalLayout.addWidget(self.TACImage,self.current_line,2)
        self.current_line += 1
    def _create1DImage(self):
        """Create the dock for the 1D Image (i.e. the slices)"""
        label = QLabel("Slices")
        self.AxialImage1D = MplCanvas(self,width=5,height=4,dpi=75)
        self.SagittalImage1D = MplCanvas(self,width=5,height=4,dpi=75)
        self.CoronalImage1D = MplCanvas(self,width=5,height=4,dpi=75)
        self.AxialImage1D.setMinimumSize(size_Image,size_Image)
        self.SagittalImage1D.setMinimumSize(size_Image,size_Image)
        self.CoronalImage1D.setMinimumSize(size_Image,size_Image)

        self.base_1D_axes()

        self.generalLayout.addWidget(label,self.current_line,0)
        self.generalLayout.addWidget(self.AxialImage1D,self.current_line,1)
        self.generalLayout.addWidget(self.SagittalImage1D,self.current_line,3)
        self.generalLayout.addWidget(self.CoronalImage1D,self.current_line,2)
        self.current_line += 1
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
        self.update_all()
    def combo_box_result_changed(self):
        """Update the view between partial and full"""
        self.resultView = self.ResultViewCombo.currentText()
        self.update_all()
    def open_parameters(self):
        "Open a window to show the basic informations of the acquisition"
        try:
            window = ParamWindow(self.parameters,self)
            window.show()
        except:
            self._createErrorMessage()
    def open_export(self):
        """
        Opens a new window to decide what to export and what to save
        """
        try:
            window = ExportWindow(self.parameters,self.Image,self)
            window.show()
        except:
            self._createErrorMessage()
    def run_segm(self):
        """
        Function to run the segmentations based on the input parameters
        """
        try:
            initial = time.time()
            if self.parameters.SegmAcq >= 0:
                k = np.array([self.parameters.SegmAcq])
            else:
                k=-1
            MyFunctions.Batch_Segmentations.Batch_Segmentations(segmentation_type=self.parameters.SegmType,Image=self.Image,
                                                            seed = self.parameters.seed,k=k,
                                                            subimage=self.parameters.subImage[1:,:],
                                                            sigma_Canny=self.parameters.sigmaCanny,combinationCanny=self.parameters.combinationCanny,
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
                                                            centerEllipsoid=self.parameters.centerEllipsoid,
                                                            axesEllipsoid=self.parameters.axesEllipsoid,
                                                            save=False,
                                                            do_Thresh=self.parameters.doThreshold,threshold=self.parameters.threshold,
                                                            do_coefficients=self.parameters.doCoefficients,
                                                            SaveSegm=self.parameters.SaveSegm,do_moments=self.parameters.doMoments,
                                                            do_stats=self.parameters.doStats,verbose=self.parameters.verbose)
            if self.parameters.SegmType != "None":
                if k == -1 and self.parameters.SegmType != "Ellipsoid":
                    self.parameters._nbSeg += self.parameters._size[0]
                else:
                    self.parameters._nbSeg += 1
            self.displayStatus(f"{self.parameters.SegmType} segmentation",initial)
            self.update_segm()
        except:
            self._createErrorMessage("Unable to run the segmentation")
    def run_errors(self):
        """
        Function to run the errors based on the input parameters
        """
        try:
            initial = time.time()
            if self.parameters.ErrorSegm >= 0:
                k = np.array([self.parameters.ErrorSegm])
            else:
                k=-1
            MyFunctions.Batch_Errors.Batch_Errors(Image=self.Image,error_type=self.parameters.ErrorType,k=k,
                                                    order=self.parameters.orderShift,d=self.parameters.distanceShift,
                                                    verbose=self.parameters.verbose)
            self.displayStatus(f"{self.parameters.ErrorType} errors",initial)
            self.update_segm()
            if self.parameters.ErrorType != "None":
                self.parameters._nbError = self.Image.voi_statistics_counter
        except:
            self._createErrorMessage("Unable to run the error bars production")
    def run_Bayesian(self):
        """
        Function to run the Bayesian Analyses to extract the coefficients based on the input parameters
        """
        try:
            initial = time.time()
            if self.parameters.BayesianAcq >= 0:
                k = np.array([self.parameters.BayesianAcq])
            else:
                k=-1
            self.Image.Bayesian_analyses(key=k,curves = self.parameters.CurveTypeBayesian,method=self.parameters.BayesianType,
                                        model = self.parameters.ModelBayesian,
                                        thresh_perc=self.parameters.Bayesian_thresh_perc,
                                        thresh_value=self.parameters.Bayesian_thresh_value,
                                        verbose = self.parameters.verbose,
                                        save=True)
            self.displayStatus(f"{self.parameters.BayesianType} Bayesian analyses",initial)
            self.update_segm()
        except:
            self._createErrorMessage("Unable to run the Bayesian analyses")
    def run_noise(self):
        """
        Function to add noise to the image.
        For now, the resulting image will overwrite the previous (or basic) one
        """   
        try:
            initial = time.time()
            self.Image.add_noise(noiseType= self.parameters.NoiseType,
                                    noiseMu = self.parameters.NoiseMu,
                                    noiseSigma= self.parameters.NoiseSigma)
            if self.parameters.NoiseType != "None":
                self.displayStatus(f"{self.parameters.NoiseType} noise added",initial)
            else:
                self.displayStatus("",initial)
            self.update_all()
        except:
            self._createErrorMessage("Unable to add the noise")
    def update_all(self):
        """Main function when something is changed to update all the views"""
        self.update_Result()
        self.update_1D()
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
        if self.resultView == "TAC":
            self.update_TAC()
        elif self.resultView == "Dice":
            self.update_Dice()
        elif self.resultView == "Jaccard":
            self.update_Jaccard()
        elif self.resultView == "Bayesian":
            self.update_Bayesian(self.sliderBayesian.value())
    def update_Dice(self):
        """Shows the Dice coefficients in the middle image"""
        try:
            self.TACImage.axes.cla()
            im = self.TACImage.axes.pcolormesh(self.Image.dice_all)
            self.base_coeff_axes(im)
            self.TACImage.draw() 
        except:
            pass
    def update_Jaccard(self):
        """Shows the Jaccard coefficients in the middle image"""
        try:
            self.TACImage.axes.cla()
            im = self.TACImage.axes.pcolormesh(self.Image.jaccard_all)
            self.base_coeff_axes(im)
            self.TACImage.draw() 
        except:
            pass
    def update_Bayesian(self,param:int=0):
        """Shows the Bayesian coefficients in the middle image"""
        try:
            if param == -1:
                k = np.arange(self.Image.bayesian_results_avg.shape[1])
            else:
                k = np.array([param])
            self.TACImage.axes.cla()
            for i in range(k.shape[0]):
                self.TACImage.axes.errorbar(np.arange(self.Image.bayesian_results_avg.shape[0]),
                                                self.Image.bayesian_results_avg[:,k[i]],
                                                yerr=[self.Image.bayesian_results_e_down[:,k[i]],self.Image.bayesian_results_e_up[:,k[i]]])
            self.base_Bayesian_axes()
            self.TACImage.draw() 
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
            self.TACImage.axes.cla()
            values = [self.sliderAcq.value(),self.sliderAxial.value(),self.sliderCoronal.value(),self.sliderSagittal.value()]
            subI = self.parameters.subImage[0,:]
            if self.view_range == "All":
                x_axis = self.Image.time
                if self.sliderSegm.value() >= 0 or self.sliderSegmStats.value() >= 0 or self.sliderFitted.value() >= 0:
                    if self.sliderSegm.value() >= 0:
                        y_axis = self.Image.voi_statistics[self.sliderSegm.value()]
                    if self.sliderSegmStats.value() >= 0:
                        y_axis2 = self.Image.voi_statistics_avg[self.sliderSegmStats.value()]
                        error = self.Image.voi_statistics_std[self.sliderSegmStats.value()]
                    if self.sliderFitted.value() > 0:
                        y_axis3 = model(x_axis,self.Image.bayesian_results_avg[self.sliderFitted.value(),:])
                else:
                    y_axis = self.Image.Image[:,values[1],values[2],values[3]]
            else:
                x_axis = self.Image.time[subI[0]:subI[1]]
                if self.sliderSegm.value() >= 0 or self.sliderSegmStats.value() >= 0:
                    if self.sliderSegm.value() >= 0:
                        y_axis = self.Image.voi_statistics[self.sliderSegm.value()][subI[0]:subI[1]]
                    if self.sliderSegmStats.value() >= 0:
                        y_axis2 = self.Image.voi_statistics_avg[self.sliderSegmStats.value()][subI[0]:subI[1]]
                        error = self.Image.voi_statistics_std[self.sliderSegmStats.value()][subI[0]:subI[1]]
                    if self.sliderFitted.value() > 0:
                        y_axis3 = model(x_axis,self.Image.bayesian_results_avg[self.sliderFitted.value(),:])[subI[0]:subI[1]]
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
                self.TACImage.axes.plot(x_axis,y_axis,color='b',label="TAC")
            except: pass
            try:
                self.TACImage.axes.errorbar(x_axis,y_axis2,error,color='r',label="Error TAC")
            except: pass
            try:
                self.TACImage.axes.plot(x_axis,y_axis3,color='g',label="Fit")
            except: pass
            self.base_TAC_axes()
            self.TACImage.draw()                
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

            values = [self.sliderAcq.value(),self.sliderAxial.value(),self.sliderCoronal.value(),self.sliderSagittal.value()]
            if self.view_range == "All":
                self.AxialImage1D.axes.plot(np.arange(self.Image.nb_slice),self.Image.Image[values[0],:,values[2],values[3]])
                self.SagittalImage1D.axes.plot(np.arange(self.Image.length),self.Image.Image[values[0],values[1],values[2],:])
                self.CoronalImage1D.axes.plot(np.arange(self.Image.width),self.Image.Image[values[0],values[1],:,values[3]])
            else:
                subI = self.parameters.subImage
                self.AxialImage1D.axes.plot(np.arange(subI[1,0],subI[1,1]+1),self.Image.Image[values[0],subI[1,0]:subI[1,1]+1,values[2],values[3]])
                self.SagittalImage1D.axes.plot(np.arange(subI[3,0],subI[3,1]+1),self.Image.Image[values[0],values[1],values[2],subI[3,0]:subI[3,1]+1])
                self.CoronalImage1D.axes.plot(np.arange(subI[2,0],subI[2,1]+1),self.Image.Image[values[0],values[1],subI[2,0]:subI[2,1]+1,values[3]])
 
            if self.showFocus:
                self.AxialImage1D.axes.axvline(values[1],color='r')
                self.SagittalImage1D.axes.axvline(values[3],color='r')
                self.CoronalImage1D.axes.axvline(values[2],color='r')
            if self.showSubImage:
                self.AxialImage1D.axes.axvline(self.parameters.subImage[1,0],color='y')
                self.AxialImage1D.axes.axvline(self.parameters.subImage[1,1],color='y')
                self.SagittalImage1D.axes.axvline(self.parameters.subImage[3,0],color='y')
                self.SagittalImage1D.axes.axvline(self.parameters.subImage[3,1],color='y')
                self.CoronalImage1D.axes.axvline(self.parameters.subImage[2,0],color='y')
                self.CoronalImage1D.axes.axvline(self.parameters.subImage[2,1],color='y')

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
            self.sliderSagittal.setMinimum(0);self.sliderSagittal.setMaximum(self.Image.width-1)
            self.sliderCoronal.setMinimum(0);self.sliderCoronal.setMaximum(self.Image.length-1)
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
    def update_view(self):
        """Updates the top images (2D views) according to the parameters input and the determined view requested"""
        values = [self.sliderAcq.value(),self.sliderAxial.value(),self.sliderCoronal.value(),self.sliderSagittal.value()]
        try: SubI = self.parameters.subImage
        except: pass
        #if SubI[0,0] >= SubI[0,1] or SubI[1,0] >= SubI[1,1] or SubI[2,0] >= SubI[2,1] or SubI[3,0] >= SubI[3,1]:
        #    self._createErrorMessage("Wrong subimage. Check to be sure that the values are in the good order")
        key = self.sliderSegm.value()
        try:
            self.axial.axes.cla()
            self.sagittal.axes.cla()
            self.coronal.axes.cla()
        except: pass
        if self.showFocus:
            self.axial.axes.plot(values[3],values[2],'*',markersize = 6,color='y')
            self.sagittal.axes.plot(values[2],values[1],'*',markersize = 6,color='y')
            self.coronal.axes.plot(values[3],values[1],'*',markersize = 6,color='y')
            self.axial.axes.axhline(values[2],color='r')
            self.axial.axes.axvline(values[3],color='r')
            self.sagittal.axes.axhline(values[1],color='r')
            self.sagittal.axes.axvline(values[2],color='r')
            self.coronal.axes.axhline(values[1],color='r')
            self.coronal.axes.axvline(values[3],color='r')
        if self.showSubImage:
            self.axial.axes.axhline(self.parameters.subImage[2,0],color='y')
            self.axial.axes.axhline(self.parameters.subImage[2,1],color='y')
            self.sagittal.axes.axhline(self.parameters.subImage[1,0],color='y')
            self.sagittal.axes.axhline(self.parameters.subImage[1,1],color='y')
            self.coronal.axes.axhline(self.parameters.subImage[1,0],color='y')
            self.coronal.axes.axhline(self.parameters.subImage[1,1],color='y')
            self.axial.axes.axvline(self.parameters.subImage[3,0],color='y')
            self.axial.axes.axvline(self.parameters.subImage[3,1],color='y')
            self.sagittal.axes.axvline(self.parameters.subImage[2,0],color='y')
            self.sagittal.axes.axvline(self.parameters.subImage[2,1],color='y')
            self.coronal.axes.axvline(self.parameters.subImage[3,0],color='y')
            self.coronal.axes.axvline(self.parameters.subImage[3,1],color='y')
        if self.showLog:
            def a(x):
                return np.log(x+1)
        else:
            def a(x):
                return x
        func = a
        if self.view == "Slice":
            try:
                self.axial.axes.pcolormesh(func(self.Image.Image[values[0],values[1],:,:]))
                self.sagittal.axes.pcolormesh(func(self.Image.Image[values[0],:,:,values[3]]))
                self.coronal.axes.pcolormesh(func(self.Image.Image[values[0],:,values[2],:]))
            except:
                pass
        elif self.view == "Flat":
            try:
                self.axial.axes.pcolormesh(func(self.Image.axial_flat(acq=values[0])))
                self.sagittal.axes.pcolormesh(func(self.Image.sagittal_flat(acq=values[0])))
                self.coronal.axes.pcolormesh(func(self.Image.coronal_flat(acq=values[0])))
            except:
                self._createErrorMessage("Can't perform this. No image is loaded or the flats are not done")
        elif self.view == "Segm. Slice":
            try:
                self.axial.axes.pcolormesh(func(self.Image.voi[f"{key}"][values[1],:,:]))
                self.sagittal.axes.pcolormesh(func(self.Image.voi[f"{key}"][:,:,values[3]]))
                self.coronal.axes.pcolormesh(func(self.Image.voi[f"{key}"][:,values[2],:]))
            except:
                self._createErrorMessage("Can't perform this. No segmentations are present")
        elif self.view == "Segm. Flat":
            try:
                self.axial.axes.pcolormesh(func(self.Image.axial_flat(counter=key)))
                self.sagittal.axes.pcolormesh(func(self.Image.sagittal_flat(counter=key)))
                self.coronal.axes.pcolormesh(func(self.Image.coronal_flat(counter=key)))
            except:
                self._createErrorMessage("Can't perform this. No segmentations are present")
        elif self.view == "Sub. Slice":
            try:
                self.axial.axes.pcolormesh(np.arange(SubI[3,0],SubI[3,1]+1),np.arange(SubI[2,0],SubI[2,1]+1),func(self.Image.Image[values[0],values[1],SubI[2,0]:SubI[2,1],SubI[3,0]:SubI[3,1]]))
                self.sagittal.axes.pcolormesh(np.arange(SubI[2,0],SubI[2,1]+1),np.arange(SubI[1,0],SubI[1,1]+1),func(self.Image.Image[values[0],SubI[1,0]:SubI[1,1],SubI[2,0]:SubI[2,1],values[3]]))
                self.coronal.axes.pcolormesh(np.arange(SubI[3,0],SubI[3,1]+1),np.arange(SubI[1,0],SubI[1,1]+1),func(self.Image.Image[values[0],SubI[1,0]:SubI[1,1],values[2],SubI[3,0]:SubI[3,1]]))
            except:
                self._createErrorMessage("Can't perform this. No SubImage selected")
        elif self.view == "Sub. Flat":
            try:
                self.axial.axes.pcolormesh(np.arange(SubI[3,0],SubI[3,1]+1),np.arange(SubI[2,0],SubI[2,1]+1),func(self.Image.axial_flat(acq=values[0])[SubI[2,0]:SubI[2,1],SubI[3,0]:SubI[3,1]]))
                self.sagittal.axes.pcolormesh(np.arange(SubI[2,0],SubI[2,1]+1),np.arange(SubI[1,0],SubI[1,1]+1),func(self.Image.sagittal_flat(acq=values[0])[SubI[1,0]:SubI[1,1],SubI[2,0]:SubI[2,1]]))
                self.coronal.axes.pcolormesh(np.arange(SubI[3,0],SubI[3,1]+1),np.arange(SubI[1,0],SubI[1,1]+1),func(self.Image.coronal_flat(acq=values[0])[SubI[1,0]:SubI[1,1],SubI[3,0]:SubI[3,1]]))
            except:
                self._createErrorMessage("Can't perform this. No SubImage selected")
        elif self.view == "Segm. Sub. Slice":
            try:
                self.axial.axes.pcolormesh(np.arange(SubI[3,0],SubI[3,1]+1),np.arange(SubI[2,0],SubI[2,1]+1),func(self.Image.voi[f"{key}"][values[1],SubI[2,0]:SubI[2,1],SubI[3,0]:SubI[3,1]]))
                self.sagittal.axes.pcolormesh(np.arange(SubI[2,0],SubI[2,1]+1),np.arange(SubI[1,0],SubI[1,1]+1),func(self.Image.voi[f"{key}"][SubI[1,0]:SubI[1,1],SubI[2,0]:SubI[2,1],values[3]]))
                self.coronal.axes.pcolormesh(np.arange(SubI[3,0],SubI[3,1]+1),np.arange(SubI[1,0],SubI[1,1]+1),func(self.Image.voi[f"{key}"][SubI[1,0]:SubI[1,1],values[2],SubI[3,0]:SubI[3,1]]))
            except:
                self._createErrorMessage("Can't perform this. No SubImage selected or no segmentation done")
        elif self.view == "Segm. Sub. Flat":
            try:
                self.axial.axes.pcolormesh(np.arange(SubI[3,0],SubI[3,1]+1),np.arange(SubI[2,0],SubI[2,1]+1),func(self.Image.axial_flat(counter=key)[SubI[2,0]:SubI[2,1],SubI[3,0]:SubI[3,1]]))
                self.sagittal.axes.pcolormesh(np.arange(SubI[2,0],SubI[2,1]+1),np.arange(SubI[1,0],SubI[1,1]+1),func(self.Image.sagittal_flat(counter=key)[SubI[1,0]:SubI[1,1],SubI[2,0]:SubI[2,1]]))
                self.coronal.axes.pcolormesh(np.arange(SubI[3,0],SubI[3,1]+1),np.arange(SubI[1,0],SubI[1,1]+1),func(self.Image.coronal_flat(counter=key)[SubI[1,0]:SubI[1,1],SubI[3,0]:SubI[3,1]]))
            except:
                self._createErrorMessage("Can't perform this. No SubImage selected or no segmentation done")
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
    def displayStatus(self,action:str="",time_i=time.time()):
        """Updates the display bar (far bottom)"""
        if action != "":
            new_status = f"{action} done in {(time.time()-time_i):.2f}' s at {time.strftime('%H:%M:%S')}"
            self.statusBar.showMessage(new_status)
            self.Image.progress_log += "\n" + new_status
            self.logText.textCursor().insertHtml(new_status + '<br>')
        self.logText.setText(self.Image.progress_log)
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
                Dose Injected: {self.Image.Dose_inj}<br>
                Mass: {self.Image.mass}<br>
                Units: {self.Image.units}<br>
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
        try:
            a = self.name
            self._createErrorMessage("An image is already loaded")
        except:
            try:
                self.Image = Extract_r.Extract_Images(source.text(),verbose=True,save=False)
            except:
                try:
                    self.Image = Extract.Extract_Images(source.text(),verbose=True,save=False)
                except:
                    self._createErrorMessage("Extraction is not possible")
                    return 0
            self.displayStatus("File extracted", initial)
            self._createImageDisplay()
            self._createImageDisplayBars()
            self.parameters = GUIParameters(self.Image)
    def load_button(self,source:QLineEdit):
        """Loads the image according to the given QLineEdit.
            Will fail if an image is already loaded."""
        initial = time.time()
        try:
            self.parameters = PF.pickle_open(source.text())
            a = self.parameters.SegmAcq
        except:
            try:
                a = self.name
                self._createErrorMessage("An image is already loaded")
            except:
                try:
                    self.Image = PF.pickle_open(source.text())
                    self.name = self.Image.version
                    self.displayStatus("File loading", initial)
                    self._createImageDisplay()
                    self._createImageDisplayBars()
                    self.parameters = GUIParameters(self.Image)
                except:
                    self._createErrorMessage("Loading is not possible")
    def browse_button_directory(self,source:QLineEdit):
        """Depleted"""
        text =  QFileDialog.getExistingDirectory()
        source.setText(text+"/")
    def browse_button_file(self,source:QLineEdit):
        """Opens a browsing system and keeps the selected file (cannot select a folder)"""
        text = QFileDialog.getOpenFileName(self)
        source.setText(text[0])
    def save_button(self,path:QLineEdit,path_name:QLineEdit):
        """Depleted"""
        initial = time.time()
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

    def __init__(self):
        """Initializes the GUI Window"""
        self.tabs = QTabWidget()
        self.BUTTON_SIZE = 40
        self.DISPLAY_HEIGHT = 35
        self.current_line = 0
        #self.displayImageLine = 0
        self.first_pass = True
        super().__init__(parent=None)
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("My GUI")
        self.generalLayout = QGridLayout()
        self.generalLayoutLog = QGridLayout()
        self.generalLayoutReadMe = QGridLayout()
        centralWidget = QWidget(self)
        centralWidgetLog = QWidget(self)
        centralWidgetReadMe = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        centralWidgetLog.setLayout(self.generalLayoutLog)
        centralWidgetReadMe.setLayout(self.generalLayoutReadMe)
        self.tabs.addTab(centralWidget,"Main")
        self.tabs.addTab(centralWidgetLog,"Log")
        self.tabs.addTab(centralWidgetReadMe,"Read Me")

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
        #Status Bar
        self._createStatusBar()

def evaluateExpression(expression):
    """Evaluate an expression (Model)."""
    try:
        result = str(eval(expression, {}, {}))
    except Exception:
        result = "ERROR_MSG"
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
        if self._view.displayText() == "ERROR_MSG":
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
    """Class for the images and the graphs as a widget"""
    def __init__(self, parent=None, width:float=5, height:float=4, dpi:int=75):
        """Creates an empty figure with axes and fig as parameters"""
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.fig = fig
        super(MplCanvas, self).__init__(fig)


###
if __name__ == "__main__":
    os.system('clear')
    print(f"Starting program at {time.strftime('%H:%M:%S')}")
    initial = time.time()
    app = QApplication([])
    window=Window()
    window.show()
    PySeg(model=evaluateExpression, view=window)
    sys.exit(app.exec())