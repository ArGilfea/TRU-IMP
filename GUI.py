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
from GUI_parts.ParamWindow import ParamWindow
import time
###
import numpy as np
import time
import matplotlib.pyplot as plt
###
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QEventLoop
from functools import partial
###
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
###
size_Image = 200

class Window(QMainWindow):
    def _createButtons(self):
        pass      
    def _createStatusBar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)      
        self.statusBar.showMessage("Nothing started")
    def _createInfoParam(self):
        subWidget = QWidget()
        layout = QHBoxLayout()
        subWidget.setLayout(layout)
        self.btn = QPushButton("Info")
        self.btn.clicked.connect(self.on_button_clicked_infos)
        self.btn.setToolTip("Displays the infos of the current loaded acquisition")
        btn_param = QPushButton("Parameters")
        btn_segm = QPushButton("Segment")
        btn_param.setToolTip("Displays the parameters to resize the acquisition or to set up for the segmentations")
        btn_param.clicked.connect(self.open_parameters)
        btn_segm.clicked.connect(self.run_segm)
        layout.addWidget(btn_param)
        layout.addWidget(self.btn)  
        layout.addWidget(btn_segm)
        self.generalLayout.addWidget(subWidget,0,3)         
    def _createExitButton(self,line=7):
        self.exit = QPushButton("Exit")
        self.exit.clicked.connect(self.close)
        self.generalLayout.addWidget(self.exit,line,3)  
    def _createExtractDock(self,line=0):
        subWidget = QWidget()
        msg_extract = QLabel("Path: ")
        source = QLineEdit()
        btn_extr = QPushButton("Extract")
        btn_load = QPushButton("Load")
        btn_browse = QPushButton("Browse")
        source.setText("/Users/philippelaporte/Desktop/Programmation/Python/Data/Fantome_6_1min_comp_2_I_k_all.pkl")
        source.setText("/Users/philippelaporte/Desktop/FantDYN9/PET-AC-DYN-1-MIN/")
        source.setText("/Users/philippelaporte/Desktop/Fantome_9_1min.pkl")
        btn_extr.clicked.connect(partial(self.extract_button,source,"d"))
        btn_load.clicked.connect(partial(self.load_button,source))
        btn_browse.clicked.connect(partial(self.browse_button_file,source))

        layout = QHBoxLayout()
        subWidget.setLayout(layout)
        layout.addWidget(btn_browse)
        layout.addWidget(btn_extr)
        layout.addWidget(btn_load)

        self.generalLayout.addWidget(msg_extract,line,0)  
        self.generalLayout.addWidget(source,line,1)           
        self.generalLayout.addWidget(subWidget,line,2)  
    def _createSavingDock(self,line=2):
        subWidget1 = QWidget()
        subWidget2 = QWidget()
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        subWidget1.setLayout(layout1)
        subWidget2.setLayout(layout2)

        msg_save = QLabel("Path: ")
        path = QLineEdit()
        path_name = QLineEdit()
        path.setText("")
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(partial(self.save_button,path,path_name))
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(partial(self.browse_button_directory,path))

        layout1.addWidget(path)
        layout1.addWidget(path_name)
        layout2.addWidget(btn_browse)
        layout2.addWidget(btn_save)

        self.generalLayout.addWidget(msg_save,line,0)  
        self.generalLayout.addWidget(subWidget1,line,1)  
        self.generalLayout.addWidget(subWidget2,line,2)  
    def _createImageDisplay(self,line=4):
        self.showFocus = False
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
        self.axial.setMinimumSize(size_Image,size_Image)
        self.coronal.setMinimumSize(size_Image,size_Image)
        self.sagittal.setMinimumSize(size_Image,size_Image)
        self.generalLayout.addWidget(msg_Image,line,0)  
        self.generalLayout.addWidget(msg_Axial,line-1,1)
        self.generalLayout.addWidget(msg_Sagittal,line-1,2)
        self.generalLayout.addWidget(msg_Coronal,line-1,3)
        self.generalLayout.addWidget(self.axial,line,1)
        self.generalLayout.addWidget(self.sagittal,line,2)
        self.generalLayout.addWidget(self.coronal,line,3)
    def _createImageDisplayType(self,line=2):
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
        self.generalLayout.addWidget(self.ImageViewCombo,line,3)
    def _createImageDisplayBars(self,line=5):
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
        try:
            self.sliderAcq.setMinimum(0);self.sliderAcq.setMaximum(self.Image.nb_acq-1)
            self.sliderAxial.setMinimum(0);self.sliderAxial.setMaximum(self.Image.nb_slice-1)
            self.sliderSagittal.setMinimum(0);self.sliderSagittal.setMaximum(self.Image.width-1)
            self.sliderCoronal.setMinimum(0);self.sliderCoronal.setMaximum(self.Image.length-1)
            self.sliderSegm.setMinimum(-1);self.sliderSegm.setMaximum(self.Image.voi_counter-1)
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
        self.checkBoxMsgFocus = QLabel("Focus:")

        self.sliderAcqValue = QLineEdit()
        self.sliderAxialValue = QLineEdit()
        self.sliderSagittalValue = QLineEdit()
        self.sliderCoronalValue = QLineEdit()
        self.sliderSegmValue = QLineEdit()
        self.checkBoxFocus = QCheckBox()
        self.checkBoxLog = QCheckBox()
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
            self.checkBoxFocus.stateChanged.connect(self.set_value_focus)
            self.checkBoxLog.stateChanged.connect(self.set_value_log)
        except:
            pass
        checkBoxMsglog = QLabel("log:")

        sublayout.addWidget(self.checkBoxMsgFocus,0,0)
        sublayout.addWidget(self.checkBoxFocus,0,1)
        sublayout.addWidget(checkBoxMsglog,1,0)
        sublayout.addWidget(self.checkBoxLog,1,1)
        subWidget.setMinimumHeight(40)
        subWidget.setContentsMargins(0,0,0,0)
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
        self.generalLayout.addWidget(subWidget,line,3)
        self.generalLayout.addWidget(self.slider_widget,line,1)
        self.slider_widget.resize(500,500)
    def _createTACImage(self,line=5):
        self.TACImage = MplCanvas(self, width=5, height=4, dpi=75)
        self.TACImage.setMinimumSize(size_Image,size_Image)
        self.base_TAC_axes()
        self.generalLayout.addWidget(self.TACImage,line,2)
    def _create1DImage(self,line = 6):
        label = QLabel("Slices")
        self.AxialImage1D = MplCanvas(self,width=5,height=4,dpi=75)
        self.SagittalImage1D = MplCanvas(self,width=5,height=4,dpi=75)
        self.CoronalImage1D = MplCanvas(self,width=5,height=4,dpi=75)
        self.AxialImage1D.setMinimumSize(size_Image,size_Image)
        self.SagittalImage1D.setMinimumSize(size_Image,size_Image)
        self.CoronalImage1D.setMinimumSize(size_Image,size_Image)

        self.base_1D_axes()

        self.generalLayout.addWidget(label,line,0)
        self.generalLayout.addWidget(self.AxialImage1D,line,1)
        self.generalLayout.addWidget(self.SagittalImage1D,line,2)
        self.generalLayout.addWidget(self.CoronalImage1D,line,3)
    def _createErrorMessage(self,message:str=""):
        alert = QMessageBox()
        if message =="":
            alert.setText("An error occurred")
        else:
            alert.setText(message)
        alert.exec()
    def set_value_slider(self,slider:QSlider,lineedit:QLineEdit):
        lineedit.setText(str(slider.value()))
        self.update_all()
        return slider.value()
    def set_value_focus(self):
        if self.checkBoxFocus.isChecked() == True:
            self.showFocus = True
        else:
            self.showFocus = False
        self.update_all()
    def set_value_log(self):
        if self.checkBoxLog.isChecked() == True:
            self.showLog = True
        else:
            self.showLog = False
        self.update_all()
    def set_value_line_edit(self,slider:QSlider,lineedit:QLineEdit):
        try:
            lineedit.setText(f"{int(lineedit.text())}")
        except:
            lineedit.setText("0")
        try:
            slider.setValue(int(lineedit.text()))
        except:
            slider.setValue(0)
        self.update_all()
    def combo_box_changed(self):
        self.view = self.ImageViewCombo.currentText()
        if self.view in ["Slice","Flat","Segm. Slice","Segm. Flat"]:
            self.view_range = "All"
        else:
            self.view_range = "Sub"
        self.update_all()
    def open_parameters(self):
        try:
            window = ParamWindow(self.parameters,self)
            window.show()
        except:
            self._createErrorMessage()
    def run_segm(self):
        try:
            initial = time.time()
            if self.parameters.SegmType == "ICM":
                self.Image.VOI_ICM(acq=20,alpha=self.parameters.alpha,subinfo=self.parameters.subImage[1:,:],
                                    max_iter=self.parameters.max_iter,max_iter_kmean=self.parameters.max_iter_kmean,
                                    verbose=self.parameters.verbose,save=self.parameters.SaveSegm,
                                    do_moments=self.parameters.doMoments,do_stats=self.parameters.doStats)
            else:
                pass
            self.displayStatus(f"{self.parameters.SegmType} segmentation",initial)
            self.update_segm()
        except:
            self._createErrorMessage("Unable to run the segmentation")
    def update_all(self):
        self.update_TAC()
        self.update_1D()
        self.update_view()
        self.update_segm()
    def update_segm(self):
        self.sliderSegm.setMaximum(self.Image.voi_counter-1)
    def update_TAC(self):
        try:
            self.TACImage.axes.cla()
            values = [self.sliderAcq.value(),self.sliderAxial.value(),self.sliderCoronal.value(),self.sliderSagittal.value()]
            x_axis = self.Image.time
            if self.sliderSegm.value() >= 0:
                y_axis = self.Image.voi_statistics[self.sliderSegm.value()]
                self.TACImage.axes.plot(x_axis,y_axis,color='b')
            else:
                y_axis = self.Image.Image[:,values[1],values[2],values[3]]
                self.TACImage.axes.plot(x_axis,y_axis,color='b')
            if self.showFocus:
                self.TACImage.axes.axvline(self.Image.time[values[0]],color='r')
            self.base_TAC_axes()
            self.TACImage.draw()                
        except:
            pass
    def update_1D(self):
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
                self.SagittalImage1D.axes.plot(np.arange(subI[2,0],subI[2,1]+1),self.Image.Image[values[0],values[1],values[2],subI[2,0]:subI[2,1]+1])
                self.CoronalImage1D.axes.plot(np.arange(subI[3,0],subI[3,1]+1),self.Image.Image[values[0],values[1],subI[3,0]:subI[3,1]+1,values[3]])
 
            if self.showFocus:
                self.AxialImage1D.axes.axvline(values[1],color='r')
                self.SagittalImage1D.axes.axvline(values[3],color='r')
                self.CoronalImage1D.axes.axvline(values[2],color='r')
            self.base_1D_axes()
            self.AxialImage1D.draw()
            self.SagittalImage1D.draw()
            self.CoronalImage1D.draw()
        except:
            pass
    def update_sliders(self):
        if self.view_range == "All":
            self.sliderAcq.setMinimum(0);self.sliderAcq.setMaximum(self.Image.nb_acq-1)
            self.sliderAxial.setMinimum(0);self.sliderAxial.setMaximum(self.Image.nb_slice-1)
            self.sliderSagittal.setMinimum(0);self.sliderSagittal.setMaximum(self.Image.width-1)
            self.sliderCoronal.setMinimum(0);self.sliderCoronal.setMaximum(self.Image.length-1)
        else:
            subI = self.parameters.subImage
            self.sliderAcq.setMinimum(subI[0,0]);self.sliderAcq.setMaximum(subI[0,1]-1)
            self.sliderAxial.setMinimum(subI[1,0]);self.sliderAxial.setMaximum(subI[1,1]-1)
            self.sliderSagittal.setMinimum(subI[3,0]);self.sliderSagittal.setMaximum(subI[3,1]-1)
            self.sliderCoronal.setMinimum(subI[2,0]);self.sliderCoronal.setMaximum(subI[2,1]-1)
    def base_TAC_axes(self):
        self.TACImage.axes.set_title("TAC");self.TACImage.axes.grid()
        self.TACImage.axes.set_xlabel("Time");self.TACImage.axes.set_ylabel("Signal")
    def base_1D_axes(self):
        self.AxialImage1D.axes.set_title("Axial Slice");self.AxialImage1D.axes.grid()
        self.AxialImage1D.axes.set_xlabel("Voxel");self.AxialImage1D.axes.set_ylabel("Signal")
        self.SagittalImage1D.axes.set_title("Axial Slice");self.SagittalImage1D.axes.grid()
        self.SagittalImage1D.axes.set_xlabel("Voxel");self.SagittalImage1D.axes.set_ylabel("Signal")
        self.CoronalImage1D.axes.set_title("Axial Slice");self.CoronalImage1D.axes.grid()
        self.CoronalImage1D.axes.set_xlabel("Voxel");self.CoronalImage1D.axes.set_ylabel("Signal")
    def update_view(self):
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
                """
        return a
    def on_button_clicked_infos(self):
        try:
            self._createErrorMessage(self.show_infos_acq())
        except:
            self._createErrorMessage("No file uploaded")
    def extract_button(self,source):
        initial = time.time()
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
    def load_button(self,source):
        initial = time.time()
        self.Image = PF.pickle_open(source.text())
        self.name = self.Image.version
        self.displayStatus("File loading", initial)
        self._createImageDisplay()
        self._createImageDisplayBars()
        self.parameters = GUIParameters(self.Image)
    def browse_button_directory(self,source:QLineEdit):
        text =  QFileDialog.getExistingDirectory()
        source.setText(text+"/")
    def browse_button_file(self,source:QLineEdit):
        text = QFileDialog.getOpenFileName(self)
        source.setText(text[0])
    def save_button(self,path:QLineEdit,path_name:QLineEdit):
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
        self.BUTTON_SIZE = 40
        self.DISPLAY_HEIGHT = 35
        super().__init__(parent=None)
        self.setMinimumSize(900, 800)
        self.setWindowTitle("My GUI")
        self.generalLayout = QGridLayout()
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)
        self._createExtractDock()
        #self._createLoadingDock()
        self._createSavingDock()
        self._createInfoParam()
        self._createImageDisplay()
        self._createImageDisplayType()
        self._createImageDisplayBars()
        self._createTACImage()
        self._create1DImage()
        self._createStatusBar()
        self._createExitButton() 
 
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
    def __init__(self, parent=None, width:float=5, height:float=4, dpi:int=75):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
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