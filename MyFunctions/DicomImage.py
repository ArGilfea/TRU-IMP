import numpy as np
from scipy.optimize import curve_fit
from skimage import feature
from skimage import dtype_limits
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import time
from numba import jit
from dynesty import NestedSampler
from dynesty import plotting as dyplot
import pickle
import MyFunctions.Statistic_Functions as SF
import os
from scipy import ndimage

try:
    import Data.util as util
except:
    import sys
    import os

    current = os.path.dirname(os.path.realpath(__file__))
    
    parent = os.path.dirname(current)

    sys.path.append(parent)
    
    import Data.util as util

class DicomImage(object):
    """
    Contains an image from Nuclear Medicine with many functions to compute segmentations, statistics, parameters, and outputs images.
    """
    def __init__(self,Image:np.ndarray,time:list = [0],name:str='',rescaleSlope:list = [1],rescaleIntercept:list = [0],
                voxel_thickness:float=1,voxel_width:float=1,voxel_length:float=1,time_scale:str='min',
                sliceAxis: np.ndarray = np.array([0]), widthAxis: np.ndarray = np.array([0]), lengthAxis: np.ndarray = np.array([0]),
                flat_images:bool=False,units:str='', radionuclide = "", radiopharmaceutical: str = "",
                mass:int = 1,dose:float = 0,Description:str=''):
        #General Info
        self.version = '1.1.0'
        self.voi_methods = ["Ellipsoid","Threshold","Canny Contour","Canny Filled",
                            "Filled","k Means (2)","ICM (2)"]
        self.pharmaco_models = ["2-compartment"]
        #Image Specific Info
        self.name = name
        self.Description = Description
        self.Image = Image
        self.nb_acq = Image.shape[0]
        self.nb_slice = Image.shape[1]
        self.width = Image.shape[2]
        self.length = Image.shape[3]
        self.sliceAxis = sliceAxis
        self.widthAxis = lengthAxis
        self.lengthAxis = widthAxis
        self.rescaleSlope = rescaleSlope
        self.rescaleIntercept = rescaleIntercept
        self.voxel_thickness = voxel_thickness
        self.voxel_width = voxel_width
        self.voxel_length = voxel_length
        self.voxelSize = np.array([self.voxel_thickness, self.voxel_width, self.voxel_length])
        self.voxel_volume = voxel_thickness*voxel_width*voxel_length
        self.Instances = self.nb_acq*self.nb_slice*self.width*self.length
        self.mass = mass
        self.dose = dose
        if np.array(time).size != Image.shape[0]:
            self.time = np.zeros((self.nb_acq))
        else:
            self.time = time
        self.time_scale = time_scale
        self.units = units
        self.radioNuclideInit = radionuclide
        self.radioNuclide = self.FindRadioNuclide()
        self.radiopharmaceutical = radiopharmaceutical
        self.voi_counter = 0
        self.voi = {}
        self.voi_fuzzy = {}
        self.energies = {}
        self.mus = {}
        self.fFactorsFillingAxisX = {}
        self.fFactorsFillingAxisY = {}
        self.voi_voxels = []
        self.voi_name = []
        self.voi_center_of_mass = []
        self.voi_moment_of_inertia = []
        self.voi_statistics = []
        self.voi_statistics_counter = 0
        self.voi_statistics_avg = []
        self.voi_statistics_std = []
        self.bayesian_results_avg = [] #If breaks, remove np.array
        self.bayesian_results_e_up = []
        self.bayesian_results_e_down = []
        self.bayesian_counter = 0
        self.bayesian_dynesty_counter = 0
        self.bayesian_graphs_runplot = {}
        self.bayesian_graphs_traceplot = {}
        self.bayesian_graphs_cornerplot = {}
        self.axial_flats = np.zeros((self.nb_acq,self.width,self.length))
        self.coronal_flats = np.zeros((self.nb_acq,self.nb_slice,self.length))
        self.sagittal_flats = np.zeros((self.nb_acq,self.nb_slice,self.width))
        if flat_images: #Added in 1.1.2
            for i in range(self.nb_acq):
                self.axial_flats[i,:,:] = self.axial_flat(i)
                self.sagittal_flats[i,:,:] = self.sagittal_flat(i)
                self.coronal_flats[i,:,:] = self.coronal_flat(i)
        self.progress_log = ""

    def select_acq(self,acq:int = -1): #Done in 1.1
        """Returns a specific 3D (spatial) volume image, determined by the key input.\n
        Keyword arguments:\n
        acq -- the timeframe of interest (default -1)
        """
        region = np.zeros((self.nb_slice,self.width,self.length))
        if(acq>= 0) and (acq < self.nb_acq):
            region = self.Image[acq,:,:,:]
        return region

    def update_log(self,message:str):
        """This will print a message to the monitor and also save it in the progress log"""
        print(message)
        self.progress_log += "\n" + message
############################################################
#                                                          #
# This section deals with the 2-D images                   #
#                                                          #
############################################################
    def axial_flat(self,acq:int=-1,counter:int=-1,save:bool=False): #Added in 1.1.1
        """
        Returns an image flat, either of the image itself or from one segmentation scheme.\n
        Keyword arguments:\n
        acq -- acquisition from which to take the flat, if > -1 (default -1)\n
        acq -- segm. counter from which to take the flat, if > -1 (default -1)\n
        save -- Save the computed flat image, if from an acq (default False)\n
        """
        flat_image = np.zeros((self.width,self.length))
        if counter < 0:
            region = self.select_acq(acq)
            for i in range(self.width):
                for j in range(self.length):
                    flat_image[i,j] = np.sum(region[:,i,j])/self.nb_slice
            if save:
                self.axial_flats[acq,:,:]=flat_image
        else:
            for i in range(self.width):
                for j in range(self.length):
                    flat_image[i,j] = np.sum(self.voi[f"{counter}"][:,i,j])/self.nb_slice
        return flat_image
    def coronal_flat(self,acq:int=-1,counter:int=-1,save:bool=False): #Added in 1.1.1
        """
        Returns an image flat, either of the image itself or from one segmentation scheme.\n
        Keyword arguments:\n
        acq -- acquisition from which to take the flat, if > -1 (default -1)\n
        acq -- segm. counter from which to take the flat, if > -1 (default -1)\n
        save -- Save the computed flat image, if from an acq (default False)\n
        """
        flat_image = np.zeros((self.nb_slice,self.length))
        if counter < 0:
            region = self.select_acq(acq)
            for i in range(self.nb_slice):
                for j in range(self.length):
                    flat_image[i,j] = np.sum(region[i,:,j])/self.width
            if save:
                self.coronal_flats[acq,:,:]=flat_image
        else:
            for i in range(self.nb_slice):
                for j in range(self.length):
                    flat_image[i,j] = np.sum(self.voi[f"{counter}"][i,:,j])/self.width
        return flat_image
    def sagittal_flat(self,acq:int=-1,counter:int=-1,save:bool=False): #Added in 1.1.1
        """
        Returns an image flat, either of the image itself or from one segmentation scheme.\n
        Keyword arguments:\n
        acq -- acquisition from which to take the flat, if > -1 (default -1)\n
        acq -- segm. counter from which to take the flat, if > -1 (default -1)\n
        save -- Save the computed flat image, if from an acq (default False)\n
        """
        flat_image = np.zeros((self.nb_slice,self.width))
        if counter < 0:
            region = self.select_acq(acq)
            for i in range(self.nb_slice):
                for j in range(self.width):
                    flat_image[i,j] = np.sum(region[i,j,:])/self.length
            if save:
                self.sagittal_flats[acq,:,:]=flat_image
        else:
            for i in range(self.nb_slice):
                for j in range(self.width):
                    flat_image[i,j] = np.sum(self.voi[f"{counter}"][i,j,:])/self.length
        return flat_image
    def show_flats(self,acq:int=-2,key:int=-2,physical:bool = False, name:str=''): #Done in 1.2.1
        """Outputs three flat images in one figure of the three cuts (axial, sagittal and coronal) 
        of a given timeframe or voi.\n
        The specific image flattened and shown is given by the argument which is greater or equal to 0.
        (There must only one, otherwise an error is raised).\n
        Keyword arguments:\n
        acq -- the timeframe of interest (default -2)\n
        key -- the VOI of interest (default -2). (-1 for all VOIs)\n
        physical -- show the physial dimensions of the acquisitions (default False)\n
        name -- optional name for the graphs (default '')\n
        """
        if ((acq >= 0 and key >= 0) or (acq < -1 and key < -1)):
            raise Exception("Key xor Acq argument must be greater than 0 to select a valid image to check")
        if key >= self.voi_counter:
            raise Exception("Key argument must be lower than the number of VOIs")
        if physical:
            sliceAxis = self.sliceAxis
            widthAxis = self.widthAxis
            lengthAxis = self.lengthAxis
        else:
            sliceAxis = np.arange(self.nb_slice)
            widthAxis = np.arange(self.width)
            lengthAxis = np.arange(self.length)
        if acq >= 0:
            fig, axs = plt.subplots(2,2)
            axs[0,0].pcolormesh(lengthAxis,widthAxis,self.axial_flat(acq=acq));axs[0,0].set_title("Axial");axs[0,0].set_xlabel("y (voxels)");axs[0,0].set_ylabel("z (voxels)")
            axs[1,0].pcolormesh(widthAxis,sliceAxis,self.sagittal_flat(acq=acq));axs[1,0].set_title("Sagittal");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("y (voxels)")
            axs[0,1].pcolormesh(lengthAxis,sliceAxis,self.coronal_flat(acq=acq));axs[0,1].set_title("Coronal");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("z (voxels)")
            fig.suptitle(f"Time Acquisition {acq} {name}")
        elif key >= 0:
            fig, axs = plt.subplots(2,2)
            axs[0,0].pcolormesh(lengthAxis,widthAxis,self.axial_flat(counter = key));axs[0,0].set_title("Axial");axs[0,0].set_xlabel("y (voxels)");axs[0,0].set_ylabel("z (voxels)")
            axs[1,0].pcolormesh(widthAxis,sliceAxis,self.sagittal_flat(counter = key));axs[1,0].set_title("Sagittal");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("y (voxels)")
            axs[0,1].pcolormesh(lengthAxis,sliceAxis,self.coronal_flat(counter = key));axs[0,1].set_title("Coronal");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("z (voxels)")
            fig.suptitle(f"VOI {key} {name} {self.voi_name[key]}")
        elif key == -1:
            for i in range(self.voi_counter):
                fig, axs = plt.subplots(2,2)
                axs[0,0].pcolormesh(lengthAxis,widthAxis,self.axial_flat(counter = i));axs[0,0].set_title("Axial");axs[0,0].set_xlabel("y (voxels)");axs[0,0].set_ylabel("z (voxels)")
                axs[1,0].pcolormesh(widthAxis,sliceAxis,self.sagittal_flat(counter = i));axs[1,0].set_title("Sagittal");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("y (voxels)")
                axs[0,1].pcolormesh(lengthAxis,sliceAxis,self.coronal_flat(counter = i));axs[0,1].set_title("Coronal");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("z (voxels)")
                fig.suptitle(f"VOI {i} {name} {self.voi_name[i]}")                         
    def show_point(self,point:list = [-1,0,0,0],star:bool=False,
                   log:bool=False, physical: bool = False,
                   sub_im:list = [[-1,-1],[-1,-1],[-1,-1]]): #Done in 1.2.1
        """Outputs three images in one figure of the three cuts (axial, sagittal and coronal) 
        at a given acquisition and spatial point.\n
        The specific image flattened and shown is given by the argument which is greater or equal to 0.
        (There must only one, otherwise an error is raised).\n
        Keyword arguments:\n
        point -- point from which to look in the three planes (default [-1,0,0,0])\n
        star -- indicates with a star the location of the point (default False)\n
        log -- apply a log_e on all voxels of the image, which is useful for low contrast images (default True)\n
        physical -- show the physial dimensions of the acquisitions (default False)\n
        sub_im -- show only part of the image (default [[-1,-1],[-1,-1],[-1,-1]])\n
        """
        sub_im = np.array(sub_im)
        if (point[0]<0 or point[0] >= self.nb_acq):
            raise Exception("Acquisition must be between 0 and the number of acquisitions")
        if (point[1]<0 or point[1]>= self.nb_slice) or (point[2]<0 or point[2]>= self.width) or (point[3]<0 or point[3]>= self.length):
            raise Exception("Spatial values must be within the image")
        fig, axs = plt.subplots(2,2)
        if physical:
            sliceAxis = self.sliceAxis
            widthAxis = self.widthAxis
            lengthAxis = self.lengthAxis
        else:
            sliceAxis = np.arange(self.nb_slice)
            widthAxis = np.arange(self.width)
            lengthAxis = np.arange(self.length)
        if np.sum(sub_im < 0):
            if log:
                axs[0,0].pcolormesh(lengthAxis,widthAxis,np.log(self.Image[point[0],point[1],:,:]));axs[0,0].set_title("Axial")
                axs[1,0].pcolormesh(widthAxis,sliceAxis,np.log(self.Image[point[0],:,:,point[3]]));axs[1,0].set_title("Sagittal")
                axs[0,1].pcolormesh(lengthAxis,sliceAxis,np.log(self.Image[point[0],:,point[2],:]));axs[0,1].set_title("Coronal")
            else:
                axs[0,0].pcolormesh(lengthAxis,widthAxis,self.Image[point[0],point[1],:,:]);axs[0,0].set_title("Axial")
                axs[1,0].pcolormesh(widthAxis,sliceAxis,self.Image[point[0],:,:,point[3]]);axs[1,0].set_title("Sagittal")
                axs[0,1].pcolormesh(lengthAxis,sliceAxis,self.Image[point[0],:,point[2],:]);axs[0,1].set_title("Coronal")
            fig.suptitle(f"Three slice around point: {point}")      
        else:
            if log:
                axs[0,0].pcolormesh(lengthAxis[sub_im[2,0]:sub_im[2,1]],widthAxis[sub_im[1,0]:sub_im[1,1]],
                                    np.log(self.Image[point[0],point[1],sub_im[1,0]:sub_im[1,1],sub_im[2,0]:sub_im[2,1]]));axs[0,0].set_title("Axial")
                axs[1,0].pcolormesh(widthAxis[sub_im[1,0]:sub_im[1,1]],sliceAxis[sub_im[0,0]:sub_im[0,1]],
                                    np.log(self.Image[point[0],sub_im[0,0]:sub_im[0,1],sub_im[1,0]:sub_im[1,1],point[3]]));axs[1,0].set_title("Sagittal")
                axs[0,1].pcolormesh(lengthAxis[sub_im[2,0]:sub_im[2,1]],sliceAxis[sub_im[0,0]:sub_im[0,1]],
                                    np.log(self.Image[point[0],sub_im[0,0]:sub_im[0,1],point[2],sub_im[2,0]:sub_im[2,1]]));axs[0,1].set_title("Coronal")
            else:
                axs[0,0].pcolormesh(lengthAxis[sub_im[2,0]:sub_im[2,1]],widthAxis[sub_im[1,0]:sub_im[1,1]],
                                    self.Image[point[0],point[1],sub_im[1,0]:sub_im[1,1],sub_im[2,0]:sub_im[2,1]]);axs[0,0].set_title("Axial")
                axs[1,0].pcolormesh(widthAxis[sub_im[1,0]:sub_im[1,1]],sliceAxis[sub_im[0,0]:sub_im[0,1]],
                                    self.Image[point[0],sub_im[0,0]:sub_im[0,1],sub_im[1,0]:sub_im[1,1],point[3]]);axs[1,0].set_title("Sagittal")
                axs[0,1].pcolormesh(lengthAxis[sub_im[2,0]:sub_im[2,1]],sliceAxis[sub_im[0,0]:sub_im[0,1]],
                                    self.Image[point[0],sub_im[0,0]:sub_im[0,1],point[2],sub_im[2,0]:sub_im[2,1]]);axs[0,1].set_title("Coronal")
            fig.suptitle(f"Three slice around point: {point} for a reduced image around ({sub_im[0,0]}-{sub_im[0,1]},{sub_im[1,0]}-{sub_im[1,1]},{sub_im[2,0]}-{sub_im[2,1]})")    
        if star:
            axs[0,0].plot(lengthAxis[point[3]],widthAxis[point[2]],'*',markersize = 6,color='y') 
            axs[1,0].plot(widthAxis[point[2]],sliceAxis[point[1]],'*',markersize = 6,color='y') 
            axs[0,1].plot(lengthAxis[point[3]],sliceAxis[point[1]],'*',markersize = 6,color='y') 
    def show_curves(self,point:list = [-1,0,0,0]): #Done in 1.2.1
        """Outputs three images in one figure of the three cuts (axial, sagittal and coronal) 
        at a given acquisition and spatial point.\n
        The specific image flattened and shown is given by the argument which is greater or equal to 0.
        (There must only one, otherwise an error is raised).\n
        Keyword arguments:\n
        point -- point from which to look in the three planes (default [-1,0,0,0])
        """
        if (point[0]<0 or point[0] >= self.nb_acq):
            raise Exception("Acquisition must be between 0 and the number of acquisitions")
        if (point[1]<0 or point[1]>= self.nb_slice) or (point[2]<0 or point[2]>= self.width) or (point[3]<0 or point[3]>= self.length):
            raise Exception("Spatial values must be within the image")
        fig, axs = plt.subplots(2,2)
        axs[0,0].plot(self.Image[point[0],point[1],point[2],:]);axs[0,0].set_title("Axial");axs[0,0].axvline(x=point[3],color='r')
        axs[1,0].plot(self.Image[point[0],point[1],:,point[3]]);axs[1,0].set_title("Sagittal");axs[1,0].axvline(x=point[2],color='r')
        axs[0,1].plot(self.Image[point[0],:,point[2],point[3]]);axs[0,1].set_title("Coronal");axs[0,1].axvline(x=point[1],color='r')
        axs[1,1].plot(self.Image[:,point[1],point[2],point[3]]);axs[1,1].set_title("Temporal");axs[1,1].axvline(x=point[0],color='r')
        axs[0,0].set_xlabel("Axial Length");axs[0,0].set_ylabel(self.units)
        axs[1,0].set_xlabel("Sagital Length");axs[1,0].set_ylabel(self.units)
        axs[0,1].set_xlabel("Coronal Length");axs[0,1].set_ylabel(self.units)
        axs[1,1].set_xlabel("Time (min)");axs[1,1].set_ylabel(self.units)
        fig.suptitle(f"Six axes around point: {point}")    
    
    def show_coeff(self,keys:int=-1,type:str='Dice',title:str=''): #Done in 2.0.0
        """
        Shows the coefficient of kind 'type' for the segmentations given by 'keys'.\n
        Keyword arguments:\n
        keys -- indices of the segmentation for which the coefficient is to be show (default -1, i.e. all)\n
        type -- type of coefficient to show: Dice, Jaccard, etc. (default Dice)\n
        title -- name for the title of the plot (default '')
        """
        if isinstance(keys,int):
            if keys == -1:
                keys = np.arange(self.voi_counter)
        else:
            if not isinstance(keys,(list,np.ndarray)):
                raise Exception("Invalid input for 'keys'. Must be a list or an np.ndarray.")
            keys = np.array(keys)
        fig,ax = plt.subplots()
        if type =='Dice':
            plt.pcolormesh(self.dice_all[keys][:,keys])
        elif type == 'Jaccard':
            plt.pcolormesh(self.jaccard_all[keys][:,keys])
        else:
            raise Exception("Invalid choice of type of coefficient.")
        plt.suptitle(f"{type} coefficients for {title}")
        plt.colorbar();plt.xlabel("Segmentation 1");plt.ylabel("Segmentation 2")
        ax.xaxis.set(ticks=np.arange(0.5, keys.shape[0]),ticklabels=keys)
        ax.yaxis.set(ticks=np.arange(0.5, keys.shape[0]),ticklabels=keys)
        return fig
############################################################
#                                                          #
# This section deals with image modifications              #
#                                                          #
############################################################
    def image_cut(self,dim_sub:np.ndarray=np.array([[0,0],[0,0],[0,0]])):
        """
        Take a spatial sub image from the whole acquisition.\n
        Keyword arguments:\n
        dim_sub -- section of the whole image to take (default np.array([[0,0],[0,0],[0,0]]))\n
        """
        new_image = np.zeros_like(self.Image)
        for t in range(self.nb_acq):
            for i in range(int(dim_sub[0][0]),int(dim_sub[0][1])):
                for j in range(int(dim_sub[1][0]),int(dim_sub[1][1])):
                    for k in range(int(dim_sub[2][0]),int(dim_sub[2][1])):
                        new_image[t,i,j,k] = self.Image[t,i,j,k]
        return new_image
    
    def flip_Image(self, axis:int):
        """
        Flips the whole image and segmentations according to one
        of the three spatial dimensions.\n
        Keyword arguments:\n
        axis -- axis along which to flip. This will correspond to one of the 3 spatial axes\n
        """
        newImage = np.zeros_like(self.Image)
        if axis == 1:
            for i in range(self.nb_slice):
                newImage[:,i,:,:] = self.Image[:,self.nb_slice-i-1,:,:]
            self.Image = np.copy(newImage)
            for i in range(self.voi_counter):
                newSegm = np.zeros_like(self.voi[f"{i}"])
                for j in range(self.nb_slice):
                    newSegm[j,:,:] = self.voi[f"{i}"][self.nb_slice-j-1,:,:]
                self.voi[f"{i}"] = np.copy(newSegm)
            #self.sliceAxis = self.sliceAxis[::-1]
        elif axis == 2:
            for i in range(self.width):
                newImage[:,:,i,:] = self.Image[:,:,self.width-i-1,:]
            self.Image = np.copy(newImage)
            for i in range(self.voi_counter):
                newSegm = np.zeros_like(self.voi[f"{i}"])
                for j in range(self.width):
                    newSegm[:,j,:] = self.voi[f"{i}"][:,self.width-j-1,:]
                self.voi[f"{i}"] = np.copy(newSegm)
            #self.widthAxis = self.widthAxis[::-1]
        elif axis == 3:
            for i in range(self.length):
                newImage[:,:,:,i] = self.Image[:,:,:,self.length-i-1]
            self.Image = np.copy(newImage)
            for i in range(self.voi_counter):
                newSegm = np.zeros_like(self.voi[f"{i}"])
                for j in range(self.length):
                    newSegm[:,:,j] = self.voi[f"{i}"][:,:,self.length-j-1]
                self.voi[f"{i}"] = np.copy(newSegm)
            #self.lengthAxis = self.lengthAxis[::-1]
        else:
            raise Exception(f"Invalid choice of axis. Must be 1, 2, or 3 and {axis} was given")

    def switchAxes_Image(self, axes:list):
        """
        Flips the whole image and segmentations according to one
        of the three spatial dimensions.\n
        Keyword arguments:\n
        axes -- axes to switch. This will correspond to two of the 3 spatial axes\n
        """
        if axes == [1,2]:
            newImage = np.swapaxes(self.Image,1,2)
            self.Image = np.copy(newImage)
            for i in range(self.voi_counter):
                newSegm = np.swapaxes(self.voi[f"{i}"],0,1)
                self.voi[f"{i}"] = np.copy(newSegm)
            tmp = np.copy(self.sliceAxis)
            self.sliceAxis = np.copy(self.widthAxis)
            self.widthAxis = np.copy(tmp)
        elif axes == [1,3]:
            newImage = np.swapaxes(self.Image,1,3)
            self.Image = np.copy(newImage)
            for i in range(self.voi_counter):
                newSegm = np.swapaxes(self.voi[f"{i}"],0,2)
                self.voi[f"{i}"] = np.copy(newSegm)
            tmp = np.copy(self.sliceAxis)
            self.sliceAxis = np.copy(self.lengthAxis)
            self.lengthAxis = np.copy(tmp)
        elif axes == [2,3]:
            newImage = np.swapaxes(self.Image,2,3)
            self.Image = np.copy(newImage)
            for i in range(self.voi_counter):
                newSegm = np.swapaxes(self.voi[f"{i}"],1,2)
                self.voi[f"{i}"] = np.copy(newSegm)
            tmp = np.copy(self.lengthAxis)
            self.lengthAxis = np.copy(self.widthAxis)
            self.widthAxis = np.copy(tmp)
        else:
            raise Exception(f"Invalid choice of axis. Must be 1, 2, or 3 and {axes} was given")
        self.nb_slice = newImage.shape[1]
        self.width = newImage.shape[2]
        self.length = newImage.shape[3]
        
        self.axial_flats = np.zeros((self.nb_acq,self.width,self.length))
        self.coronal_flats = np.zeros((self.nb_acq,self.nb_slice,self.length))
        self.sagittal_flats = np.zeros((self.nb_acq,self.nb_slice,self.width))
        for i in range(self.nb_acq):
            self.axial_flats[i,:,:] = self.axial_flat(i)
            self.sagittal_flats[i,:,:] = self.sagittal_flat(i)
            self.coronal_flats[i,:,:] = self.coronal_flat(i)


    def linear_shift(self,shifts:np.ndarray=np.array([0,0,0]),counter:int = -1,save:bool=True,name:str=''):
        """
        Shift a given VOI linearly according to the input shifts.\n
        Each voxel of the VOI is shifted linearly along the three axes.\n
        Keyword arguments:\n
        shifts -- 3-D distance to shift, in 3-vector form (default [0,0,0])\n
        counter -- segmentation to use for the shift (default -1)\n
        save -- save the VOI if True, else, return it as an output (default True)\n
        name -- name of the new VOI (default '')\n
        """
        if (counter >= 0):
            new_VOI = np.zeros_like(self.voi[f"{counter}"])
            for i in range(np.max([shifts[0],-shifts[0]]),np.min([self.voi[f"{counter}"].shape[0]-shifts[0],self.voi[f"{counter}"].shape[0]+shifts[0]])):
                for j in range(np.max([shifts[1],-shifts[1]]),np.min([self.voi[f"{counter}"].shape[1]-shifts[1],self.voi[f"{counter}"].shape[1]+shifts[1]])):
                    for k in range(np.max([shifts[2],-shifts[2]]),np.min([self.voi[f"{counter}"].shape[2]-shifts[2],self.voi[f"{counter}"].shape[2]+shifts[2]])):
                        new_VOI[i+shifts[0],j+shifts[1],k+shifts[2]] = self.voi[f"{counter}"][i,j,k]
            if save:
                if name == '':
                    self.save_VOI(new_VOI,name=f"linear_shifts_{shifts}")
                else:
                    self.save_VOI(new_VOI,name=f"linear_shifts_{shifts}_{name}")
            else:
                return new_VOI
        else:
            self.update_log(f"Nothing happened, for counter argument ({counter}) is not valid. It needed to be between 0 and {self.voi_counter}")
    def rotation_VOI(self,angles:np.ndarray = ([0,0,0]),axis: np.ndarray = ([-1,0,0]), counter:int= -1, save:bool = True, name: str= ''):
        """
        Rotate a given VOI by given angles around a central axis.\n
        Since rotations are a non-abelian group, the order of composition is important.
        Note that the rotation will first be along the first dimension, then the second and, finaly, the third.
        Plan the angles accordingly.\n
        Keyword arguments:\n
        angles -- angles for the rotations: the first one correspond to the axial, then coronal, then sagittal (default [0,0,0])\n
        axis -- axis around which to do the rotation; if unchanged, will be around the center of mass of the VOI (default [-1,0,0])\n
        counter -- segmentation to use for the shift (default -1)\n
        save -- save the VOI if True, else, return it as an output (default True)\n
        name -- name of the new VOI (default '')\n
        """
        if (counter >= 0):
            new_VOI1 = np.zeros_like(self.voi[f"{counter}"])
            new_VOI2 = np.zeros_like(self.voi[f"{counter}"])
            new_VOI3 = np.zeros_like(self.voi[f"{counter}"])
            old_VOI = self.voi[f"{counter}"]
            if np.sum(axis) < 0:
                axis = np.array(self.voi_center_of_mass[counter]).astype(int)
            if angles[0] > 1e-5 or angles[0] < -1e-5:
                for i in range(new_VOI1.shape[0]):#self.nb_slice):
                    new_VOI1[i,:,:] = self.rotate_slice(slice = old_VOI[i,:,:],center = np.array([axis[1],axis[2]]),angle = angles[0])
            else:
                new_VOI1 = np.copy(old_VOI)
            if angles[2] > 1e-5 or angles[2] < -1e-5:
                for j in range(self.width):
                    new_VOI2[:,j,:] = self.rotate_slice(slice = new_VOI1[:,j,:],center = np.array([axis[0],axis[1]]),angle = angles[2])
            else:
                new_VOI2 = np.copy(new_VOI1)
            if angles[1] > 1e-5 or angles[1] < -1e-5:
                for k in range(self.length):
                    new_VOI3[:,:,k] = self.rotate_slice(slice = new_VOI2[:,:,k],center = np.array([axis[0],axis[2]]),angle = angles[1])
            else:
                new_VOI3 = np.copy(new_VOI2)
            if save:
                if name == '':
                    self.save_VOI(new_VOI3,name=f"rotation_{angles}")
                else:
                    self.save_VOI(new_VOI3,name=f"rotation_{angles}_{name}")
            else:
                return new_VOI3
        else:
            self.update_log(f"Nothing happened, for counter argument ({counter}) is not valid. It needed to be between 0 and {self.voi_counter}")
    def rotate_slice(self,slice : np.ndarray, center: np.ndarray, angle: float) -> np.ndarray:
        """Rotate a slice of an array around a point"""
        rotated_array = np.zeros_like(slice)
        for i in range(slice.shape[0]):
            for j in range(slice.shape[1]):
                new_I = i - center[0]
                new_J = j - center[1]
                new_X = new_I*np.cos(angle)+new_J*np.sin(angle)
                new_Y = -new_I*np.sin(angle)+new_J*np.cos(angle)
                new_X_replaced = new_X + center[0]
                new_Y_replaced = new_Y + center[1]
                if (new_X_replaced > 0 and new_X_replaced < slice.shape[0]) and (new_Y_replaced > 0 and new_Y_replaced < slice.shape[1]):
                    inter_value = self.segm_interpolation_2D(slice,new_X_replaced,new_Y_replaced)
                else:
                    inter_value = 0
                if inter_value > 0.5:
                    rotated_array[i,j] = 1
                else:
                    rotated_array[i,j] = 0
        return rotated_array

    def expand_VOI(self,factors:np.ndarray = ([0,0,0]),axis: np.ndarray = ([-1,0,0]), counter:int= -1, save:bool = True, name: str= ''):
        """
        This function takes a segmentation and expands it around the center of mass.\n
        Plan the angles accordingly.\n
        Keyword arguments:\n
        factors -- factors for the expansion: each factor will be about an axis (default [0,0,0])\n
        axis -- central point around which to do the expansion; if undefined, will be around the center of mass of the VOI (default [-1,0,0])\n
        counter -- segmentation to use for the shift (default -1)\n
        save -- save the VOI if True, else, return it as an output (default True)\n
        name -- name of the new VOI (default '')\n
        """
        if (counter >= 0):
            new_VOI = np.zeros_like(self.voi[f"{counter}"])
            old_VOI = self.voi[f"{counter}"]
            if np.sum(axis) < 0:
                axis = np.array(self.voi_center_of_mass[counter]).astype(int)

            for i in range(new_VOI.shape[0]):
                for j in range(new_VOI.shape[1]):
                    for k in range(new_VOI.shape[2]):
                        #This is done backward. We look at a voxel and the new image.
                        #If it falls within the segmentation of the original VOI, we add it.
                        #Otherwise, no
                        #First, shift the image around the axis
                        x1 = i - axis[0]
                        y1 = j - axis[1]
                        z1 = k - axis[2]
                        #Then, expand (inversely)
                        if factors[0] == 0:
                            factors[0] = 1
                        if factors[1] == 0:
                            factors[1] = 1
                        if factors[2] == 0:
                            factors[2] = 1
                        x2 = x1/factors[0]
                        y2 = y1/factors[1]
                        z2 = z1/factors[2]
                        #Check if it falls within the segmentation
                        x3 = x2 + axis[0]
                        y3 = y2 + axis[1]
                        z3 = z2 + axis[2]
                        if (x3 > 0 and x3 < old_VOI.shape[0]-1) and (y3 > 0 and y3 < old_VOI.shape[1]-1) and (z3 > 0 and z3 < old_VOI.shape[2]-1):
                            box = np.array([old_VOI[int(x3),int(y3),int(z3)],old_VOI[int(x3)+1,int(y3),int(z3)],
                                            old_VOI[int(x3),int(y3)+1,int(z3)],old_VOI[int(x3),int(y3),int(z3)+1],
                                            old_VOI[int(x3)+1,int(y3)+1,int(z3)],old_VOI[int(x3)+1,int(y3),int(z3)+1],
                                            old_VOI[int(x3),int(y3)+1,int(z3)+1],old_VOI[int(x3)+1,int(y3)+1,int(z3)+1]])
                            if np.sum(box) == 8:
                                value = 1
                            elif np.sum(box) == 0:
                                value = 0
                            else:
                                value = self.segm_interpolation_3D(boxArray = box,point = np.array([x2,y2,z2]))
                        else:
                            value = 0
                        #Finaly, return in a usual position
                        if value > 0.5:
                            new_VOI[i,j,k] = 1
            if save:
                if name == '':
                    self.save_VOI(new_VOI,name=f"expansion_{factors}")
                else:
                    self.save_VOI(new_VOI,name=f"expansion_{factors}_{name}")
            else:
                return new_VOI
        else:
            self.update_log(f"Nothing happened, for counter argument ({counter}) is not valid. It needed to be between 0 and {self.voi_counter}")

    def reflection_ROI(self,axis: np.ndarray = ([-1,0,0]), axisNumber: int = 0,counter:int= -1, save:bool = True, name: str= ''):
        """
        This function takes a segmentation and rotates it around the center of mass.\n
        Plan the angles accordingly.\n
        Keyword arguments:\n
        axis -- central point around which to do the expansion; if undefined, will be around the center of mass of the VOI (default [-1,0,0])\n
        axisNumber -- axis around which to rotate the image (default 0)\n
        counter -- segmentation to use for the shift (default -1)\n
        save -- save the VOI if True, else, return it as an output (default True)\n
        name -- name of the new VOI (default '')\n
        """
        if (counter >= 0):
            new_VOI = np.zeros_like(self.voi[f"{counter}"])
            old_VOI = self.voi[f"{counter}"]
            if np.sum(axis) < 0:
                axis = np.array(self.voi_center_of_mass[counter]).astype(int)

            if axisNumber == 0:
                for i in range(old_VOI.shape[0]):
                    if axis[0] + i < old_VOI.shape[0] and axis[0] - i >= 0:
                        if i != axis[0]:
                            new_VOI[axis[0] - i,:,:] = old_VOI[axis[0] + i,:,:]
                            new_VOI[axis[0] + i,:,:] = old_VOI[axis[0] - i,:,:]
                        elif i == axis[0]:
                            new_VOI[i,:,:] = old_VOI[i,:,:]

            elif axisNumber == 1:
                for i in range(old_VOI.shape[1]):
                    if axis[1] + i < old_VOI.shape[1] and axis[1] - i >= 0:
                        if i < axis[1]:
                            new_VOI[:,axis[1] - i,:] = old_VOI[:,axis[1] + i,:]
                            new_VOI[:,axis[1] + i,:] = old_VOI[:,axis[1] - i,:]
                        elif i == axis[1]:
                            new_VOI[:,i,:] = old_VOI[:,i,:]
            elif axisNumber == 2:
                for i in range(old_VOI.shape[2]):
                    if axis[2] + i < old_VOI.shape[2] and axis[2] - i >= 0:
                        if i < axis[2]:
                            new_VOI[:,:,axis[2] - i] = old_VOI[:,:,axis[2] + i]
                            new_VOI[:,:,axis[2] + i] = old_VOI[:,:,axis[2] - i]
                        elif i == axis[2]:
                            new_VOI[:,:,i] = old_VOI[:,:,i]
            else:
                raise Exception(f"Invalid choice of Axis for the Rotation. Choice must be 0, 1, or 2 and it was: {axisNumber}")

            if save:
                if name == '':
                    self.save_VOI(new_VOI,name=f"Reflection around {axis} with axis {axisNumber}")
                else:
                    self.save_VOI(new_VOI,name=f"Reflection around {axis} with axis {axisNumber} {name}")
            else:
                return new_VOI
        else:
            self.update_log(f"Nothing happened, for counter argument ({counter}) is not valid. It needed to be between 0 and {self.voi_counter}")
    def complement_ROI(self,counter:int = -1, save:bool = True, name:str = ''):
        """
        Takes a specific segmentation and keep only the complement, i.e. only what was not part of the initial segmentation.\n
        Keyword arguments:\n
        key -- segmentation key to use (default -1)\n
        save -- save the VOI if True, else, return it as an output (default True)\n
        name -- name of the new VOI (default '')\n
        """
        if (counter >= 0):
            new_VOI = np.zeros_like(self.voi[f"{counter}"])
            old_VOI = self.voi[f"{counter}"]
            for i in range(new_VOI.shape[0]):
                for j in range(new_VOI.shape[1]):
                    for k in range(new_VOI.shape[2]):
                        if old_VOI[i,j,k] == 0:
                            new_VOI[i,j,k] = 1
            if save:
                if name == '':
                    self.save_VOI(new_VOI,name=f"complement")
                else:
                    self.save_VOI(new_VOI,name=f"complement_{name}")
            else:
                return new_VOI        
        else:
            self.update_log(f"Nothing happened, for counter argument ({counter}) is not valid. It needed to be between 0 and {self.voi_counter}")
        
    def linear_shifts_error(self,key:int=-1,order=1,d=1,weight=1,verbose:bool=False):#Done in 2.0.0
        """
        This function takes a specific segmentation and shifts it linearly, saving only the results,
        in order to save memory space.
        Keyword arguments:\n
        key -- segmentation key to use (default -1)\n
        order -- linear shift order (default 1)\n
        d -- distance of the shift (default 1)\n
        weight -- weight for each axis, if compounded [TBA] (default 1)\n
        verbose -- outputs the progress (default False)\n
        """
        initial = time.time()
        if key < 0 or key >= self.voi_counter:
            raise Exception(f"Counter must be between 0 and {self.voi_counter}, whereas here it was {key}.")
        shift_axis = self.axis(order,d)
        stats_curves = np.zeros((shift_axis.shape[0],self.nb_acq))
        for i in range(shift_axis.shape[0]):
            VOI_shifted = self.linear_shift(shift_axis[i,:],counter=key,save=False)
            stats_curves[i,:] = self.VOI_statistics(VOI = VOI_shifted)
            if verbose:
                self.update_log(f"% done for key {key}: {(i+1)/shift_axis.shape[0]*100:.2f}% in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}")
        self.voi_statistics_counter += 1
        self.voi_statistics_avg.append(np.mean(stats_curves,0))
        self.voi_statistics_std.append(np.std(stats_curves,0))

    def linear_shifts_errors(self,keys:np.ndarray,order=1,d=1,weight=1,verbose:bool=False,verbose_precise:bool=False):#Done in 2.0.0
        """
        Runs the function linear_shift_errors on a number of segmentations, saving the resulting curves.\n
        The order and weight parameters will be the same for each computation.\n
        Keyword arguments:\n
        keys -- segmentations key to use. Must be a list or an np.ndarray\n
        order -- linear shift order (default 1)\n
        d -- distance of the shift (default 1)\n
        weight -- weight for each axis, if compounded [TBA] (default 1)\n
        verbose -- outputs the progress (default False)\n
        verbose_precise -- outputs the progress of the underlying process (default False)\n
        """
        initial= time.time()
        if not isinstance(keys,(list,np.ndarray)):
            raise Exception('''keys must be an array of the segmentations to estimate the error.\n
                            To use on a single segmentation, use linear_shifts_error (without 's')''')
        else: keys=np.array(keys)
        for i in range(keys.shape[0]):
            self.linear_shifts_error(keys[i],order=order,d=d,weight=weight,verbose=verbose_precise)
            if verbose: 
                self.update_log(f"Errors done: {(i+1)/keys.shape[0]*100:.2f}% in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}")
    
    def rotation_error(self, key:int, angle:float = 0, order:int = 1, verbose: bool = False):
        """
        This function takes a specific segmentation and rotates it, saving only the results,
        in order to save memory space.
        Keyword arguments:\n
        key -- segmentation key to use (default -1)\n
        angle -- angle of rotation (default 0)\n
        order -- rotation order (default 1)\n
        verbose -- outputs the progress (default False)\n
        """
        initial = time.time()
        if key < 0 or key >= self.voi_counter:
            raise Exception(f"Counter must be between 0 and {self.voi_counter}, whereas here it was {key}.")
        angle_axis = self.axis(order = order,d = angle)
        stats_curves = np.zeros((angle_axis.shape[0],self.nb_acq))
        for i in range(angle_axis.shape[0]):
            VOI_shifted = self.rotation_VOI(angle_axis[i,:],counter=key,save=False)
            stats_curves[i,:] = self.VOI_statistics(VOI = VOI_shifted)
            if verbose:
                self.update_log(f"% done for key {key}: {(i+1)/angle_axis.shape[0]*100:.2f}% in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}")
        self.voi_statistics_counter += 1
        self.voi_statistics_avg.append(np.mean(stats_curves,0))
        self.voi_statistics_std.append(np.std(stats_curves,0))

    def rotation_errors(self, keys:np.ndarray, angle: float = 0, order: int = 1, verbose: bool = False, verbose_precise: bool = False):
        """
        Runs the function rotation_error on a number of segmentations, saving the resulting curves.\n
        The order and weight parameters will be the same for each computation.\n
        Keyword arguments:\n
        keys -- segmentations key to use. Must be a list or an np.ndarray\n
        angle -- rotation angle (default 0)\n
        order -- rotation order (default 1)\n
        verbose -- outputs the progress (default False)\n
        verbose_precise -- outputs the progress of the underlying process (default False)\n
        """
        initial= time.time()
        if not isinstance(keys,(list,np.ndarray)):
            raise Exception('''keys must be an array of the segmentations to estimate the error.\n
                            To use on a single segmentation, use rotation_error (without 's')''')
        else: keys=np.array(keys)
        for i in range(keys.shape[0]):
            self.rotation_error(keys[i],angle = angle,order = order,verbose=verbose_precise)
            if verbose: 
                self.update_log(f"Errors done: {(i+1)/keys.shape[0]*100:.2f}% in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}")

    def expansion_error(self, key:int, factor:float = 1, order:int = 1, verbose: bool = False):
        """
        This function takes a specific segmentation and expands it, saving only the results,
        in order to save memory space.
        Keyword arguments:\n
        key -- segmentation key to use (default -1)\n
        factor -- factor of the expansion (default 1)\n
        order -- expansion order (default 1)\n
        verbose -- outputs the progress (default False)\n
        """
        initial = time.time()
        if key < 0 or key >= self.voi_counter:
            raise Exception(f"Counter must be between 0 and {self.voi_counter}, whereas here it was {key}.")
        if order == 1:
            factor_axis = np.array([[factor,0,0],[1/factor,0,0],
                                [0,factor,0],[0,1/factor,0],
                                [0,0,factor],[0,0,1/factor]])
        elif order == 2:
            factor_axis = np.array([[factor,factor,0],[1/factor,1/factor,0],[1/factor,factor,0],[factor,1/factor,0],
                                [0,factor,factor],[0,1/factor,1/factor],[0,1/factor,factor],[0,factor,1/factor],
                                [factor,0,factor],[1/factor,0,1/factor],[1/factor,0,factor],[factor,0,1/factor]])
        elif order == 3:
            factor_axis = np.array([[factor,factor,factor],[1/factor,1/factor,1/factor],
                                [factor,factor,1/factor],[1/factor,1/factor,factor],
                                [factor,1/factor,factor],[1/factor,factor,1/factor],
                                [1/factor,factor,factor],[factor,1/factor,1/factor]])
        stats_curves = np.zeros((factor_axis.shape[0],self.nb_acq))
        for i in range(factor_axis.shape[0]):
            VOI_shifted = self.expand_VOI(factor_axis[i,:],counter=key,save=False)
            stats_curves[i,:] = self.VOI_statistics(VOI = VOI_shifted)
            if verbose:
                self.update_log(f"% done for key {key}: {(i+1)/factor_axis.shape[0]*100:.2f}% in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}")
        self.voi_statistics_counter += 1
        self.voi_statistics_avg.append(np.mean(stats_curves,0))
        self.voi_statistics_std.append(np.std(stats_curves,0))

    def expansion_errors(self, keys:np.ndarray, factor: float = 1, order: int = 1, verbose: bool = False, verbose_precise: bool = False):
        """
        Runs the function rotation_error on a number of segmentations, saving the resulting curves.\n
        The order and weight parameters will be the same for each computation.\n
        Keyword arguments:\n
        keys -- segmentations key to use. Must be a list or an np.ndarray\n
        factor -- factor for the expansion (default 1)\n
        order -- expansion order (default 1)\n
        verbose -- outputs the progress (default False)\n
        verbose_precise -- outputs the progress of the underlying process (default False)\n
        """
        initial= time.time()
        if not isinstance(keys,(list,np.ndarray)):
            raise Exception('''keys must be an array of the segmentations to estimate the error.\n
                            To use on a single segmentation, use expansion_error (without 's')''')
        else: keys=np.array(keys)
        for i in range(keys.shape[0]):
            self.expansion_error(keys[i],factor = factor,order = order,verbose=verbose_precise)
            if verbose: 
                self.update_log(f"Errors done: {(i+1)/keys.shape[0]*100:.2f}% in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}")

    def reflection_error(self, key:int, verbose: bool = False):
        """
        This function takes a specific segmentation and expands it, saving only the results,
        in order to save memory space.
        Keyword arguments:\n
        key -- segmentation key to use (default -1)\n
        verbose -- outputs the progress (default False)\n
        """
        initial = time.time()
        if key < 0 or key >= self.voi_counter:
            raise Exception(f"Counter must be between 0 and {self.voi_counter}, whereas here it was {key}.")
        axes = np.array([0,1,2])
        stats_curves = np.zeros((axes.shape[0],self.nb_acq))
        for i in range(axes.shape[0]):
            VOI_shifted = self.reflection_ROI(axisNumber = axes[i],counter=key,save=False)
            stats_curves[i,:] = self.VOI_statistics(VOI = VOI_shifted)
            if verbose:
                self.update_log(f"% done for key {key}: {(i+1)/axes.shape[0]*100:.2f}% in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}")
        self.voi_statistics_counter += 1
        self.voi_statistics_avg.append(np.mean(stats_curves,0))
        self.voi_statistics_std.append(np.std(stats_curves,0))
    def reflection_errors(self, keys:np.ndarray, verbose: bool = False, verbose_precise: bool = False):
        """
        Runs the function rotation_error on a number of segmentations, saving the resulting curves.\n
        The order and weight parameters will be the same for each computation.\n
        Keyword arguments:\n
        keys -- segmentations key to use. Must be a list or an np.ndarray\n
        verbose -- outputs the progress (default False)\n
        verbose_precise -- outputs the progress of the underlying process (default False)\n
        """
        initial= time.time()
        if not isinstance(keys,(list,np.ndarray)):
            raise Exception('''keys must be an array of the segmentations to estimate the error.\n
                            To use on a single segmentation, use expansion_error (without 's')''')
        else: keys=np.array(keys)
        for i in range(keys.shape[0]):
            self.reflection_error(keys[i],verbose=verbose_precise)
            if verbose: 
                self.update_log(f"Errors done: {(i+1)/keys.shape[0]*100:.2f}% in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}")    
    def FCM_errors(self, key:int, iterations:int = 30, verbose: bool = False) -> None:
        """
        This function takes a specific FCM segmentation computes errors for it.
        Only valid for 2 classes for now.
        Only the resulting TAC is saved, in order to save memory space.
        Keyword arguments:\n
        key -- segmentation key to use\n
        iterations -- number of analyses to run (default 30)\n
        verbose -- outputs the progress (default False)\n
        """
        initial = time.time()
        if key < 0 or key >= self.voi_counter:
            raise Exception(f"Counter must be between 0 and {self.voi_counter}, whereas here it was {key}.")
        if self.voi_fuzzy[f"{key}"].shape[0] != 2:
            raise Exception(f"Can't run FCM error. This only work if there were 2 classes and here there were {self.voi_fuzzy[f'{key}'].shape[0]}")
        current_FCM = self.voi_fuzzy[f"{key}"][1,:,:,:]
        stats_curves = np.zeros((iterations,self.nb_acq))
        for i in range(iterations):
            random_sample = np.random.rand(current_FCM.shape[0],current_FCM.shape[1],current_FCM.shape[2])
            VOI_rdm = np.where(random_sample >= current_FCM, 0, 1)
            stats_curves[i,:] = self.VOI_statistics(VOI = VOI_rdm)
            if verbose:
                self.update_log(f"% done for key {key}: {(i+1)/iterations*100:.2f}% in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}")
        self.voi_statistics_counter += 1
        self.voi_statistics_avg.append(np.mean(stats_curves,0))
        self.voi_statistics_std.append(np.std(stats_curves,0))
    
    def RadioNuclide_Errors(self, key:int, verbose: bool = False,
                            showErrorsGraphs: bool = False, ErrorGraphsFocus: list = [-1,-1,-1],
                            showErrorsDegree: bool = False, debugMode: bool = False) -> None:
        """
        Computes the error of the TAC using the nature of the displacement of the positron.\n
        The errors is dynamic in time and depends on the timeframe, if more than 1 is present.\n
        +++For now, only a cubic neighbourhood of 2 voxels is correctly taken into account. 
        I need to check for higher than that.+++\n
        Keyword arguments:\n
        key -- segmentation key to use\n
        verbose -- outputs the progress (default False)\n
        showErrorsGraphs -- shows images of the contours, around ErrorGraphsFocus (default False)\n
        ErrorGraphsFocus -- point around which to show the images of the contours (default [-1, -1, -1])\n
        showErrorsDegree -- shows the flow in and out as a function of the degree (default False)\n
        debugMode -- shows the Filters, useful for debug mode (default False)\n
        """
        initial = time.time()
        if key < 0 :#or key >= self.voi_counter:
            raise Exception(f"Counter must be between 0 and {self.voi_counter}, whereas here it was {key}.")
        stats_curves = np.zeros((3,self.nb_acq))

        basedir = os.path.dirname(__file__)
        RadioNuclideData = np.loadtxt(basedir + "/../Data/G_graph_1D_error_RadionuclideData.txt")
        RadioNuclideHeader = open(basedir + "/../Data/G_graph_1D_error_RadionuclideHeader.txt",'r')
        
        value = -5
        count = 0
        for line in RadioNuclideHeader:
            if line == f"squared exponential {self.radioNuclide}\n":
                value = count
            count += 1
        if value == -5:
            raise Exception("Problem in finding the radionuclide in the list.")
        
        sizeOrder = int(2*util.maxRangePositron[f"{self.radioNuclide}"]/np.min(self.voxelSize))
        fractionGoodSize = np.ones((sizeOrder + 1,self.voxelSize.shape[0]))

        for i in range(fractionGoodSize.shape[1]):
            for j in range(sizeOrder):
                if (j+1)*self.voxelSize[i]/2 < util.maxRangePositron[f"{self.radioNuclide}"]:
                    f = np.interp((j+1)*self.voxelSize[i]/2,RadioNuclideData[:,0],RadioNuclideData[:,value])
                else:
                    f = 1
                fractionGoodSize[j,i] = f

        #Create Filters
        firstOrderFilters = []
        for i in range(sizeOrder):
            newFilter = np.zeros(2*(i+1) + 1)
            newFilter[0] = 1
            newFilter[-1] = 1
            firstOrderFilters.append(newFilter/np.sum(newFilter)) # /2

        secondOrderFilters = []
        for i in range(sizeOrder):
            newFilter = np.zeros((2*(i+1) + 1, 2*(i+1) + 1))
            for j in range(newFilter.shape[0]):
                if j != i + 1:
                    newFilter[j,:] += firstOrderFilters[i]/4
                    newFilter[:,j] += firstOrderFilters[i]/4
            
            secondOrderFilters.append(newFilter)

        thirdOrderFilters = []
        for i in range(sizeOrder):
            newFilter = np.zeros((2*(i+1) + 1, 2*(i+1) + 1, 2*(i+1) + 1))
            for j in range(newFilter.shape[0]):
                if j != i + 1 :
                    newFilter[j,:,:] += secondOrderFilters[i]/6
                    newFilter[:,j,:] += secondOrderFilters[i]/6
                    newFilter[:,:,j] += secondOrderFilters[i]/6
            
            thirdOrderFilters.append(newFilter)

        """for i in range(sizeOrder):
            secondOrderFilters[i] = np.where(secondOrderFilters[i] > 0, 1, 0)
            thirdOrderFilters[i] = np.where(thirdOrderFilters[i] > 0, 1, 0)
            secondOrderFilters[i] = secondOrderFilters[i]/np.sum(secondOrderFilters[i])
            thirdOrderFilters[i] = thirdOrderFilters[i]/np.sum(thirdOrderFilters[i])
        """
        if debugMode:
            print(f"Size Order {sizeOrder}")
            print(f"First Order Filters \n{firstOrderFilters}")
            print(f"Second Order Filters \n{secondOrderFilters}")
            print(f"Third Order Filters \n{thirdOrderFilters}")
            #exit()
        VOI = np.copy(self.voi[f"{key}"])

        FirstOrderSegm = np.zeros((3,sizeOrder,self.nb_slice,self.width,self.length))
        SecondOrderSegm = np.zeros((3,sizeOrder,self.nb_slice,self.width,self.length))
        ThirdOrderSegm = np.zeros((sizeOrder,self.nb_slice,self.width,self.length))
        #Apply Filters

        for i in range(3):
            for j in range(sizeOrder):
                if i == 0:
                    for k in range(self.width):
                        for l in range(self.length):
                            FirstOrderSegm[i,j,:,k,l] = np.convolve(VOI[:,k,l], firstOrderFilters[j], mode = 'same') - VOI[:,k,l]
                            FirstOrderSegm[i,j,:,k,l] *= (fractionGoodSize[j+1,0] - fractionGoodSize[j,0])
                elif i == 1:
                    for k in range(self.nb_slice):
                        for l in range(self.length):
                            FirstOrderSegm[i,j,k,:,l] = np.convolve(VOI[k,:,l], firstOrderFilters[j], mode = 'same') - VOI[k,:,l]
                            FirstOrderSegm[i,j,k,:,l] *= (fractionGoodSize[j+1,2] - fractionGoodSize[j,2])
                elif i == 2:
                    for k in range(self.nb_slice):
                        for l in range(self.width):
                            FirstOrderSegm[i,j,k,l,:] = np.convolve(VOI[k,l,:], firstOrderFilters[j], mode = 'same') - VOI[k,l,:]
                            FirstOrderSegm[i,j,k,l,:] *= (fractionGoodSize[j+1,2] - fractionGoodSize[j,2])
                if verbose:
                    self.update_log(f"% of 1st order convolution done for key {key}: {(100*((j+1)+3*i)/(3*fractionGoodSize.shape[0])):.2f}% in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}")

        for i in range(3):
            for j in range(sizeOrder):
                if i == 0:
                    for k in range(self.nb_slice):
                        filterTmp = np.copy(secondOrderFilters[j])
                        for l in range(1,j+2): #Or j + 2
                            #print(f"{l} : {(fractionGoodSize[j+1,1] - fractionGoodSize[j,1]) ** (l+1):.2f} ,{(fractionGoodSize[j+1,2] - fractionGoodSize[j,2]) ** (l+1):.2f}")
                            filterTmp[j + 1 + l,:] *= (fractionGoodSize[l,1] - fractionGoodSize[l-1,1])
                            filterTmp[j + 1 - l,:] *= (fractionGoodSize[l,1] - fractionGoodSize[l-1,1])
                            filterTmp[:,j + 1 + l] *= (fractionGoodSize[l,2] - fractionGoodSize[l-1,2])
                            filterTmp[:,j + 1 - l] *= (fractionGoodSize[l,2] - fractionGoodSize[l-1,2])
                        #print(f"Filter Temps: {j}, {l}", filterTmp)
                        convolvedFilter = ndimage.convolve(VOI[k,:,:], secondOrderFilters[j], mode = 'nearest') - VOI[k,:,:]
                        convolvedValues = ndimage.convolve(VOI[k,:,:], filterTmp, mode = 'nearest')
                        SecondOrderSegm[i,j,k,:,:] = convolvedFilter * convolvedValues/np.sum(secondOrderFilters[j])
                elif i == 1:
                    for k in range(self.width):
                        filterTmp = np.copy(secondOrderFilters[j])
                        for l in range(1,j+2): #Or j + 2
                            filterTmp[j + 1 + l,:] *= (fractionGoodSize[l,0] - fractionGoodSize[l-1,0])
                            filterTmp[j + 1 - l,:] *= (fractionGoodSize[l,0] - fractionGoodSize[l-1,0])
                            filterTmp[:,j + 1 + l] *= (fractionGoodSize[l,2] - fractionGoodSize[l-1,2])
                            filterTmp[:,j + 1 - l] *= (fractionGoodSize[l,2] - fractionGoodSize[l-1,2])

                        convolvedFilter = ndimage.convolve(VOI[:,k,:], secondOrderFilters[j], mode = 'nearest') - VOI[:,k,:]
                        convolvedValues = ndimage.convolve(VOI[:,k,:], filterTmp, mode = 'nearest')
                        SecondOrderSegm[i,j,:,k,:] = convolvedFilter * convolvedValues/np.sum(secondOrderFilters[j])

                elif i == 2:
                    for k in range(self.length):
                        filterTmp = np.copy(secondOrderFilters[j])
                        for l in range(1,j+2): #Or j + 2
                            filterTmp[j + 1 + l,:] *= (fractionGoodSize[l,0] - fractionGoodSize[l-1,0])
                            filterTmp[j + 1 - l,:] *= (fractionGoodSize[l,0] - fractionGoodSize[l-1,0])
                            filterTmp[:,j + 1 + l] *= (fractionGoodSize[l,1] - fractionGoodSize[l-1,1])
                            filterTmp[:,j + 1 - l] *= (fractionGoodSize[l,1] - fractionGoodSize[l-1,1])

                        convolvedFilter = ndimage.convolve(VOI[:,:,k], secondOrderFilters[j], mode = 'nearest') - VOI[:,:,k]
                        convolvedValues = ndimage.convolve(VOI[:,:,k], filterTmp, mode = 'nearest')
                        SecondOrderSegm[i,j,:,:,k] = convolvedFilter * convolvedValues/np.sum(secondOrderFilters[j])
                if verbose:
                    self.update_log(f"% of 2nd order convolution done for key {key}: {(100*((j+1)+3*i)/(3*fractionGoodSize.shape[0])):.2f}% in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}")
                        
        for j in range(sizeOrder):
            filterTmp = np.copy(thirdOrderFilters[j])

            for k in range(1,j + 2):
                filterTmp[j + 1 + k,:,:] *= (fractionGoodSize[k,0] - fractionGoodSize[k-1,0])
                filterTmp[j + 1 - k,:,:] *= (fractionGoodSize[k,0] - fractionGoodSize[k-1,0])
                filterTmp[:,j + 1 + k,:] *= (fractionGoodSize[k,1] - fractionGoodSize[k-1,1])
                filterTmp[:,j + 1 - k,:] *= (fractionGoodSize[k,1] - fractionGoodSize[k-1,1])
                filterTmp[:,:,j + 1 + k] *= (fractionGoodSize[k,2] - fractionGoodSize[k-1,2])
                filterTmp[:,:,j + 1 - k] *= (fractionGoodSize[k,2] - fractionGoodSize[k-1,2])



            convolvedValues = ndimage.convolve(VOI[:,:,:], filterTmp, mode = 'nearest')
            convolvedFilter = ndimage.convolve(VOI[:,:,:], thirdOrderFilters[j], mode = 'nearest') - VOI

            ThirdOrderSegm[j,:,:,:] = convolvedFilter * convolvedValues/np.sum(secondOrderFilters[j])
            if verbose:
                self.update_log(f"% of 3rd order convolution done for key {key}: {(100*(j+1)/(fractionGoodSize.shape[0])):.2f}% in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}")
            #ThirdOrderSegm *= 0

        if showErrorsGraphs and ErrorGraphsFocus[0] >= 0 and ErrorGraphsFocus[1] >= 0 and ErrorGraphsFocus[2] >= 0:
            ylabels = ["1st order \n1st axis", "1st order \n2nd axis", "1st order \n3rd axis",
                    "2nd order \n1st axis", "2nd order \n2nd axis", "2nd order \n3rd axis",
                    "3rd order", "Segmentation"]
            figs, axes = plt.subplots(8,sizeOrder)
            pcm = []
            slice = ErrorGraphsFocus[0]
            for i in range(sizeOrder):
                pcm.append(axes[0,i].pcolormesh(FirstOrderSegm[0,i,slice,:,:]))
                pcm.append(axes[1,i].pcolormesh(FirstOrderSegm[1,i,slice,:,:]))
                pcm.append(axes[2,i].pcolormesh(FirstOrderSegm[2,i,slice,:,:]))
                pcm.append(axes[3,i].pcolormesh(SecondOrderSegm[0,i,slice,:,:]))
                pcm.append(axes[4,i].pcolormesh(SecondOrderSegm[1,i,slice,:,:]))
                pcm.append(axes[5,i].pcolormesh(SecondOrderSegm[2,i,slice,:,:]))
                pcm.append(axes[6,i].pcolormesh(ThirdOrderSegm[i,slice,:,:]))
                pcm.append(axes[7,i].pcolormesh(VOI[slice-1+i,:,:]))
                axes[7,i].set_xlabel(f"Degree {i}")
            for j in range(8):
                axes[j,0].set_ylabel(ylabels[j])
            for i in range(8):
                for j in range(sizeOrder):
                    figs.colorbar(pcm[sizeOrder*i + j], ax = axes[i,j])
            plt.suptitle("Axial Contours for the Radionuclide Error")

            figs, axes = plt.subplots(8,sizeOrder)
            pcm = []
            slice = ErrorGraphsFocus[1]
            for i in range(sizeOrder):
                pcm.append(axes[0,i].pcolormesh(FirstOrderSegm[0,i,:,slice,:]))
                pcm.append(axes[1,i].pcolormesh(FirstOrderSegm[1,i,:,slice,:]))
                pcm.append(axes[2,i].pcolormesh(FirstOrderSegm[2,i,:,slice,:]))
                pcm.append(axes[3,i].pcolormesh(SecondOrderSegm[0,i,:,slice,:]))
                pcm.append(axes[4,i].pcolormesh(SecondOrderSegm[1,i,:,slice,:]))
                pcm.append(axes[5,i].pcolormesh(SecondOrderSegm[2,i,:,slice,:]))
                pcm.append(axes[6,i].pcolormesh(ThirdOrderSegm[i,:,slice,:]))
                pcm.append(axes[7,i].pcolormesh(VOI[:,slice-1+i,:]))
                axes[7,i].set_xlabel(f"Degree {i}")
            for j in range(8):
                axes[j,0].set_ylabel(ylabels[j])
            for i in range(8):
                for j in range(sizeOrder):
                    figs.colorbar(pcm[sizeOrder*i + j], ax = axes[i,j])
            plt.suptitle("Coronal Contours for the Radionuclide Error")

            figs, axes = plt.subplots(8,sizeOrder)
            pcm = []
            slice = ErrorGraphsFocus[2]
            for i in range(sizeOrder):
                pcm.append(axes[0,i].pcolormesh(FirstOrderSegm[0,i,:,:,slice]))
                pcm.append(axes[1,i].pcolormesh(FirstOrderSegm[1,i,:,:,slice]))
                pcm.append(axes[2,i].pcolormesh(FirstOrderSegm[2,i,:,:,slice]))
                pcm.append(axes[3,i].pcolormesh(SecondOrderSegm[0,i,:,:,slice]))
                pcm.append(axes[4,i].pcolormesh(SecondOrderSegm[1,i,:,:,slice]))
                pcm.append(axes[5,i].pcolormesh(SecondOrderSegm[2,i,:,:,slice]))
                pcm.append(axes[6,i].pcolormesh(ThirdOrderSegm[i,:,:,slice]))
                pcm.append(axes[7,i].pcolormesh(VOI[:,:,slice-1+i]))
                axes[7,i].set_xlabel(f"Degree {i}")
            for j in range(8):
                axes[j,0].set_ylabel(ylabels[j])
            for i in range(8):
                for j in range(sizeOrder):
                    figs.colorbar(pcm[sizeOrder*i + j], ax = axes[i,j])
            plt.suptitle("Sagital Contours for the Radionuclide Error")

        #Compute error In & Out
        #Add all axes
        FirstOrderFlowOut = np.zeros((self.nb_acq,3, sizeOrder))
        FirstOrderFlowIn = np.zeros((self.nb_acq,3, sizeOrder))
        SecondOrderFlowOut = np.zeros((self.nb_acq,3, sizeOrder))
        SecondOrderFlowIn = np.zeros((self.nb_acq,3, sizeOrder))
        ThirdOrderFlowOut = np.zeros((self.nb_acq,sizeOrder))
        ThirdOrderFlowIn = np.zeros((self.nb_acq,sizeOrder))

        for k in range(self.nb_acq):
            for j in range(sizeOrder):
                for i in range(3):
                    FirstOrderFlowOut[k,i,j] = np.sum(FirstOrderSegm[i,j,:,:,:] * VOI * self.Image[k,:,:,:])
                    FirstOrderFlowIn[k,i,j] = np.sum(FirstOrderSegm[i,j,:,:,:] * ( - VOI + 1) * self.Image[k,:,:,:])

                    SecondOrderFlowOut[k,i,j] = np.sum(SecondOrderSegm[i,j,:,:,:] * VOI * self.Image[k,:,:,:])
                    SecondOrderFlowIn[k,i,j] = np.sum(SecondOrderSegm[i,j,:,:,:] * ( - VOI + 1) * self.Image[k,:,:,:])
                    #SecondOrderFlowOut[k,i,j] = np.sum(SecondOrderSegm[i,j,:,:,:] * VOI)
                    #SecondOrderFlowIn[k,i,j] = np.sum(SecondOrderSegm[i,j,:,:,:] * ( - VOI + 1))

                ThirdOrderFlowOut[k,j] = np.sum(ThirdOrderSegm[j,:,:,:] * VOI * self.Image[k,:,:,:])
                ThirdOrderFlowIn[k,j] = np.sum(ThirdOrderSegm[j,:,:,:] * ( - VOI + 1) * self.Image[k,:,:,:])
                #ThirdOrderFlowOut[k,j] = np.sum(ThirdOrderSegm[j,:,:,:] * VOI )
                #ThirdOrderFlowIn[k,j] = np.sum(ThirdOrderSegm[j,:,:,:] * ( - VOI + 1) )

        if showErrorsDegree:
            plt.figure()
            for i in range(sizeOrder):
                plt.plot(np.sum(FirstOrderFlowOut[:,:,i],axis = 1)/self.voi_voxels[key], label = f"1st order flow out degree {i}")
                plt.plot(np.sum(FirstOrderFlowIn[:,:,i],axis = 1)/self.voi_voxels[key], label = f"1st order flow in degree {i}")

                plt.plot(np.sum(SecondOrderFlowOut[:,:,i],axis = 1)/self.voi_voxels[key], label = f"2nd order flow out degree {i}")
                plt.plot(np.sum(SecondOrderFlowIn[:,:,i],axis = 1)/self.voi_voxels[key], label = f"2nd order flow in degree {i}")

                plt.plot(ThirdOrderFlowOut[:,i]/self.voi_voxels[key], label = f"3rd order flow out degree {i}")
                plt.plot(ThirdOrderFlowIn[:,i]/self.voi_voxels[key], label = f"3rd order flow in degree {i}")

            plt.xlabel("Degree"); plt.grid(); plt.legend()
            plt.title("Average voxel error for each timeframe, \nfor each order and degree of correction")

        totalFlowOut = np.sum(FirstOrderFlowOut[:,:,:], axis = (1,2))
        totalFlowIn = np.sum(FirstOrderFlowIn[:,:,:], axis = (1,2))
        totalFlowOut += np.sum(SecondOrderFlowOut[:,:,:], axis = (1,2))
        totalFlowIn += np.sum(SecondOrderFlowIn[:,:,:], axis = (1,2))
        totalFlowOut += np.sum(ThirdOrderFlowOut[:,:], axis = 1)
        totalFlowIn += np.sum(ThirdOrderFlowIn[:,:], axis = 1)

        totalFlow = np.abs((totalFlowIn + totalFlowOut)/self.voi_voxels[key])
        if verbose:
            print(totalFlowIn)
            print(totalFlowIn.shape)
            print(totalFlowOut)
            print(totalFlowOut.shape)
            print(totalFlow)
        if verbose:
            print(f"RadioNuclide: {self.radioNuclide}")
            print("Positron attributes ",util.meanRangePositron[f"{self.radioNuclide}"],util.maxRangePositron[f"{self.radioNuclide}"])
            print(f"Voxel Size: {self.voxelSize}")
            print(f"Fraction of good detections \n{fractionGoodSize}")

        self.voi_statistics_counter += 1
        self.voi_statistics_avg.append(self.voi_statistics[key])
        self.voi_statistics_std.append(totalFlow)
############################################################
#                                                          #
# This section deals with the adding and removal of VOIs   #
#                                                          #
############################################################
    def save_VOI(self,VOI:np.ndarray,Fuzzy_VOI: np.ndarray = np.zeros((1,1,1,1)),
                 energies: np.ndarray = np.zeros(10), mus: np.ndarray = np.zeros((1,10)),
                 fFactorsFillingAxisX: np.ndarray = np.zeros(1),
                 fFactorsFillingAxisY: np.ndarray = np.zeros(1),
                 name:str='',do_stats:bool=True,do_moments:bool=True): #Added in 1.3.1
        """
        Save the VOI being worked with in the dictionary
        Keyword arguments:\n
        VOI -- VOI to be saved\n
        Fuzzy_VOI -- (default [])\n
        energies -- (default [])\n
        mus -- (default [])\n
        fFactorsFillingAxisX -- Values of the factor f for filling segmentations (default [0])\n
        fFactorsFillingAxisY -- Values of the volume for the factor f for filling segmentations (default [0])\n
        name -- name of the VOI to be saved (default '')\n
        do_stats -- compute the statistics for the VOI of interest (default True)\n
        do_moments -- compute the moments for the VOI of interest (default True)\n
        """        
        self.voi[f"{self.voi_counter}"] = VOI
        self.voi_fuzzy[f"{self.voi_counter}"] = Fuzzy_VOI
        self.energies[f"{self.voi_counter}"] = energies
        self.mus[f"{self.voi_counter}"] = mus
        self.fFactorsFillingAxisX[f"{self.voi_counter}"] = fFactorsFillingAxisX
        self.fFactorsFillingAxisY[f"{self.voi_counter}"] = fFactorsFillingAxisY
        self.voi_voxels.append(self.count_voxels(self.voi_counter))
        self.voi_name.append(name)
        self.voi_counter += 1
        if do_moments:
            center = self.center_of_mass(VOI)
            self.voi_center_of_mass.append(center.astype(int))
            self.voi_moment_of_inertia.append(self.moment_of_inertia(VOI,center))
        else:
            self.voi_center_of_mass.append([0,0,0])
            self.voi_moment_of_inertia.append([0,0,0])
        if do_stats:
            self.voi_statistics.append(self.VOI_statistics(self.voi_counter-1))
        else:
            self.voi_statistics.append(np.zeros(self.nb_acq))
    
    def remove_VOI(self,key:int = -1): #Done in 1.1
        """Removes a specific VOI entry to the dictionary of VOIs.
        This will make and fill a gap in the dictionary and other arrays containing
        aspects computed with respect to the VOI.
        
        Keyword arguments:\n
        key -- entry of the dictionary of VOIs to be deleted (default -1)
        """
        if(key >= 0):
            new_dict_VOI = {}
            new_dict_Energies = {}
            new_dict_mu = {}
            for i in range(self.voi_counter):
                if i < key:
                    new_dict_VOI[f"{i}"] = self.voi[f"{i}"]
                    new_dict_Energies[f"{i}"] = self.energies[f"{i}"]
                    new_dict_mu[f"{i}"] = self.mus[f"{i}"]
                elif i > key:
                    new_dict_VOI[f"{i-1}"] = self.voi[f"{i}"]
                    new_dict_Energies[f"{i-1}"] = self.energies[f"{i}"]
                    new_dict_mu[f"{i-1}"] = self.mus[f"{i}"]

            self.voi_counter -= 1
            self.voi = new_dict_VOI
            self.energies = new_dict_Energies
            self.mus = new_dict_mu
            del self.voi_voxels[key]
            del self.voi_name[key]
            del self.voi_center_of_mass[key]
            del self.voi_moment_of_inertia[key]
            del self.voi_statistics[key]
            try:
                self.dice_all = np.delete(self.dice_all, key, 0)
                self.jaccard_all = np.delete(self.dice_all, key, 0)
            except: pass
            try: #In case it is the last segmentation
                self.dice_all = np.delete(self.dice_all, key, 1)
                self.jaccard_all = np.delete(self.dice_all, key, 1)
            except: pass
            self.update_log(f"Segmentation {key} removed")

    def remove_Error(self,key: int = -1):
        """Removes a specific Error entry.
        This will make and fill a gap in the lists and other arrays containing
        aspects computed with respect to the VOI.
        
        Keyword arguments:\n
        key -- entry of the error to be deleted (default -1)
        """                
        if(key >= 0):
            self.voi_statistics_counter -= 1
            del self.voi_statistics_avg[key]
            del self.voi_statistics_std[key]
            self.update_log(f"Error {key} removed")

    def remove_Bayesian(self,key: int = -1):
        """Removes a specific Bayesian analysis entry.
        This will make and fill a gap in the lists and other arrays containing
        aspects computed with respect to the VOI.
        
        Keyword arguments:\n
        key -- entry of the error to be deleted (default -1)
        """                
        if(key >= 0):
            new_dict_run = {}
            new_dict_trace = {}
            new_dict_corner = {}
            for i in range(self.bayesian_dynesty_counter):
                if i < key:
                    new_dict_run[f"{i}"] = self.bayesian_graphs_runplot[f"{i}"]
                    new_dict_trace[f"{i}"] = self.bayesian_graphs_traceplot[f"{i}"]
                    new_dict_corner[f"{i}"] = self.bayesian_graphs_cornerplot[f"{i}"]
                elif i > key:
                    new_dict_run[f"{i-1}"] = self.bayesian_graphs_runplot[f"{i}"]
                    new_dict_trace[f"{i-1}"] = self.bayesian_graphs_traceplot[f"{i}"]
                    new_dict_corner[f"{i-1}"] = self.bayesian_graphs_cornerplot[f"{i}"]
            self.bayesian_dynesty_counter -= 1
            self.bayesian_results_avg = np.delete(self.bayesian_results_avg, key, 0)
            self.bayesian_results_e_up = np.delete(self.bayesian_results_e_up, key, 0)
            self.bayesian_results_e_down = np.delete(self.bayesian_results_e_down, key, 0)

            self.bayesian_graphs_runplot = new_dict_run
            self.bayesian_graphs_traceplot = new_dict_trace
            self.bayesian_graphs_cornerplot = new_dict_corner
            self.update_log(f"Bayesian analysis {key} removed")
    def duplicate_VOI(self,key:int = -1): #Done in 1.2.0
        """Adds a new VOI entry to the dictionary of VOIs, which will be placed
        at the end. Also copies all other computed aspects, i.e. number of voxels, name,
        moments and statistics.
        
        Keyword arguments:\n
        key -- entry of the dictionary of VOIs to be duplicated (default -1)
        """
        if (key>=0):
            self.voi[f"{self.voi_counter}"] = self.voi[f"{key}"]
            self.voi_voxels.append(self.voi_voxels[key])
            self.voi_name.append(self.voi_name[key])
            self.voi_center_of_mass(self.voi_center_of_mass[key])
            self.voi_moment_of_inertia(self.voi_moment_of_inertia[key])
            self.voi_statistics(self.voi_statistics[key])
            self.voi_counter += 1

    def add_VOI_ellipsoid(self,center:np.ndarray = np.array([2,2,2]),axes:np.ndarray = np.array([1,1,1]),name:str='',do_moments:bool=False,do_stats:bool=False,save:bool=True): #Done in 1.0
        """Creates a physical ellipsoid volume of interest (VOI)
        centered at a specific voxel specified by the first row in infos 
        and whose length of the three axes 
        are aligned with the array and specified by the second row in infos.
        
        Keyword arguments:\n
        center -- center of the ellipsoid and (default [2,2,2])\n
        axes -- the length of the three axes (default [1,1,1])\n
        name -- name of the VOI (default '')\n
        do_moments -- compute the moments of the VOI and store them (default False)\n
        do_stats -- compute the TACs relative to the VOI (default False)\n
        save -- Save the VOI if true; otherwise, returns it as an argument (default True)\n
        """
        VOI = np.zeros((self.nb_slice,self.width,self.length))
        voxels = 0
        for i in range(self.nb_slice):
            for j in range(self.width):
                for k in range(self.length):
                    if( (i-center[0])**2/axes[0]**2 + (j-center[1])**2/axes[1]**2 + (k-center[2])**2/axes[2]**2 <= 1):
                        VOI[i,j,k] = 1
                        voxels += 1
        if save:
            self.save_VOI(VOI,name=name,do_stats=do_stats,do_moments=do_moments)
        else:
            return VOI

    def add_VOI_prism(self,position:np.ndarray,name:str='',do_moments:bool=False,do_stats:bool=False,save:bool=True): #Done in 1.0
        """Creates a physical prism volume of interest (VOI)
        whose two opposite corners are given by each column
        of the position parameter (should be a 2-3 array).\n        
        Keyword arguments:\n
        position -- region for the prism. Each colum represents opposite vertices(default [[]]\n
        name -- name of the VOI (default '')\n
        do_moments -- compute the moments of the VOI and store them (default False)\n
        do_stats -- compute the TACs relative to the VOI (default False)\n
        save -- Save the VOI if true; otherwise, returns it as an argument (default True)\n
        """
        VOI = np.zeros((self.nb_slice,self.width,self.length))
        for i in range(position[0,0],position[0,1]+1):
            for j in range(position[1,0],position[1,1]+1):
                for k in range(position[2,0],position[2,1]+1):
                    VOI[i,j,k] = 1
        if save:
            self.save_VOI(VOI,name=name,do_stats=do_stats,do_moments=do_moments)
        else:
            return VOI

    def VOI_threshold(self,acq:int = 0,key:int=-1,sigma:float=1,threshold:float = 1,
                        name:str='',do_moments:bool=False,do_stats:bool=False,save:bool=True): #Done in 1.4.0
        """Creates a new VOI from a given VOI, by using a threshold. All values over it are kept, the others discarded.
        
        Keyword arguments:\n
        acq -- temporal acquisition to use (default 0)\n
        key -- segmentation key to use (default -1)\n
        sigma -- value used for the Gaussian filter to take out asperities (default 1)\n
        threshold -- threshold value to use, as a fraction of the maximum value (default 1)\n
        name -- name of the VOI (default '')\n
        do_moments -- compute the moments of the VOI and store them (default False)\n
        do_stats -- compute the TACs relative to the VOI (default False)\n
        save -- Save the VOI if true; otherwise, returns it as an argument (default True)\n
        """
        new_Im = np.zeros_like(self.voi[f"{key}"])
        new_VOI = gaussian_filter(self.voi[f"{key}"],sigma=sigma)
        limit = np.max(new_VOI)*threshold
        for i in range(new_Im.shape[0]):
            for j in range(new_Im.shape[1]):
                for k in range(new_Im.shape[2]):
                    if self.Image[int(acq),i,j,k] >= limit and self.voi[f"{key}"][i,j,k] == 1:
                        new_Im[i,j,k] = 1
        if save:
            self.save_VOI(new_Im,name=name,do_stats=do_stats,do_moments=do_moments)
        return new_Im        

    def VOI_canny(self,subimage:np.ndarray = np.array([]),subinfo = [[-1,0],[0,0],[0,0]],acq:int=0,
                    combination:int = 2,sigma:float=1,
                    threshLow:float = 0.1,threshHigh:float = 0.2,
                    name:str='',do_moments:bool = False,save:bool = True,do_stats:bool=False): #Done in 1.2.0
        """This function creates the contour of a 3D image using Canny edge detection algorithm, with sigma for the Gaussian filter.
        The Canny edge detection algorithm works in 2D, so every 2D plane has to be considered individually.
        The combination options determine how many of the voxels in a given dimension have to be on the 2D contour to be counted.        
        Keyword arguments:\n
        subimage -- image on which to apply the Canny edge algorithm (default [], i.e. all the 3D volume)\n
        subinfo -- smaller region upon which to do the segmentations (default [-1], i.e. the whole image will be considered)\n
        acq -- timeframes on which to base the static segmentations (default 0)\n
        combination -- combination parameter for the number of necessary 2D Canny on a given voxel to make that voxel part of the 
        VOI (default 2)\n
        sigma -- standard deviation of the Gaussian filter used in the Canny algorithm (default 1)\n
        threshLow -- lower threshold for the histeresis in the Canny algorithm; must be between 0 and 1 (default 0.1)\n
        threshHigh -- upper threshold for the histeresis in the Canny algorithm; must be between 0 and 1 (default 0.2)\n
        name -- name of the VOI (default '')\n
        do_moments -- compute the moments of the VOI and store them (default False)\n
        save -- add the VOI to the dictionary of VOIs, with relevant infos (default True); if False, return instead the VOI alone\n
        do_stats -- compute the TACs relative to the VOI (default False)\n
        """
        if subimage.size == 0:
            base_Im = False
            #Either the subimage is given directly (via Canny_filled), or the
            #infos for the subimage are given, whence the subimage is selected
            subimage = self.image_cut(subinfo)[int(acq),:,:,:]
        else:
            base_Im = True
        VOI = np.zeros_like(subimage)
        Canny_2D_sagittal = np.zeros_like(subimage)
        Canny_2D_coronal = np.zeros_like(subimage)
        Canny_2D_axial = np.zeros_like(subimage)
        for i in range(subimage.shape[0]):
            im_tmp = subimage[i,:,:]
            Canny_2D_axial[i,:,:] = feature.canny(im_tmp,sigma=sigma,low_threshold=threshLow,high_threshold=threshHigh)
        for j in range(subimage.shape[1]):
            im_tmp = subimage[:,j,:].reshape((subimage.shape[0],subimage.shape[2]))
            Canny_2D_coronal[:,j,:] = feature.canny(im_tmp,sigma=sigma,low_threshold=threshLow,high_threshold=threshHigh)
        for k in range(subimage.shape[2]):
            im_tmp = subimage[:,:,k].reshape((subimage.shape[0],subimage.shape[1]))
            Canny_2D_sagittal[:,:,k] = feature.canny(im_tmp,sigma=sigma,low_threshold=threshLow,high_threshold=threshHigh)
        Canny_total = Canny_2D_axial+Canny_2D_coronal+Canny_2D_sagittal
        for i in range(subimage.shape[0]):
            for j in range(subimage.shape[1]):
                for k in range(subimage.shape[2]):
                    if Canny_total[i,j,k] >= int(combination):
                        VOI[i,j,k] = 1
        if (not base_Im) and (np.sum(subinfo) >= 0):
            VOI[subinfo[0,0],:,:] = 0
            VOI[subinfo[0,1],:,:] = 0
            VOI[:,subinfo[1,0],:] = 0
            VOI[:,subinfo[1,1],:] = 0
            VOI[:,:,subinfo[2,0]] = 0
            VOI[:,:,subinfo[2,1]] = 0
        if save:
            self.save_VOI(VOI,name=name,do_stats=do_stats,do_moments=do_moments)
        return VOI
    def VOI_Canny_filled(self,subinfo:np.ndarray = [[-1,0],[0,0],[0,0]],acq:int=0,combination:int = 2,
                        sigma:float=1.0,name='',threshLow:float = 0.1,threshHigh:float = 0.2,
                        combinationPost:int = 3,
                        do_moments:bool = False,method:str='TaxiCab',
                        do_stats:str = False,save:str=True): #Done in 1.2.0
        """
        Computes a segmentation using Canny for the contour, then filling it.
        Keyword arguments:\n
        acq -- timeframes on which to base the static segmentations (default 0)\n
        subinfo -- smaller region upon which to do the segmentations (default [-1], i.e. the whole image will be considered)\n
        sigma -- used for the Canny segmentation (default 5)\n
        combination -- combination parameter for the number of necessary 2D Canny on a given voxel to make that voxel part of the 
        VOI (default 2)\n
        threshLow -- lower threshold for the histeresis in the Canny algorithm (default 0.1)\n
        threshHigh -- upper threshold for the histeresis in the Canny algorithm (default 0.2)\n
        combinationPost -- combination parameter for the number of necessary 2D filling on a given voxel to make that voxel part of the 
        VOI. It is used after the filling section (default 3)\n
        method -- method to compute the distance between two voxels (default 'TaxiCab')\n
        name -- used to name all the segmentations saved (default '')\n
        do_moments -- compute the moments of the resulting segmentations (default True)\n
        do_stats -- compute the mean and std of the segmentations (default True)\n
        save -- save the segmentations in the DicomImage class (default True)\n  
        """
        if np.sum(subinfo) < -0.5:
            Image = self.Image[int(acq),:,:,:]
        else:
            Image = self.image_cut(subinfo)[int(acq),:,:,:]
        Cannied = self.VOI_canny(subimage = Image,combination = combination,sigma = sigma,
                                threshLow=threshLow,threshHigh=threshHigh,
                                name=name,do_moments=do_moments,save=False)
        if np.sum(subinfo) > -0.5: #If there is a subimage, this ensure that the contour of the subimage is not taken
                            #because of the difference in intensity between the background and what is not taken
            subinfo = np.array(subinfo)
            Cannied[subinfo[0,0],:,:] = 0
            Cannied[subinfo[0,1],:,:] = 0
            Cannied[:,subinfo[1,0],:] = 0
            Cannied[:,subinfo[1,1],:] = 0
            Cannied[:,:,subinfo[2,0]] = 0
            Cannied[:,:,subinfo[2,1]] = 0        
        Canny_filled = self.fill_3D(array = Cannied,method=method,combination=combinationPost)

        if save:
            self.save_VOI(Canny_filled,name=name,do_stats=do_stats,do_moments=do_moments)
        else:
            return Canny_filled
    def VOI_filled_noNumba(self,seed: np.ndarray = [[-1,-1,-1]],factor:float = 1,
        acq:int=0,sub_im: np.ndarray = [[-1,-1],[-1,-1],[-1,1]],
        name: str = '',max_iter: int = 100,do_moments: bool = False,
        save:bool=True,do_stats:bool=False,
        verbose:bool=True,save_between:bool=False,fraction_f:np.ndarray=[-1,0],
        size_f:np.ndarray=[-1,0],voxels_f:np.ndarray=[-1,0],counter_save: int = 0,
        fAxisX: np.ndarray=np.zeros(1),fAxisY: np.ndarray=np.zeros(1)): #Done in 1.3.2
        """
        This function determines a VOI using a filling algorithm, as discussed in TG211.\n
        Keyword arguments:\n
        seed -- image on which to apply the Canny edge algorithm (default [], i.e. all the 3D volume)\n
        factor -- value f for the seed growing algorithm\n
        acq -- time acquisition on which to do the segmentation (default 0)\n
        sub_im -- if different than default, restricted region over which to fill (default [[-1,-1],[-1,-1],[-1,1]])\n
        name -- name of the VOI (default '')\n
        max_iter -- number of loops before aborting by force the program (default 100)\n
        do_moments -- compute the moments of the VOI and store them (default False)\n
        save -- add the VOI to the dictionary of VOIs, with relevant infos (default True); if False, return instead the VOI alone\n
        do_stats -- compute the TACs relative to the VOI (default False)\n
        verbose -- outputs information along the computing, to follow progression (default false)\n
        save -- add the VOI to the dictionary of VOIs, with relevant infos (default False). Useful for VOI_filled_f, to save all intermediate VOIs\n
        save_between -- allows to save VOIs according to other parameters, such as size of VOI (default = False)\n
        fraction_f -- saves the VOI if the VOI's fraction (with respect to the full image) is within a specific range (default [-1,0])\n
        size_f -- saves the VOI if the VOI's size (in actual units) is within a specific range (default [-1,0])\n
        voxels_f -- saves the VOI if the VOI's number of voxels is within a specific range (default [-1,0])\n
        counter_save -- used to determine whether to save the segmentation or not (c.f. VOI_filled_f) (default 0)\n
        fAxisX -- values of f for the filling_f algorithm to be saved (default [0])\n
        fAxisY -- values of the fraction of the volume for each f for the filling_f algorithm to be saved (default [0])\n
        """
        seed = np.array(seed)
        sub_im = np.array(sub_im)
        try:
            if (seed[0,0]==-1):
                raise Exception("Seed argument must be a 3-array within the image, ex. [0,0,0]")
        except:
            if (seed[0]==-1):
                raise Exception("Seed argument must be a 3-array within the image, ex. [0,0,0]") 
        subimage = self.select_acq(acq = acq)
        VOI = np.zeros_like(subimage)
        VOI_old = np.zeros_like(subimage)
        try:
            for i in range(seed.shape[0]):
                VOI[seed[i,0],seed[i,1],seed[i,2]] = 1
        except:
            VOI[seed[0],seed[1],seed[2]] = 1
        iteration = 0
        try:
            range_im = np.array([[np.max(seed[:,0])-1,np.max(seed[:,0]+1)],[np.max(seed[:,1])-1,np.max(seed[:,1])+1],[np.max(seed[:,2])-1,np.max(seed[:,2])+1]])
        except:
            range_im = np.array([[np.max(seed[0])-1,np.max(seed[0]+1)],[np.max(seed[1])-1,np.max(seed[1])+1],[np.max(seed[2])-1,np.max(seed[2])+1]])
        if sub_im[0,0] == -1:
            min_i = 0
        else:
            min_i = np.max([sub_im[0,0],0])
        if sub_im[0,1] == -1:
            max_i = self.nb_slice
        else:
            max_i = np.min([sub_im[0,1],self.nb_slice])
        if sub_im[1,0] == -1:
            min_j = 0
        else:
            min_j = np.max([sub_im[1,0],0])
        if sub_im[1,1] == -1:
            max_j = self.width
        else:
            max_j = np.min([sub_im[1,1],self.width])
        if sub_im[2,0] == -1:
            min_k = 0
        else:
            min_k = np.max([sub_im[2,0],0])
        if sub_im[2,1] == -1:
            max_k = self.length
        else:
            max_k = np.min([sub_im[2,1],self.length])
        while(iteration<max_iter and (not (VOI==VOI_old).all())): #As long as the images are different
            VOI_old = np.copy(VOI)
            range_im_tmp = range_im
            iteration += 1
            region_mean = np.sum(np.multiply(VOI,subimage))/np.sum(VOI)
            region_std = (np.sum(np.multiply(VOI,(subimage-region_mean)**2))/np.sum(VOI))**(1/2)
            if iteration == 1:
                region_std = np.abs(region_mean)
            if (verbose and iteration%10==0) or (verbose and iteration==1):
                self.update_log(f"Iter: {iteration}, x = {region_mean}, std = {region_std} , voxels = {np.sum(VOI_old)}")
            for i in range(range_im_tmp[0,0],range_im_tmp[0,1]+1):
                for j in range(range_im_tmp[1,0],range_im_tmp[1,1]+1):
                    for k in range(range_im_tmp[2,0],range_im_tmp[2,1]+1):
                        if(VOI[i,j,k] < 0.5): #If the voxel is already in the VOI, don't care
                            if(self.check_neighbours(VOI_old,[i,j,k])): #A neighbour has to be on
                                if((subimage[i,j,k]<=(region_mean+factor*region_std) and subimage[i,j,k]>=(region_mean-factor*region_std))):
                                    VOI[i,j,k] = 1
                                    if i<=range_im[0,0] and i>= min_i+1:
                                        range_im[0,0] = i - 1
                                    if i>=range_im[0,1] and i< max_i - 1:
                                        range_im[0,1] = i + 1
                                    if j<=range_im[1,0] and j>= min_j+1:
                                        range_im[1,0] = j - 1
                                    if j>=range_im[1,1] and j< max_j - 1:
                                        range_im[1,1] = j + 1
                                    if k<=range_im[2,0] and k>= min_k+1:
                                        range_im[2,0] = k - 1
                                    if k>=range_im[2,1] and k< max_k - 1:
                                        range_im[2,1] = k + 1
        size_VOI = np.sum(VOI)
        fraction_VOI = np.sum(VOI)/(self.nb_acq*self.width*self.length)
        if fraction_VOI >= fraction_f[0] and fraction_VOI <= fraction_f[1]:
            save_between = True
        if size_VOI*self.voxel_volume/1000 >= size_f[0] and size_VOI*self.voxel_volume/1000 <= size_f[1]:
            save_between = True
        if size_VOI >= voxels_f[0] and size_VOI <= voxels_f[1]:
            save_between = True
        if verbose:
            self.update_log(f'Stopped the filling at iter {iteration}, while the max_iter was {max_iter}')
        if save or save_between:
            counter_save += 1
            self.save_VOI(VOI,name=name,do_stats=do_stats,do_moments=do_moments,
                          fFactorsFillingAxisX= fAxisX,fFactorsFillingAxisY= fAxisY)
        return VOI, counter_save
    def VOI_filled(self,seed: np.ndarray = [[-1,-1,-1]],factor:float = 1,
        acq:int=0,sub_im: np.ndarray = [[-1,-1],[-1,-1],[-1,1]],
        name: str = '',max_iter: int = 100,do_moments: bool = False,
        save:bool=True,do_stats:bool=False,
        verbose:bool=True,save_between:bool=False,fraction_f:np.ndarray=[-1,0],
        size_f:np.ndarray=[-1,0],voxels_f:np.ndarray=[-1,0],counter_save: int = 0,
        loop = 0,
        fAxisX: np.ndarray=np.zeros(1),fAxisY: np.ndarray=np.zeros(1)): #Done in 1.3.2
        """
        This function determines a VOI using a filling algorithm, as discussed in TG211.\n
        Keyword arguments:\n
        seed -- image on which to apply the Canny edge algorithm (default [], i.e. all the 3D volume)\n
        factor -- value f for the seed growing algorithm\n
        acq -- time acquisition on which to do the segmentation (default 0)\n
        sub_im -- if different than default, restricted region over which to fill (default [[-1,-1],[-1,-1],[-1,1]])\n
        name -- name of the VOI (default '')\n
        max_iter -- number of loops before aborting by force the program (default 100)\n
        do_moments -- compute the moments of the VOI and store them (default False)\n
        save -- add the VOI to the dictionary of VOIs, with relevant infos (default True); if False, return instead the VOI alone\n
        do_stats -- compute the TACs relative to the VOI (default False)\n
        verbose -- outputs information along the computing, to follow progression (default false)\n
        save -- add the VOI to the dictionary of VOIs, with relevant infos (default False). Useful for VOI_filled_f, to save all intermediate VOIs\n
        save_between -- allows to save VOIs according to other parameters, such as size of VOI (default = False)\n
        fraction_f -- saves the VOI if the VOI's fraction (with respect to the full image) is within a specific range (default [-1,0])\n
        size_f -- saves the VOI if the VOI's size (in actual units) is within a specific range (default [-1,0])\n
        voxels_f -- saves the VOI if the VOI's number of voxels is within a specific range (default [-1,0])\n
        counter_save -- used to determine whether to save the segmentation or not (c.f. VOI_filled_f) (default 0)\n
        fAxisX -- values of f for the filling_f algorithm to be saved (default [0])\n
        fAxisY -- values of the fraction of the volume for each f for the filling_f algorithm to be saved (default [0])\n
        """
        seed = np.array(seed)
        sub_im = np.array(sub_im)
        try:
            if (seed[0,0]==-1):
                raise Exception("Seed argument must be a 3-array within the image, ex. [0,0,0]")
        except:
            if (seed[0]==-1):
                raise Exception("Seed argument must be a 3-array within the image, ex. [0,0,0]")            
        subimage = self.select_acq(acq = acq)
        VOI = np.zeros_like(subimage)
        VOI_old = np.zeros_like(subimage)
        try:
            for i in range(seed.shape[0]):
                VOI[seed[i,0],seed[i,1],seed[i,2]] = 1
        except:
            VOI[seed[0],seed[1],seed[2]] = 1
        iteration = 0
        try:
            range_im = np.array([[np.max(seed[:,0])-1,np.max(seed[:,0]+1)],[np.max(seed[:,1])-1,np.max(seed[:,1])+1],[np.max(seed[:,2])-1,np.max(seed[:,2])+1]])
        except:
            range_im = np.array([[np.max(seed[0])-1,np.max(seed[0]+1)],[np.max(seed[1])-1,np.max(seed[1])+1],[np.max(seed[2])-1,np.max(seed[2])+1]])
        if sub_im[0,0] == -1:
            min_i = 0
        else:
            min_i = np.max([sub_im[0,0],0])
        if sub_im[0,1] == -1:
            max_i = self.nb_slice
        else:
            max_i = np.min([sub_im[0,1],self.nb_slice])
        if sub_im[1,0] == -1:
            min_j = 0
        else:
            min_j = np.max([sub_im[1,0],0])
        if sub_im[1,1] == -1:
            max_j = self.width
        else:
            max_j = np.min([sub_im[1,1],self.width])
        if sub_im[2,0] == -1:
            min_k = 0
        else:
            min_k = np.max([sub_im[2,0],0])
        if sub_im[2,1] == -1:
            max_k = self.length
        else:
            max_k = np.min([sub_im[2,1],self.length])
        while(iteration<max_iter and (not (VOI==VOI_old).all())): #As long as the images are different
            VOI_old = np.copy(VOI)
            range_im_tmp = range_im
            iteration += 1
            region_mean = np.sum(np.multiply(VOI,subimage))/np.sum(VOI)
            region_std = (np.sum(np.multiply(VOI,(subimage-region_mean)**2))/np.sum(VOI))**(1/2)
            if iteration == 1:
                region_std = np.abs(region_mean)
            if (verbose and iteration%5==0) or (verbose and iteration==1):
                self.update_log(f"Iter: {iteration}, x = {region_mean}, std = {region_std} , voxels = {np.sum(VOI_old)}")
            ### Numba
            ###
            VOI, range_im = loop(VOI,VOI_old,range_im,range_im_tmp,region_mean,region_std,factor,subimage,min_i,min_j,min_k,max_i,max_j,max_k)
        size_VOI = np.sum(VOI)
        fraction_VOI = np.sum(VOI)/(self.nb_acq*self.width*self.length)
        if fraction_VOI >= fraction_f[0] and fraction_VOI <= fraction_f[1]:
            save_between = True
        if size_VOI*self.voxel_volume/1000 >= size_f[0] and size_VOI*self.voxel_volume/1000 <= size_f[1]:
            save_between = True
        if size_VOI >= voxels_f[0] and size_VOI <= voxels_f[1]:
            save_between = True
        if verbose:
            self.update_log(f'Stopped the filling at iter {iteration}, while the max_iter was {max_iter}')
        if save or save_between:
            counter_save += 1
            self.save_VOI(VOI,name=name,do_stats=do_stats,do_moments=do_moments,
                          fFactorsFillingAxisX= fAxisX,fFactorsFillingAxisY= fAxisY)
        return VOI, counter_save
    def VOI_filled_f(self,seed:np.ndarray=[-1,-1,-1],factor:np.ndarray = [0,1],
        steps:int=5,acq:int=0,sub_im:np.ndarray = [[-1,-1],[-1,-1],[-1,-1]],
        name:str='',
        max_iter:int = 100,do_moments:bool= False,do_stats:bool=False,
        verbose:bool=False,verbose_graphs:bool=False,
        verbose_precise: bool = False,
        save_between:bool=False,max_number_save:int=10000,
        threshold:float=0.99,fraction_f:np.ndarray=[-1,0],size_f:np.ndarray=[-1,0],
        voxels_f:np.ndarray=[-1,0],
        min_f_growth:float = 0,growth:float=-1,break_after_f:bool=False,
        numba = True): #Done in 1.3.2
        """
        Segment by filling over a range of f to determine which is best.
        Keyword parameters:\n
        steps -- number of separations for the factor parameter (default 5)\n
        verbose_precise -- gives detailed output as the segmentation runs. Useful for debugging (default False)\n
        verbose_graphs -- outputs the graphs pertaining to the filling of a the seeded region (default False)\n
        threshold -- value at which to stop the loop, as either the full image is segmented binarily or another condition is attained (default 0.99)\n
        save_between -- allows to save all VOIs during the full loop (data heavy)\n
        max_number_save -- number of segmentations to save; after this threshold, the remaining segmentations are not saved anymore (default 10000)\n
        fraction_f -- saves the VOI if the VOI's fraction (with respect to the full image) is within a specific range (default [-1,0])\n
        size_f -- saves the VOI if the VOI's size (in actual units, cm^3) is within a specific range (default [-1,0])\n
        voxels_f -- saves the VOI if the VOI's number of voxels is within a specific range (default [-1,0])\n
        min_f_growth -- minimal index of the factors after which to check the growth rate (default 0)\n
        growth -- saves the image if the size of the segmented volume increases by more than this factor (default -1)\n
        break_after_f -- breaks the loop over f if all fraction intervals are overpassed (default False)\n
        numba -- use the Numba package to spead up the loops (default True)\n
        """   
        if numba:  
            @jit#(nopython=True)
            def loop(VOI,VOI_old,range_im,range_im_tmp,region_mean,region_std,factor,subimage,min_i,min_j,min_k,max_i,max_j,max_k):
                for i in range(range_im_tmp[0,0],range_im_tmp[0,1]+1):
                    for j in range(range_im_tmp[1,0],range_im_tmp[1,1]+1):
                        for k in range(range_im_tmp[2,0],range_im_tmp[2,1]+1):
                            if(VOI[i,j,k] < 0.5): #If the voxel is already in the VOI, don't care
                                neighbours = 0
                                try: neighbours += VOI_old[i+1,j,k] 
                                except: pass
                                try: neighbours += VOI_old[i-1,j,k] 
                                except: pass
                                try: neighbours += VOI_old[i,j+1,k] 
                                except: pass
                                try: neighbours += VOI_old[i,j-1,k] 
                                except: pass
                                try: neighbours += VOI_old[i,j,k+1] 
                                except: pass
                                try: neighbours += VOI_old[i,j,k-1] 
                                except: pass
                                
                                if(neighbours > 0.5): #A neighbour has to be on
                                    if((subimage[i,j,k]<=(region_mean+factor*region_std) and subimage[i,j,k]>=(region_mean-factor*region_std))):
                                        VOI[i,j,k] = 1
                                        if i<=range_im[0,0] and i>= min_i+1:
                                            range_im[0,0] = i - 1
                                        if i>=range_im[0,1] and i< max_i - 1:
                                            range_im[0,1] = i + 1
                                        if j<=range_im[1,0] and j>= min_j+1:
                                            range_im[1,0] = j - 1
                                        if j>=range_im[1,1] and j< max_j - 1:
                                            range_im[1,1] = j + 1
                                        if k<=range_im[2,0] and k>= min_k+1:
                                            range_im[2,0] = k - 1
                                        if k>=range_im[2,1] and k< max_k - 1:
                                            range_im[2,1] = k + 1
                return VOI, range_im  
        if (seed[0]==-1):
            raise Exception("Seed argument must be a 3-array within the image, ex. [0,0,0]") 
        f_range = np.arange(factor[0],factor[1],(factor[1]-factor[0])/steps)
        voxels = np.zeros_like(f_range)
        ratio_range = np.zeros_like(f_range)
        image_size = self.nb_slice*self.width*self.length
        counter_save = 0
        size_sub_im = (sub_im[0][1]-sub_im[0][0])*(sub_im[1][1]-sub_im[1][0])*(sub_im[2][1]-sub_im[2][0])
        for f in range(steps):
            if verbose and (f+1)%int(steps/10) == 0:
                self.update_log(f"f value = {f_range[f]:.3f}, step {f+1}/{steps}")
            if counter_save >= max_number_save:
                fraction_f=[-1,0];size_f=[-1,0];voxels_f=[-1,0]
                break
            if numba:
                VOI_filled = self.VOI_filled(seed=np.array(seed),factor=f_range[f],acq=acq,sub_im=np.array(sub_im),max_iter=max_iter,save=False,
                    verbose=verbose_precise,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f}",
                    do_moments=do_moments,do_stats=do_stats,fraction_f=fraction_f,size_f=size_f,voxels_f=voxels_f,counter_save=counter_save,loop=loop)
            else:
                VOI_filled = self.VOI_filled_noNumba(seed=np.array(seed),factor=f_range[f],acq=acq,sub_im=np.array(sub_im),max_iter=max_iter,save=False,
                    verbose=verbose_precise,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f}",
                    do_moments=do_moments,do_stats=do_stats,fraction_f=fraction_f,size_f=size_f,voxels_f=voxels_f,counter_save=counter_save)
            counter_save = VOI_filled[1]
            voxels[f] = self.count_voxels(VOI=VOI_filled[0])
            ratio_range[f] = (voxels[f]/image_size)
            if (fraction_f[0] + fraction_f[1])!=-1 or (size_f[0] + size_f[1])!=-1 or (voxels_f[0] + voxels_f[1])!=-1:
                if((break_after_f and voxels[f] > voxels_f[1]) \
                        and (ratio_range[f] > fraction_f[1] and voxels[f]*self.voxel_volume/1000 > size_f[1])) \
                        and (counter_save == 0 and max_number_save > 0):
                    self.update_log(f"Saving the least worst segmentation")
                    self.save_VOI(VOI_filled[0],name=name,do_stats=do_stats,do_moments=do_moments,
                                  fFactorsFillingAxisX= f_range[:f+1], fFactorsFillingAxisY=ratio_range[:f+1])
                    break
            if size_sub_im>0 and voxels[f]/size_sub_im > threshold:
                self.update_log(f"Stopping at iter {f+1}, because threshold of {threshold} has been reached with {voxels[f]/size_sub_im:.3f}.")
                if counter_save == 0 and max_number_save > 0:
                    self.update_log(f"Saving a backup segmentation, for nothing was satisfactory")
                    if numba:
                        self.VOI_filled(seed=seed,factor=f_range[f-1],acq=acq,sub_im=np.array(sub_im),
                                        max_iter=max_iter,save=True,
                            verbose=verbose_precise,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f} backup",
                            do_moments=do_moments,do_stats=do_stats,loop=loop,
                            fAxisX= f_range[:f+1], fAxisY=ratio_range[:f+1])
                    else:
                        self.VOI_filled_noNumba(seed=seed,factor=f_range[f-1],acq=acq,sub_im=np.array(sub_im),max_iter=max_iter,save=True,
                            verbose=verbose_precise,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f} backup",
                            do_moments=do_moments,do_stats=do_stats,
                            fAxisX= f_range[:f+1], fAxisY=ratio_range[:f+1])
                break
            if f > min_f_growth and growth>=0:
                if voxels[f]/voxels[f-1] > growth:
                    self.update_log(f"Saving the previous segmentation, for the growth factor is {(voxels[f]/voxels[f-1]):.2f}, which is over the allowed {growth}.\
                            \nThe index was {f-1}, which is >= to {min_f_growth}")
                    if numba:
                        self.VOI_filled(seed=seed,factor=f_range[f-1],acq=acq,sub_im=np.array(sub_im),max_iter=max_iter,save=True,
                            verbose=verbose_precise,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f} growth {(voxels[f]/voxels[f-1]):.2f}>{growth}",
                            do_moments=do_moments,do_stats=do_stats,loop=loop,
                            fAxisX= f_range[:f+1], fAxisY=ratio_range[:f+1])   
                    else: 
                        self.VOI_filled_noNumba(seed=seed,factor=f_range[f-1],acq=acq,sub_im=np.array(sub_im),max_iter=max_iter,save=True,
                            verbose=verbose_precise,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f} growth {(voxels[f]/voxels[f-1]):.2f}>{growth}",
                            do_moments=do_moments,do_stats=do_stats,
                            fAxisX= f_range[:f+1], fAxisY=ratio_range[:f+1]) 
                    break               
            if voxels[f]/image_size >= threshold:
                self.update_log(f"Stopping at iter {f+1}, because threshold of {threshold} has been reached with {voxels[f]/image_size:.3f}.")
                if counter_save == 0 and max_number_save > 0:
                    self.update_log(f"Saving a backup image, for nothing was satisfactory.")
                    if numba:
                        self.VOI_filled(seed=seed,factor=f_range[f-1],acq=acq,sub_im=np.array(sub_im),max_iter=max_iter,save=True,
                            verbose=verbose_precise,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f} backup",
                            do_moments=do_moments,do_stats=do_stats,loop=loop,
                            fAxisX= f_range[:f+1], fAxisY=ratio_range[:f+1])
                    else:
                        self.VOI_filled_noNumba(seed=seed,factor=f_range[f-1],acq=acq,sub_im=np.array(sub_im),max_iter=max_iter,save=True,
                            verbose=verbose_precise,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f} backup",
                            do_moments=do_moments,do_stats=do_stats,
                            fAxisX= f_range[:f+1], fAxisY=ratio_range[:f+1])
                break
            if f == (steps - 1):
                self.update_log(f"Stopping because max factor f = {f_range[-1]:.2f} was reached")
                if counter_save == 0 and max_number_save > 0:
                    self.update_log(f"Saving a backup image, for nothing was satisfactory.")
                    if numba:
                        self.VOI_filled(seed=seed,factor=f_range[-1],acq=acq,sub_im=np.array(sub_im),max_iter=max_iter,save=True,
                            verbose=verbose_precise,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[-1]:.3f} backup",
                            do_moments=do_moments,do_stats=do_stats,loop=loop,
                            fAxisX= f_range[:f+1], fAxisY=ratio_range[:f+1])
                    else:
                        self.VOI_filled_noNumba(seed=seed,factor=f_range[f-1],acq=acq,sub_im=np.array(sub_im),max_iter=max_iter,save=True,
                            verbose=verbose_precise,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[-1]:.3f} backup",
                            do_moments=do_moments,do_stats=do_stats,
                            fAxisX= f_range[:f+1], fAxisY=ratio_range[:f+1])
                break
        ###Save last if steps is exceeded
        if verbose_graphs:
            if fraction_f[0] >= 0 and fraction_f[1] <= 1:
                plt.figure();plt.plot(f_range[:f+1],(ratio_range[:f+1]));plt.ylabel("Ratio Filled");plt.xlabel("f");plt.yscale("log")
                plt.title(f"Ratio of the Image filled depending on the factor f at acq {acq}");plt.grid()
                plt.axhline(y=fraction_f[0], color='r', linestyle='-');plt.axhline(y=fraction_f[1], color='r', linestyle='-')
                if counter_save==0 and max_number_save > 0:
                    plt.axvline(x=f_range[f-1], color='b', linestyle='-')
            if size_f[0] >= 0:
                plt.figure();plt.plot(f_range[:f+1],voxels[:f+1]);plt.ylabel("Voxels Filled");plt.xlabel("f");plt.yscale("log")
                plt.title(f"Voxels of the Image filled depending on the factor f at acq {acq}");plt.grid()
                plt.axhline(y=size_f[0], color='r', linestyle='-');plt.axhline(y=size_f[1], color='r', linestyle='-')
                if counter_save==0 and max_number_save > 0:
                    plt.axvline(x=f_range[f-1], color='b', linestyle='-')
            if voxels_f[0] >= 0:
                plt.figure();plt.plot(f_range[:f+1],voxels[:f+1]*self.voxel_volume/1000);plt.ylabel(f"Volume Filled (cm^3=mL)");plt.xlabel("f");plt.yscale("log")
                plt.title(f"Volume of the Image filled depending on the factor f at acq {acq}");plt.grid()
                plt.axhline(y=voxels_f[0], color='r', linestyle='-');plt.axhline(y=voxels_f[1], color='r', linestyle='-')
                if counter_save==0 and max_number_save > 0:
                    plt.axvline(x=f_range[f-1], color='b', linestyle='-')
        return ratio_range

    def VOI_kMean(self,acq:int=0,subinfo:np.ndarray = [[-1,0],[0,0],[0,0]],
                max_iter:int=100,
                verbose:bool = False,save:bool=True,do_moments:bool= False,
                do_stats:bool=False,name:str=''): #Added in 1.3.0
        """
        This function segments an image using a k-mean algorithm. (2-Mean Only!)\n
        Keyword arguments:\n
        acq -- time acquisition on which to base the static segmentation (default 0)\n
        subinfo -- fraction (i.e. section) of the image to consider for the segmentation (default [[-1,0],[0,0],[0,0]])\n
        max_iter -- number of iterations for the algorithm (default 100)\n
        verbose -- print the statistics along the computations (default False)\n
        save -- add the VOI to the dictionary of VOIs, with relevant infos (default True); if False, return instead the VOI alone\n
        do_moments -- compute the moments of the VOI and store them (default False)\n
        do_stats -- compute the TACs relative to the VOI (default False)\n
        name -- name to give to the VOI in the dictionary of VOIs (default '')\n
        """
        if np.sum(subinfo) < -0.5:
            subimage = self.Image[acq,:,:,:]
        else:
            subimage = self.Image[acq,subinfo[0][0]:subinfo[0][1],subinfo[1][0]:subinfo[1][1],subinfo[2][0]:subinfo[2][1]]
        old_mean = np.zeros(2)
        mean = np.zeros((2,max_iter,1))
        var = np.zeros((2,max_iter,1))
        old_mean[0] = np.min(subimage)
        old_mean[1] = np.max(subimage)
        iter_now = 0
        
        while(iter_now < max_iter and (not (old_mean[:]==mean[:,iter_now]).all())):
            VOI_0 = np.zeros_like(subimage)
            VOI_1 = np.zeros_like(subimage)
            if(iter_now != 0):
                old_mean = np.copy(mean[:,iter_now])
            else:
                mean[:,0,0] = np.copy(old_mean)
            mid_value = (old_mean[0]+old_mean[1])/2
            iter_now += 1
            for i in range(subimage.shape[0]):
                for j in range(subimage.shape[1]):
                    for k in range(subimage.shape[2]):
                        if(subimage[i,j,k]<mid_value):
                            VOI_0[i,j,k] = 1
                        else:
                            VOI_1[i,j,k] = 1
            mean[0,iter_now:,0] = np.sum(np.multiply(VOI_0,subimage))/np.sum(VOI_0)
            mean[1,iter_now:,0] = np.sum(np.multiply(VOI_1,subimage))/np.sum(VOI_1)
            var[0,iter_now:,0] = np.sum(np.multiply(VOI_0,(subimage-mean[0,iter_now])**2))/np.sum(VOI_0)
            var[1,iter_now:,0] = np.sum(np.multiply(VOI_1,(subimage-mean[1,iter_now])**2))/np.sum(VOI_1)
            if verbose:
                self.update_log(f"Average of the groups for iter {iter_now}: {mean[0,iter_now,0]:.1f} and {mean[1,iter_now,0]:.1f}")
                self.update_log(f"Variance of the groups for iter {iter_now}: {var[0,iter_now,0]:.1f} and {var[1,iter_now,0]:.1f}")

        VOI = np.zeros_like(self.Image[int(acq),:,:,:])
        for i in range(subimage.shape[0]):
            for j in range(subimage.shape[1]):
                for k in range(subimage.shape[2]):
                    prob0 = np.exp(-(subimage[i,j,k]-mean[0,-1,0])**2/(2*var[0,-1,0]))/(2*3.141592*var[0,-1,0])**(1/2)
                    prob1 = np.exp(-(subimage[i,j,k]-mean[1,-1,0])**2/(2*var[1,-1,0]))/(2*3.141592*var[1,-1,0])**(1/2)
                    if(prob1>prob0):
                        VOI[i+subinfo[0][0],j+subinfo[1][0],k+subinfo[2][0]] = 1
        if save:
            self.save_VOI(VOI,name=name,do_stats=do_stats,do_moments=do_moments)
        if not save:
            return VOI, mean[:,:iter_now,:], var[:,:iter_now,:]
    def VOI_ICM(self,acq:int=0,alpha:float = 1,subinfo:list = [[-1,0],[0,0],[0,0]],
                max_iter:int=100,max_iter_kmean:int=100,
                verbose:bool = False,save:bool=True,do_moments:bool= False,
                do_stats:bool=False,name:str=''): #Added in 1.3.0
        """
        This function segments an image using a k-mean algorithm.\n
        Keyword arguments:\n
        acq -- time acquisition on which to base the static segmentation (default 0)\n
        alpha -- constant to weigh the presence of different neighbours (default 1)\n 
        subinfo -- fraction (i.e. section) of the image to consider for the segmentation (default [[-1,0],[0,0],[0,0]])\n
        max_iter -- number of iterations for the kmean algorithm (underlying) (default 100)\n
        max_iter_kmean -- number of iterations for the algorithm (default 100)\n
        verbose -- print the statistics along the computations (default False)\n
        save -- add the VOI to the dictionary of VOIs, with relevant infos (default True); if False, return instead the VOI alone\n
        do_moments -- compute the moments of the VOI and store them (default False)\n
        do_stats -- compute the TACs relative to the VOI (default False)\n
        name -- name to give to the VOI in the dictionary of VOIs (default '')\n
        """
        if np.sum(subinfo) < -0.5:
            subimage = self.Image[acq,:,:,:]
        else:
            subimage = self.Image[acq,subinfo[0][0]:subinfo[0][1],subinfo[1][0]:subinfo[1][1],subinfo[2][0]:subinfo[2][1]]
        VOI, mean, var = self.VOI_kMean(acq=acq,subinfo = subinfo,max_iter=max_iter_kmean,save=False)
        new_VOI = np.copy(VOI[subinfo[0][0]:subinfo[0][1],subinfo[1][0]:subinfo[1][1],subinfo[2][0]:subinfo[2][1]])
        old_VOI = np.copy(new_VOI+0.5)
        iter_now = 0
        E_tot_all = np.zeros(max_iter)
        E_old = 1e100
        E_tot = -1
        while(iter_now < max_iter and (not (new_VOI==old_VOI).all()) and E_tot < E_old):
            old_VOI = np.copy(new_VOI)
            iter_now += 1
            if iter_now != 1:
                E_old = E_tot
            E_tot = 0
            counter = 0
            for i in range(old_VOI.shape[0]):
                for j in range(old_VOI.shape[1]):
                    for k in range(old_VOI.shape[2]):
                        neighbour0 = self.count_neighbours_other_class(old_VOI,[i,j,k],0)
                        neighbour1 = self.count_neighbours_other_class(old_VOI,[i,j,k],1)
                        E_0 = -np.log(np.exp(-(subimage[i,j,k]-mean[0,-1,0])**2/(2*var[0,-1,0]))/(2*3.141592*var[0,-1,0])**(1/2)) + alpha* neighbour0
                        E_1 = -np.log(np.exp(-(subimage[i,j,k]-mean[1,-1,0])**2/(2*var[1,-1,0]))/(2*3.141592*var[1,-1,0])**(1/2)) + alpha* neighbour1
                        if E_0 > E_1:
                            if new_VOI[i,j,k]==0:
                                counter += 1
                            new_VOI[i,j,k] = 1
                            E_tot += E_1
                        else:
                            if new_VOI[i,j,k]==1:
                                counter += 1
                            new_VOI[i,j,k] = 0
                            E_tot += E_0
            if (verbose and iter_now%5==0) or (verbose and iter_now==1):
                self.update_log(f"Iter {iter_now}, size of classes: {np.sum(new_VOI):.0f} and {(subinfo[0][1]-subinfo[0][0])*(subinfo[1][1]-subinfo[1][0])*(subinfo[2][1]-subinfo[2][0])-np.sum(new_VOI):.0f}, with total energy {E_tot:.3f}")
                self.update_log(f"Number of voxels changed: {counter}")
            E_tot_all[iter_now - 1] = E_tot
        for i in range(old_VOI.shape[0]):
            for j in range(old_VOI.shape[1]):
                for k in range(old_VOI.shape[2]):
                    VOI[i+subinfo[0][0],j+subinfo[1][0],k+subinfo[2][0]] = new_VOI[i,j,k]
        if save:
            self.save_VOI(VOI,energies= E_tot_all[:iter_now-1],mus = mean,name=name,do_stats=do_stats,do_moments=do_moments)
        if not save:
            return VOI, E_tot
        return E_tot
    def VOI_FCM(self,acq:int=0, subinfo:list = [[-1,0],[0,0],[0,0]],
                classNumber: int = 2, alpha: float = 2, m: float = 2,
                maxIter:int = 20, maxIterConvergence:int = 20, 
                convergenceDelta: float = 1e-2, convergenceStep: float = 1e-10,
                verbose = True, verboseIter = 10,
                save:bool=True,do_moments:bool= True,
                do_stats:bool=True,name:str=''):
        """
        Fuzzy C-Mean Segmentation technique
        Keyword arguments:\n
        acq -- time acquisition on which to base the static segmentation (default 0)\n
        subinfo -- fraction (i.e. section) of the image to consider for the segmentation (default [[-1,0],[0,0],[0,0]])\n
        classNumber -- used for the number of class to segment (default 2)\n
        alpha -- distance metric (default 2)\n
        m -- fuzziness parameter (default 2)\n
        maxIter -- maximum number of iteration to converge generally (default 20)\n
        maxIterConvergence -- maximum number of iteration to converge for the means (default 20)\n
        convergenceDelta -- interval to stop the iterations (default 1e-2)\n
        convergenceStep -- time step for the gradient descent (default 1e-10)\n
        verbose -- print the statistics along the computations (default False)\n
        verboseIter -- steps after which to print the progress
        save -- add the VOI to the dictionary of VOIs, with relevant infos (default True); if False, return instead the VOI alone\n
        do_moments -- compute the moments of the VOI and store them (default False)\n
        do_stats -- compute the TACs relative to the VOI (default False)\n
        name -- name to give to the VOI in the dictionary of VOIs (default '')\n
        """
        if np.sum(subinfo) < -0.5:
            subImage = self.Image[acq,:,:,:]
        else:
            subImage = self.Image[acq,subinfo[0][0]:subinfo[0][1],subinfo[1][0]:subinfo[1][1],subinfo[2][0]:subinfo[2][1]]
        NewProbVectors = np.ones((classNumber,subImage.shape[0],subImage.shape[1],subImage.shape[2]))
        mus = np.ones(classNumber)
        for i in range(classNumber):
            NewProbVectors [i,:,:,:] = (2 * (i + 1)) /(classNumber * (classNumber + 1) ) * NewProbVectors [i,:,:,:] + (-1)**i * 0.1
            NewProbVectors [i,:,:,:] = np.random.rand()
            mus[i] = (np.max(subImage) - np.min(subImage)) * (2 * (i + 1)) /(classNumber * (classNumber + 1) )
        NewProbVectors = NewProbVectors/np.sum(NewProbVectors,axis = 0)
        NewSegm = np.zeros((subImage.shape[0],subImage.shape[1],subImage.shape[2]))
        OldProbVectors = np.copy(NewProbVectors) + 1
        currentIter = 0
        Energies = np.zeros(maxIter+1)
        mus_all = np.zeros((classNumber,maxIter+1,maxIterConvergence+1))
        for i in range(classNumber):
            mus_all[i,0,:] = mus[i]
        Energies[0] = self.LossFunction(subImage,NewProbVectors,mus = mus,m=m,alpha=alpha)
        while(currentIter < maxIter and ((not (np.abs(NewProbVectors -OldProbVectors) < 1e-4).all()) or currentIter < maxIter * 0.1)):
            OldProbVectors = np.copy(NewProbVectors)
            if alpha == 2:
                for i in range(classNumber):
                    mus[i] = np.sum(NewProbVectors[i,:,:,:]**m * subImage)
                    mus[i] /= np.sum(NewProbVectors[i,:,:,:]**m)
                    mus[i] = mus[i] + np.random.rand()*(-1)**(i+1)/mus[i]
            elif alpha < 2 and alpha > 1:
                if classNumber == 2 and mus[0] > mus[1]:
                    tmp = mus[0]
                    mus[0] = mus[1]
                    mus[1] = tmp
                for i in range(classNumber):
                    old_mus = mus[i] + 10
                    currentIterConvergence = 0
                    while(currentIterConvergence < maxIterConvergence and (not (np.abs(mus[i] - old_mus) < convergenceDelta))):
                        old_mus = mus[i]
                        mus[i] += convergenceStep * np.sum(NewProbVectors[i,:,:,:]**m * np.sign(subImage - mus[i]) * np.abs(subImage - mus[i])**(alpha-1))
                        currentIterConvergence += 1
                        if verbose and currentIterConvergence != 1 and (currentIterConvergence - 1)%10 == 0 :
                            pass#self.update_log(f"Sub Iter = {currentIterConvergence - 1}, means {i} = {mus[i]}")
                        mus_all[i,currentIter+1,currentIterConvergence-1:] = mus[i]
                if classNumber == 2 and mus[0] > mus[1]:
                    tmp = mus[0]
                    mus[0] = mus[1]
                    mus[1] = tmp                
            elif alpha > 2:
                for i in range(classNumber):
                    old_mus = mus[i] + 10
                    currentIterConvergence = 0
                    while(currentIterConvergence < maxIterConvergence and (not (np.abs(mus[i] - old_mus) < convergenceDelta))):
                        old_mus = mus[i]

                        above = np.sum(NewProbVectors[i,:,:,:]**m * np.sign(subImage - mus[i]) * np.abs(subImage - mus[i])**(alpha-1))
                        below = (alpha - 1) * np.sum(NewProbVectors[i,:,:,:]**m * np.abs(subImage - mus[i])**(alpha-2))
                        mus[i] += above/below

                        currentIterConvergence += 1
                        mus_all[i,currentIter+1,currentIterConvergence-1:] = mus[i]
                    mus[i] += np.random.rand()*(-1)**(i+1)/mus[i]
            else:
                raise Exception(f"Invalid value for alpha. It must be greater than 1 and it was {alpha}")
            for i in range(subImage.shape[0]):
                for j in range(subImage.shape[1]):
                    for k in range(subImage.shape[2]):
                        for l in range(classNumber):
                            value = np.sum((np.abs(subImage[i,j,k]-mus[l])/np.abs(subImage[i,j,k] * np.ones(classNumber) - mus))**(alpha/(m-1)))
                            NewProbVectors[l,i,j,k] = 1/value
            currentIter += 1
            if verbose and currentIter != 1 and (currentIter - 1)%verboseIter == 0 :
                with np.printoptions(precision=2, suppress=True):
                    self.update_log(f"Main Iter = {currentIter - 1}, means = {mus}")
            Energies[currentIter] = self.LossFunction(subImage,NewProbVectors,mus = mus,m=m,alpha=alpha)
            mus_all[:,currentIter,-1] = mus

        VOI = np.zeros_like(self.Image[acq,:,:,:])
        VOI_FCM = np.zeros((classNumber,self.nb_slice,self.width,self.length))
        VOI_FCM[0,:,:,:] = 1
        for i in range(subImage.shape[0]):
            for j in range(subImage.shape[1]):
                for k in range(subImage.shape[2]):
                    VOI[i+subinfo[0][0],j+subinfo[1][0],k+subinfo[2][0]] = np.argmax(NewProbVectors[:,i,j,k])
                    for l in range(classNumber):
                        VOI_FCM[l,i+subinfo[0][0],j+subinfo[1][0],k+subinfo[2][0]] = NewProbVectors[l,i,j,k]
        if save:
            self.save_VOI(VOI = VOI,Fuzzy_VOI=VOI_FCM,
                          energies = Energies[:currentIter],mus = mus_all[:,:currentIter],
                          name=f"FCM, m = {m}, alpha = {alpha}"+name,
                          do_stats=do_stats,do_moments=do_moments)
        else:
            return Energies[:currentIter], mus_all[:,:currentIter], NewProbVectors
############################################################
#                                                          #
# This section deals with the statistics of VOIs           #
#                                                          #
############################################################
    def count_voxels(self,key:int = -1,VOI:np.ndarray=-1):
        """
        Counts the voxels in a segmentation, either one of the saved or a temporary one.\n
        Keyword arguments:\n
        key -- segmentation key used to compute the voxels (default -1)\n
        VOI -- array from which to count the number of voxels (default -1)\n
        """
        voxel = 0
        if isinstance(key,int):
            if key >= 0:
                voxel = np.sum(self.voi[f"{key}"])
        if isinstance(VOI,(np.ndarray,list)):
            voxel = np.sum(VOI)
        return int(voxel)

    def VOI_statistics(self,key:int=-1,VOI:np.ndarray=[]): #Done in 1.1
        """
        Counts the mean value in a segmentation, either one of the saved or a temporary one.\n
        Keyword arguments:\n
        key -- segmentation key used to compute the mean (default -1)\n
        VOI -- array from which to count the number of mean (default -1)\n
        """
        means = np.zeros(self.nb_acq)
        if(key >= 0 and key < self.voi_counter): 
            for t in range(self.nb_acq):
                means[t] = np.sum(np.multiply(self.Image[t,:,:,:],self.voi[f"{key}"]))/self.voi_voxels[key]
        else:
            for t in range(self.nb_acq):
                means[t] = np.sum(np.multiply(self.Image[t,:,:,:],VOI))/self.count_voxels(VOI = VOI)
        return means
    def center_of_mass(self,array,D=3): #Done in 1.2.0
        """
        Compute the center of mass of an array.\n
        Keyword arguments:\n
        array -- array from which the center of mass is computed \n
        D -- dimension of the array parameter (default 3)\n
        """
        if D==3:
            Center = np.zeros(len(array.shape))
            pixel = 0
            for i in range(array.shape[0]):
                for j in range(array.shape[1]):
                    for k in range(array.shape[2]):
                        if array[i,j,k] > 0.5:
                            pixel += 1
                            Center += np.array([i,j,k])
            if pixel != 0:
                Center = Center/pixel
            else:
                self.update_log("No voxels in the image, center of mass not determined and set to (0,0,0)")
        elif D==2:
            Center = np.zeros(len(array.shape))
            pixel = 0
            for i in range(array.shape[0]):
                for j in range(array.shape[1]):
                        if array[i,j] > 0.5:
                            pixel += 1
                            Center += np.array([i,j])
            if pixel != 0:
                Center = Center/pixel
            else:
                pass
        return Center
    def moment_of_inertia(self,array:np.ndarray,center:np.ndarray): #Done in 1.2.0
        """
        Compute the moment of inertia (second moment) of a given array.\n
        Keyword argument:\n
        array -- array from which the moment is computed \n
        center -- center of the image (first moment)\n
        """
        moment = np.zeros(len(array.shape))
        pixel = 0
        for i in range(array.shape[0]):
            for j in range(array.shape[1]):
                for k in range(array.shape[2]):
                    if array[i,j,k] > 0.5:
                        pixel += 1
                        moment[0] += (j-center[1])**2+(k-center[2])**2
                        moment[1] += (i-center[0])**2+(k-center[2])**2
                        moment[2] += (i-center[0])**2+(j-center[1])**2
        if pixel != 0:
            moment = moment/pixel
        else:
            pass
        return moment
    def convert_units(self,target:str,origin:str=''): #Done in 1.2.1
        """Gives the correction factor to go from a given units to a target unit.\n
        If no original unit is given, it is supposed to be the one of the Dicom files, stored
        in self.units.\n
        If no valid argument is given, returns a factor of 1.\n
        Keyword arguments:\n
        target -- target units of interest\n
        origin -- units of origin (default '', i.e. self.units) 
        """
        if len(origin) == 0:
            origin = self.units
        if origin =='BQML' and target == 'SUVbw':
            return (self.mass/(self.Dose_inj*1e6))*1000 #*1e6))*1000
        if origin =='SUVbw' and target == 'BQML':
            return (self.Dose_inj*1e6)/(self.mass*1000)
        else:
            self.update_log('Invalid combination of origin and target units, no change made')
            return 1
    def mean_stats(self,keys:int=-1,type_stat:str='TAC'):
        """
        Computes the average of selected statistics for VOI. \n
        Useful for combining multiple TACs together and getting the mean.\n
        Keyword arguments:\n
        keys -- keys of the TACs to combine (default -1)\n
        type_stat -- statistics on which to compute the mean (default TAC)\n
        """
        if isinstance(keys,int):
            if keys == -1:
                if type_stat == 'TAC': keys = np.arange(self.voi_counter)
                elif type_stat == 'linear': key = np.arange(len(self.voi_statistics_avg))
                else: raise Exception("Invalid choice of statistics")
            else:
                raise Exception("Key argument must be an array, ex. [0], not 0")
        elif not isinstance(keys,(list,np.ndarray)):
            raise Exception("Key argument must be an array, ex. [0], not 0")
        output = np.zeros_like(self.time); keys=np.array(keys)
        for i in range(keys.shape[0]):
            if type_stat=='TAC':
                output += self.voi_statistics[keys[i]]/keys.shape[0]
            elif type_stat=='linear':
                output += self.voi_statistics_avg[i]/keys.shape[0]
            else: raise Exception("Invalid choice of statistics")
        return output
    def std_stats(self,keys:int=-1,type_stat:str='TAC'):
        """
        Computes the standard deviation of selected statistics for VOI. \n
        Useful for combining multiple TACs together and getting the std.\n
        Keyword arguments:\n
        keys -- keys of the TACs to combine (default [])\n
        type_stat -- statistics on which to compute the std (default TAC)\n
        """
        if isinstance(keys,int):
            if keys == -1:
                if type_stat == 'TAC': keys = np.arange(self.voi_counter)
                elif type_stat == 'linear': key = np.arange(len(self.voi_statistics_avg))
                else: raise Exception("Invalid choice of statistics")
            else:
                raise Exception("Key argument must be an array, ex. [0], not 0")
        if not isinstance(keys,(list,np.ndarray)):
            raise Exception("Key argument must be an array, ex. [0], not 0")
        output = np.zeros_like(self.time);output2 = np.zeros_like(self.time)
        keys=np.array(keys)
        mean = self.mean_stats(keys,type_stat=type_stat)
        for i in range(keys.shape[0]):
            if type_stat=='TAC':
                output += (self.voi_statistics[keys[i]]-mean)**2/keys.shape[0]
            elif type_stat == 'linear':
                output += (self.voi_statistics_avg[i]-mean)**2/keys.shape[0]
                output2 += self.voi_statistics_std[i]/keys.shape[0]
            else: raise Exception("Invalid choice of statistics")
        return mean,output**(1/2),output2

    def curve_common_vol(self,keys:int=-1):#Done in 2.0.0
        """
        Returns the common volume and the associated TAC for a list of segmentations.\n
        Keyword arguments:\n
        keys -- indices of the segmentation to compare (default -1)\n
        """
        if isinstance(keys,int):
            if keys == -1:
                keys = np.arange(self.voi_counter)
            else:
                return self.voi[f"{keys}"]
        elif isinstance(keys,(list,np.ndarray)):
            keys = np.array(keys)
        else: raise Exception(f"'keys' parameter must be a list or an np.ndarray")
        voi_common = np.ones((self.nb_slice,self.width,self.length))
        for i in range(keys.shape[0]):
            voi_common = voi_common * self.voi[f"{keys[i]}"]
        return self.count_voxels(VOI=voi_common),self.VOI_statistics(VOI=voi_common)

    def sorensen_dice_coefficients(self,keys:np.ndarray):#Added in 1.4.0
        """
        Computes the Sørensen-Dice coefficient for two segmentations.\n
        The result is between 0 and 1.\n
        The explicit formula for two sets A and B is
        S(A,B) = (|A\intersection B|)/(|A|+|B|).\n
        This is expanded for n sets to S(A_1,...,A_n) = n*|\intersection A_i|/\sum|A_i|
        Keyword arguments:\n
        keys -- keys for the segmentation.\n
        """
        keys = np.array(keys)
        intersection = np.ones_like(self.voi[f"{keys[0]}"])
        denominator = 0
        for i in range(keys.shape[0]):
            intersection = np.multiply(intersection,self.voi[f"{keys[i]}"])
            denominator += np.sum(self.voi[f"{keys[i]}"])
        Dice = keys.shape[0]*np.sum(intersection)/denominator
        if Dice <0 or Dice > 1:
            raise Exception(f"Dice is out of bound [0,1], with {Dice}\n Keys = {keys.shape[0]},Inter = {np.sum(intersection)}, denom = {denominator}")
        if np.isnan(Dice):
            return 0
        else:
            return Dice
    def jaccard_index(self,key1:int,key2:int):#Added in 1.4.0
        """
        Computes the Jaccard index for two segmentations.\n
        The result is between 0 and 1.\n
        The explicit formula for two sets A and B is
        S(A,B) = (|A\intersection B|)/(|A U B|) = (|A\intersection B|)/(|A|+|B|-|A\intersection B|).\n
        Keyword arguments:\n
        key1 -- key for the first segmentation.\n
        key2 -- key for the second segmentation.\n
        """
        A = self.voi[f"{key1}"]
        B = self.voi[f"{key2}"]
        Jaccard = np.sum(np.multiply(A,B))/(np.sum(A)+np.sum(B)-np.sum(np.multiply(A,B)))
        if np.isnan(Jaccard):
            return 0
        else:
            return Jaccard
    def Dice_all(self):#Added in 1.4.1
        """
        Computes the Sørensen-Dice coefficient for all VOIs.\n
        Keyword arguments:\n
        nil
        """
        dice_all = np.zeros((self.voi_counter,self.voi_counter))
        for i in range(self.voi_counter):
            for j in range(self.voi_counter):
                dice_all[i,j] = self.sorensen_dice_coefficients([i,j])
        self.dice_all = dice_all
        return dice_all
    def Jaccard_all(self):#Added in 1.4.1
        """
        Computes the Jaccard index for all VOIs.\n
        Keyword arguments:\n
        nil
        """
        jaccard_all = np.zeros((self.voi_counter,self.voi_counter))
        for i in range(self.voi_counter):
            for j in range(self.voi_counter):
                jaccard_all[i,j] = self.jaccard_index(i,j)
        self.jaccard_all = jaccard_all
        return jaccard_all
############################################################
#                                                          #
# This section deals with pharmacokinetic models           #
#                                                          #
############################################################
    def model_three_compartment_A1(self,t:np.ndarray,param:np.ndarray) -> np.ndarray: #Added in 3.0.0
        """Model of the first compartment in a two_compartment model.\n
        Form: A_1(t) = A_0 e^(-k_1/V_1 t)\n

        Keyword arguments:\n
        param -- list of parameters [A_0,k_1/V1]
        """
        return param[0]*(np.exp(-param[1]*t))
    def model_three_compartment_A2(self,t:np.ndarray,param:np.ndarray) -> np.ndarray: #Added in 3.0.0
        """Model of the second compartment in a two_compartment model\n
        Form: A_2(t) = A_0 (k_1V_2/(k_1V_2-k_2V_1))[e^(-k_2/V_2 t)-e^(-k_1/V_1 t)]\n

        Keyword arguments:\n
        param -- list of parameters [A_0,k_1,k_2/V2]
        """
        return param[0]*(np.exp(-param[1]*t)-np.exp(-param[2]*t))
    def model_three_compartment_A2_pause(self,t:np.ndarray,param:np.ndarray) -> np.ndarray:  #Added in 3.0.0
        """Model of the second compartment in a two_compartment model\n
        Form: A_2(t) = A_0 (k_1V_2/(k_1V_2-k_2V_1))[e^(-k_2/V_2 t)-e^(-k_1/V_1 t)]\n
        This model includes a pause, during which there is no change anymore (bubble in the tube)\n

        Keyword arguments:\n
        param -- list of parameters [A_0,k_1,k_2/V2]
        """
        result = np.zeros_like(t)
        for i in range(t.shape[0]):
            if t[i] < param[3]:
                result[i] = param[0]*(np.exp(-param[1]*t[i])-np.exp(-param[2]*t[i]))
            elif t[i] > param[4]:
                result[i] = param[0]*(np.exp(-param[1]*(t[i]-param[4]))-np.exp(-param[2]*(t[i]-param[4])))
            else:
                result[i] = result[i-1]
        return result
############################################################
#                                                          #
# This section deals with methods of fitting               #
#                                                          #
############################################################
    def Fit_SOC(self,y_data:np.ndarray,e_data:np.ndarray,model,ndim:int=3,keep_im_open:bool=False):
        '''
        Use scipy.optimize.curve_fit to fit a given curve to a certain model.\n
        Keyword arguments:\n
        y_data -- function values to fit with the selected model\n
        e_data -- spurious here\n
        model -- type of model to fit\n
        keep_im_open -- spurious here (default False)\n        
        '''
        p0 = np.ones(ndim)
        def func(t,*p): #To make Dynesty and curve_fit work on the same functions; avoid doubling
            return model(t,p)
        try:
            popt, pcov = curve_fit(func,self.time,y_data,p0)
            return popt,np.sqrt(np.diag(pcov)),np.sqrt(np.diag(pcov))
        except RuntimeError:
            self.update_log(f"Error for a fitting, setting all to 0")
            return np.zeros(ndim),np.zeros(ndim),np.zeros(ndim)
    def Fit_Dynesty(self,y_data:np.ndarray,e_data:np.ndarray,model,ndim:int=3,keep_im_open:bool=False):
        '''
        Use Dynesty to fit a given curve to a certain model.\n
        Keyword arguments:\n
        y_data -- function values to fit with the selected model\n
        e_data -- errors on the y_data to fit with the selected model\n
        model -- type of model to fit\n
        keep_im_open -- keeps the Dynesty plots open if set to True; otherwise closes it (default False)\n        
        '''
        e_data[0:2] += max(e_data) #Used to avoid problems with the very low error on low-time values 
        param_init = np.ones((ndim,2))
        param_init[:,0] *= 1e-10
        param_init[:,1] *= 1e8
        def loglike(param,data_t,data_f,data_e):
            prob = 0
            m = model(data_t,param)
            for j in range(m.shape[0]): #This is a specific point for that model
                prob += np.log(2*np.pi*data_e[j])/2-((m[j]-data_f[j])/data_e[j])**2
            return prob
        samplerDynesty = NestedSampler(loglike,self.prior_transform_J,ndim,
                            logl_args=[self.time,y_data,e_data],ptform_args=[param_init],nlive=1500)
        samplerDynesty.run_nested(maxiter=1e6)
        results = samplerDynesty.results
        lnz_truth = ndim * -np.log(2 * 10.)  # analytic evidence solution

        fig,axes = dyplot.traceplot(results, show_titles=True,trace_cmap='viridis', connect=True,connect_highlight=range(5),title_fmt=".4f")
        figu, axe = dyplot.runplot(results, lnz_truth=lnz_truth)  # summary (run) plot
        fg, ax = dyplot.cornerplot(results, color='dodgerblue', show_titles=True,quantiles=None, max_n_ticks=3,title_fmt=".4f")

        self.Bayesian_save_graph(figu,fig,fg)
        std_up = np.zeros(ndim)
        std_down = np.zeros(ndim)
        for i in range(ndim):
            param = axes[i,1].title.get_text()
            std_down[i] = float(param[param.find("-")+1:param.find("^")-1])
            std_up[i] = float(param[param.find("+")+1:param.rfind("}$")])
        if keep_im_open != True: plt.close('all')

        return results.samples[-1,:],std_up,std_down
############################################################
#                                                          #
# This section deals with utilities for Dynesty            #
#                                                          #
############################################################
    def loglike(self,param,data_t,data_f,data_e):
        """Log likelihood used for Dynesty"""
        prob = 0
        #First compute the model with the parameters
        m = self.model(data_t,param)
        #Now compute the probability of the model w.r.t. data
        for j in range(m.shape[0]): #This is a specific point for that model
            prob += np.log(2*np.pi*data_e[j])/2-((m[j]-data_f[j])/data_e[j])**2
        return prob
    def prior_transform_L(self,param_unif_0_1,param_limit):
        """Linear Prior Transform used for Dynesty"""
        #Linear Prior
        param = np.ones_like(param_unif_0_1)
        for i in range(param.shape[0]):
            param[i] = param_unif_0_1[i]*(param_limit[i,1]-param_limit[i,0])+param_limit[i,0]
        return param
    def prior_transform_J(self,param_unif_0_1,param_limit):
        """Jeffrey Prior Transform used for Dynesty (log10)"""
        #Jeffrey Prior
        param = np.ones_like(param_unif_0_1)
        for i in range(param.shape[0]):
            param[i] = param_limit[i,0]*np.exp(param_unif_0_1[i]*np.log(param_limit[i,1]/param_limit[i,0]))
        return param
############################################################
#                                                          #
# This section deals with Bayesian analysis of curves      #
#                                                          #
############################################################
    def Bayesian_analyses(self,key = -1,curves:str = 'Average',method:str='Dynesty',model:str='2_Comp_A2',
                            thresh_perc:float = 0, thresh_value:float = 0,
                            verbose:bool = False,save:bool = True,keep_im_open:bool=False):
        """Takes an array of index for a curve and fit it using a given model and algorithm.

        Keyword arguments:\n
        key -- array of the curves to fit (default [-1])\n
        curves -- Type of curves to be fitted: average or errors (default average)\n
        method -- algorithmic method of Bayesian analysis; can take scipy.optimize.curve_fit or Dynesty (default Dynesty)
        Other possibilities will include EMCEE (To be added).\n
        model -- pharmacokinetic model to fit the data (default '2-compartment'). \n
        thresh_perc -- percentage of the values under which the error is increased (default 0)\n
        thresh_value -- percentage of the maximum value to which errors under the threshold will be set (default 0)\n
        Other possibilities will include 1-compartment, 2-comparment-with-reference (To be added).\n
        param -- array of the subcharacteristic of the curves to fit (default [])\n
        verbose -- print the progress of the process (default False)\n
        keep_im_open -- keeps the Dynesty plots open if set to True; otherwise closes it (default False)\n        
        """
        if (not isinstance(key,(np.ndarray,list))):
            if key == -1 and curves == 'Average': key = np.arange(self.voi_counter);self.update_log("Selecting all TACs")
            elif key == -1 and curves == 'Errors': key = np.arange(len(self.voi_statistics_avg));self.update_log("Selecting all curves with errors")
            else:
                raise Exception("Key argument must be a list or np.array of indices for the curves to fit")
        key = np.array(key)
        if verbose: initial = time.time()
        for i in range(key.shape[0]):
            if verbose: self.update_log(f"Iter {i+1} of {key.shape[0]} after {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")
            value, error_up, error_down = self.Bayesian_analysis(key[i],curves=curves,method=method,model=model,
                                                               thresh_perc = thresh_perc, thresh_value = thresh_value,
                                                               keep_im_open=keep_im_open)
            if i == 0:
                values = np.zeros((key.shape[0],value.shape[0]))
                errors_up = np.zeros_like(values)
                errors_down = np.zeros_like(values)
            values[i,:] = value
            errors_up[i,:] = error_up
            errors_down[i,:] = error_down
            if save:
                if self.bayesian_results_avg == []:
                    self.bayesian_results_avg = np.array([value])
                    self.bayesian_results_e_up = np.array([error_up])
                    self.bayesian_results_e_down = np.array([error_down])
                else:
                    self.bayesian_results_avg = np.append(self.bayesian_results_avg,[value],axis=0)
                    self.bayesian_results_e_up = np.append(self.bayesian_results_e_up,[error_up],axis=0)
                    self.bayesian_results_e_down = np.append(self.bayesian_results_e_down,[error_down],axis=0)
        self.bayesian_counter = self.bayesian_results_avg.shape[1]
        return values, errors_up, errors_down

    def Bayesian_analysis(self,key:int=-1,curves:str = 'Average',method:str='Dynesty',model:str='2_Comp_A2',
                            thresh_perc:float = 0, thresh_value:float = 0,keep_im_open:bool = False):
        """Takes an index for a curve and fit it using a given model and algorithm.\n
        Keyword arguments:\n
        key -- value of the curve to fit (default [-1])\n
        curves -- Type of curves to be fitted: average or errors (default average)\n
        method -- algorithmic method of Bayesian analysis; can take scipy.optimize.curve_fit or Dynesty (default Dynesty)
        Other possibilities will include EMCEE (To be added).\n
        model -- pharmacokinetic model to fit the data (default '2-compartment'). \n
        thresh_perc -- percentage of the values under which the error is increased (default 0)\n
        thresh_value -- percentage of the maximum value to which errors under the threshold will be set (default 0)\n
        Other possibilities will include 1-compartment, 2-comparment-with-reference (To be added).\n
        param -- array of the subcharacteristic of the curves to fit (default [])\n
        keep_im_open -- keeps the Dynesty plots open if set to True; otherwise closes it (default False)\n        
        """
        if (not isinstance(key,int)):
            if key < 0 or key > self.voi_counter:
                raise Exception("Key argument must be integer, greater than 0, and smaller than the total number of segmentations")
        if curves == 'Average':
            y_data = np.copy(self.voi_statistics[key])
            e_data = np.zeros(self.time)
        elif curves == 'Errors':
            y_data = np.copy(self.voi_statistics_avg[key])
            e_data = np.copy(self.voi_statistics_std[key])
        else:
            raise Exception("Invalid choice of curves to fit. Please see function definition for acceptable choices.")
        if (thresh_perc > 0 and thresh_perc < 1) and curves == 'Errors':
            max_value = np.max(y_data)
            for i in range(y_data.shape[0]):
                if e_data[i] < max_value*thresh_perc:
                    e_data[i] = max_value*thresh_value
        if model == '2_Comp_A1':
            model = self.model_three_compartment_A1
            ndim = 2 #Number of parameters of the model
        elif model == '2_Comp_A2':
            model = self.model_three_compartment_A2
            ndim = 3 #Number of parameters of the model
        elif model == '2_Comp_A2_Pause':
            model = self.model_three_compartment_A2_pause
            ndim = 5
        else:
            raise Exception("Invalid choice of model. Please see function definition for acceptable choices.")
        if method == 'Dynesty':
            technique = self.Fit_Dynesty
        elif method == "SOC" or method == "scipy" or method == 'Brute':
            technique = self.Fit_SOC
        else:
            raise Exception("Invalid choice of method. Please see function definition for acceptable choices.")
        try:
            value, error_up, error_down = technique(y_data,e_data,model,ndim=ndim,keep_im_open=keep_im_open)
        except:
            self.update_log(f"Unable to run the parameter extraction on key {key} using method {method}, giving out 0s")
            value = np.zeros(ndim)
            error_up = np.zeros(ndim)
            error_down = np.zeros(ndim)
        return value,error_up, error_down
    
    def Bayesian_save_graph(self,runplot,
                            traceplot,
                            cornerplot):
        """
        Saves the graphs of the Bayesian Analysis when Dynesty is used.\n
        Keyword parameters:\n
        runplot -- Summary (run) plot from the Dynesty analysis\n
        traceplot -- Traceplot from the Dynesty analysis\n
        cornerplot -- Cornerplot from the Dynesty analysis\n
        """

        self.bayesian_graphs_runplot[f"{self.bayesian_dynesty_counter}"] = runplot
        self.bayesian_graphs_traceplot[f"{self.bayesian_dynesty_counter}"] = traceplot
        self.bayesian_graphs_cornerplot[f"{self.bayesian_dynesty_counter}"] = cornerplot

        self.bayesian_dynesty_counter += 1
############################################################
#                                                          #
# This section deals with the noise                        #
#                                                          #
############################################################
    def add_noise(self,noiseType:str = "Gaussian",noiseMu:float = 0,noiseSigma:float = 1,
                            Rayleigh_a:float = 0.0, Rayleigh_b:float = 1.0,
                            Erlang_a:float = 1.0, Erlang_b:float = 1,
                            Unif_a:float = 0, Unif_b:float = 1,
                            Exponential:float = 1.0):
        """
        Adds a noise to the whole acquisition.\n
        Keyword arguments:\n
        noiseType -- Type of noise to add to the whole acquisition (default Gaussian)\n
        noiseMu -- average of the noise (default 0)\n
        noiseSigma -- standard deviation of the noise (default 1)\n
        Rayleigh_a -- first parameter for the Rayleigh noise distribution, its lowest value (default 0)\n
        Rayleigh_b -- second parameter for the Rayleigh noise distribution, its spread (default 0)\n
        """
        if noiseType == "Gaussian":
            self.gaussian_noise(noiseMu= noiseMu, noiseSigma=noiseSigma)
        elif noiseType == "Poisson":
            pass
        elif noiseType == "Rayleigh":
            self.pdf_noise("Rayleigh",[Rayleigh_a,Rayleigh_b])
        elif noiseType == "Exponential":
            self.pdf_noise("Exponential",Exponential)
        elif noiseType == "Uniform":
            self.pdf_noise("Uniform",[Unif_a,Unif_b])
        elif noiseType == "Erlang (Gamma)":
            self.pdf_noise("Erlang",[Erlang_a,Erlang_b])
        else:
            self.update_log("No noise was created")

    def pdf_noise(self,type:str,param:list = [1,1]):
        """
        Computes the noise from a pdf distribution, without explicitely knowing the icdf analytically.\n
        Will add the noise to the full image.\n
        Keyword arguments:\n
        type -- pdf function to use; these come from the Statistic_Functions file\n
        param -- list of parameters to send to the pdf. 
        Must have the same size as the required argument number of parameters of the pdf.\n
        """
        unif = np.random.rand(self.nb_acq*self.nb_slice*self.width*self.length)
        if type == "Erlang":
            noise = SF.get_pdf_from_uniform(unif,SF.Erlang_noise_pdf,param)
        elif type == "Uniform":
            noise = SF.uniform_noise_pdf(unif,a=param[0],b = param[1],type = "icdf")
        elif type == "Exponential":
            noise = SF.exponential_noise_pdf(unif, a=param, type= "icdf")
        elif type == "Rayleigh":
            noise = SF.rayleigh_noise_pdf(unif, a=param[0], b=param[1], type= "icdf")
        
        noise = noise.reshape((self.nb_acq,self.nb_slice,self.width,self.length))
        self.Image = np.absolute(noise + self.Image)

    def gaussian_noise(self,noiseMu:float = 0,noiseSigma:float = 1):
        """
        Creates a Gaussian noise matrix and adds it to the whole image.\n
        Keyword arguments:\n
        noiseMu -- average of the Gaussian Distribution(default 0)\n
        noiseSigma -- Standard deviation of the Gaussian Distribution (default 1)\n        
        """
        noise = np.random.normal(noiseMu,noiseSigma,(self.nb_acq,self.nb_slice,self.width,self.length))
        self.Image = np.absolute(noise + self.Image)
    
    def rayleigh_noise(self,a:float = 0,b:float = 1): #Removed
        """
        Creates a Rayleigh noise matrix and adds it to the whole image.\n
        The distribution is given by 2/b * (z-a)exp(-(z-a)^2/b)
        The mean is a + sqrt(pi b/4) and the variance is b(4-pi)/4.\n
        Keyword arguments:\n
        a -- first parameter for the Rayleigh noise distribution, its lowest value (default 0)\n
        b -- second parameter for the Rayleigh noise distribution, its spread (default 0)\n  
        """
        ones = np.random.rand(self.nb_acq,self.nb_slice,self.width,self.length)
        noise = SF.rayleigh_noise_pdf(ones, a=a, b=b, type= "icdf")
        self.Image = np.absolute(noise + self.Image)
############################################################
#                                                          #
# This section deals with the metrics                      #
#                                                          #
############################################################
    def taxi_cab_distance(self,p1:np.ndarray,p2:np.ndarray): #Done in 1.2.0
        """Computes the taxi cab distance between two points p1 and p2"""
        p1 = np.array(p1)
        p2 = np.array(p2)
        dist = 0
        if np.size(p1)!=np.size(p2):
            raise Exception("Error in the dimensions of the points (they have to be in the same dimensional space")
        else:
            for i in range(np.size(p1)):
                dist += np.abs(p1[i]-p2[i])
        return dist
############################################################
#                                                          #
# This section deals with fillings                         #
#                                                          #
############################################################
    def fill_2D(self,array:np.ndarray,iter_max:int = 1000,method:str='TaxiCab'): #Done in 1.2.0
        """
        Fills a 2-D image, by going towards the center and linking adjacent pixels.
        Acts in a similar way as the ICM.\n
        Keyword arguments:\n
        array -- array to fill\n
        iter_max -- max number of iterations for the filling (default 1000)\n
        method -- method to compute the distance between pixels (default TaxiCab)\n
        """
        neighbour_filling = True
        VOI_pre = 4*np.copy(array)
        center_mass = self.center_of_mass(VOI_pre,D=2).astype(int)
        VOI_pre[int(center_mass[0]),int(center_mass[1])] = -1
        VOI_post = np.copy(array)
        #Filling by going toward the center
        iter_now = 0
        while (iter_now < iter_max and not(VOI_pre==VOI_post).all()):
            VOI_post = np.copy(VOI_pre)
            for i in range(array.shape[0]):
                for j in range(array.shape[1]):
                    if VOI_pre[i,j] > 3.5:
                        #Find neighbor
                        neigh = self.neighbour_towards_center(point = [i,j],target = center_mass,method = method)
                        #Set value to 5, except for the CM
                        if ((int(neigh[0])!=center_mass[0] or int(neigh[1])!=center_mass[1]) and VOI_pre[int(neigh[0]),int(neigh[1])]<0.5):
                            VOI_pre[int(neigh[0]),int(neigh[1])] = 5
                        #Lower value of the used pixel by 2 
                        #(initial 4 ->2)
                        #(filling 5 ->3)
                        VOI_pre[i,j] -= 2
            iter_now += 1
        if iter_now == iter_max:
            self.update_log("Max Iter for Filling reached")
        VOI_post[int(center_mass[0]),int(center_mass[1])] = 4
        #Second part of filling, according to holes left
        iter_now = 0
        VOI_pre = np.copy(VOI_post)
        VOI_post = np.copy(array)
        if neighbour_filling:
            while (iter_now < iter_max and not(VOI_pre==VOI_post).all()):
                VOI_post = np.copy(VOI_pre)
                iter_now += 1
                for i in range(1,array.shape[0]-1):
                    for j in range(1,array.shape[1]-1):
                        try: 
                            if (VOI_pre[i,j] < 0.5 and VOI_pre[i+1,j]+VOI_pre[i-1,j]+VOI_pre[i,j+1]+VOI_pre[i,j-1]>5.5):
                                VOI_pre[i,j] = 2.9
                        except:
                            pass
                iter_now += 1
        VOI_post = np.zeros_like(array)
        for i in range(array.shape[0]):
            for j in range(array.shape[1]):
                if VOI_pre[i,j] > 0.5:
                    VOI_post[i,j] = 1
        if (center_mass == [0,0]).all():
            VOI_post[0,0] = 0
        return VOI_post


    def fill_3D(self,array:np.ndarray,method:str='TaxiCab',combination:int = 3)->np.ndarray: #Done 1.2.0
        """
        Fills a 3-D image, by going towards the center and linking adjacent pixels.
        Three 2-D images are filled successively and then added.\n
        Keyword arguments:\n
        array -- array to fill\n
        method -- method to compute the distance between pixels (default TaxiCab)\n
        combination -- number of combinations for a voxel to be part of the final filling (default 3)\n
        """
        VOI_filled_3D = np.zeros_like(array)
        VOI_filled_0 = np.zeros_like(array)
        VOI_filled_1 = np.zeros_like(array)
        VOI_filled_2 = np.zeros_like(array)

        for w in range(self.nb_slice):
            VOI_filled_0[w,:,:] = self.fill_2D(array[w,:,:],method=method)
        for w in range(self.width):
            VOI_filled_1[:,w,:] = self.fill_2D(array[:,w,:],method=method)
        for w in range(self.length):
            VOI_filled_2[:,:,w] = self.fill_2D(array[:,:,w],method=method)
        VOI_filled_all = VOI_filled_0 + VOI_filled_1 + VOI_filled_2
        for i in range(self.nb_slice):
            for j in range(self.width):
                for k in range(self.length):
                    if(VOI_filled_all[i,j,k]>(combination-0.5)):
                        VOI_filled_3D[i,j,k] = 1
        return VOI_filled_3D

    def neighbour_towards_center(self,point,target,method = 'TaxiCab'): #Done in 1.2.0
        neighbour = np.zeros_like(point)
        if method == 'TaxiCab':
            for i in range(len(point)):
                step = 0
                diff = target[i] - point[i]
                if diff < -0.5:
                    step = -1
                elif diff > 0.5:
                    step = 1
                neighbour[i] = point[i] + step
        elif method == 'vector':
            #Works only in 2D for now
            dist = np.zeros_like(point)
            step = np.zeros_like(point)
            for i in range(len(point)):
                dist[i] = target[i]-point[i]
            if np.abs(dist[0])==np.abs(dist[1]):
                step[0] = dist[0]/np.abs(dist[0])
                step[1] = dist[1]/np.abs(dist[1])
            elif np.abs(dist[0])>=np.abs(dist[1]):
                step[0] = dist[0]/np.abs(dist[0])
            else:
                step[1] = dist[1]/np.abs(dist[1])
            neighbour = point + step
        return neighbour
############################################################
#                                                          #
# This section deals with Loss Functions                   #
#                                                          #
############################################################
    def LossFunction(self, subImage: np.ndarray, Segm: np.ndarray, mus: np.ndarray,
                     m:float = 2,alpha:float = 2):
        """
        Computes the Loss Function of a given segmentation.
        Keyword arguments:\n
        subImage -- Image used for the segmentation\n
        Segm -- current segmentation. Contains the information for all classes\n
        mus -- mean of the distribution for each class\n
        m -- fuzzy parameter (default 2)\n
        alpha -- norm parameter (default 2)\n
        """
        totalEnergy = 0
        Seg_Tmp = np.copy(Segm)
        for i in range(Segm.shape[0]):
            totalEnergy += np.sum((Seg_Tmp[i,:,:,:]**m)*(np.abs(subImage - mus[i])**alpha))
        return totalEnergy
############################################################
#                                                          #
# This section deals with interpolations                   #
#                                                          #
############################################################
    def segm_interpolation_2D(self,slice:np.ndarray,p1:float,p2:float) -> float:
        """
        This function interpolates the segmentation between two points\n
        Keyword arguments:\n
        slice -- slice to use for the interpolation\n
        p1 -- point along the first axis\n
        p2 -- point along the second axis\n
        """
        intX = int(p1)
        intY = int(p2)

        LeftOverX = p1 - intX
        LeftOverY = p2 - intY
        try:
            xp1y = slice[intX+1,intY]

            xprimey = slice[intX,intY]+(xp1y-slice[intX,intY])*LeftOverX

            xprimeyp1 = slice[intX,intY+1]+(slice[intX+1,intY+1]-slice[intX,intY+1])*LeftOverY

            xprimeyprime = xprimey + (xprimeyp1-xprimey)*LeftOverY
        except: 
            xprimeyprime = 0

        return xprimeyprime

    def segm_interpolation_3D(self,boxArray:np.ndarray,point:np.ndarray) -> float:
        """
        This function interpolates the segmentation between two 3D points\n
        Keyword arguments:\n
        boxArray -- slice to use for the interpolation\n
        point -- point along the first axis
        """

        try:
            xd = point[0] - int(point[0])
            yd = point[1] - int(point[1])
            zd = point[2] - int(point[2])

            c00 = boxArray[0]*(1 - xd) + boxArray[1] * xd
            c01 = boxArray[3]*(1 - xd) + boxArray[5] * xd
            c10 = boxArray[2]*(1 - xd) + boxArray[4] * xd
            c11 = boxArray[6]*(1 - xd) + boxArray[7] * xd

            c0 = c00*(1-yd) + c10 * yd
            c1 = c01*(1-yd) + c11 * yd

            return c0*(1 - zd) + c1*zd

        except:
            return 0

############################################################
#                                                          #
# This section deals with neighbours                       #
#                                                          #
############################################################
    def check_neighbours(self,VOI:np.ndarray,seed:list=[-1,-1,-1],precise:bool=True):  
        """
        This function checks to see whether any adjacent voxel is in the VOI. The neighbours checked are 1st degree.\n
        This function takes for granted that the image is 3-D. It also checks whether the voxel of
        interest is close to the edge or not.
        Keyword arguments:\n
        VOI -- VOI from which to check if the voxel is a neighbour for any voxel in the VOI\n
        seed -- voxel of interest, i.e. the one for which all neighbours are checked\n
        precise -- takes in consideration the side of the image if true, allows self-overlap if false (default True) 
        """
        if(seed[0]<0 or seed[0]>self.nb_slice-1 or seed[1]<0 or seed[1]>self.width-1 or seed[2]<0 or seed[2]>self.length-1):
            raise Exception("Voxel of interest must be within the spatial domain of the image")
        i = seed[0]
        j = seed[1]
        k = seed[2]
        max_i = VOI.shape[0]
        max_j = VOI.shape[1]
        max_k = VOI.shape[2]
        if precise:
        #3-Corners
            if(i==0 and j==0 and k==0):
                if(VOI[i+1,j,k]+VOI[i,j+1,k]+VOI[i,j,k+1]): return True
            elif(i==0 and j==0 and k==max_k-1):
                if(VOI[i+1,j,k]+VOI[i,j+1,k]+VOI[i,j,k-1]): return True
            elif(i==0 and j==max_j-1 and k==0):
                if(VOI[i+1,j,k]+VOI[i,j-1,k]+VOI[i,j,k+1]): return True
            elif(i==0 and j==max_j-1 and k==max_k-1):
                if(VOI[i+1,j,k]+VOI[i,j-1,k]+VOI[i,j,k-1]): return True
            elif(i==max_i-1 and j==0 and k==0):
                if(VOI[i-1,j,k]+VOI[i,j+1,k]+VOI[i,j,k+1]): return True
            elif(i==max_i-1 and j==0 and k==max_k-1):
                if(VOI[i-1,j,k]+VOI[i,j+1,k]+VOI[i,j,k-1]): return True
            elif(i==max_i-1 and j==max_j-1 and k==0):
                if(VOI[i-1,j,k]+VOI[i,j-1,k]+VOI[i,j,k+1]): return True
            elif(i==max_i-1 and j==max_j-1 and k==max_k-1):
                if(VOI[i-1,j,k]+VOI[i,j-1,k]+VOI[i,j,k-1]): return True
            #2-corners (L)
            elif(i==0 and j==0):
                if(VOI[i+1,j,k]+VOI[i,j+1,k]+VOI[i,j,k+1]+VOI[i,j,k-1]): return True    
            elif(i==0 and j==max_j-1):
                if(VOI[i+1,j,k]+VOI[i,j-1,k]+VOI[i,j,k+1]+VOI[i,j,k-1]): return True   
            elif(i==max_i-1 and j==0):
                if(VOI[i-1,j,k]+VOI[i,j+1,k]+VOI[i,j,k+1]+VOI[i,j,k-1]): return True   
            elif(i==max_i-1 and j==max_j-1):
                if(VOI[i-1,j,k]+VOI[i,j-1,k]+VOI[i,j,k+1]+VOI[i,j,k-1]): return True   

            elif(i==0 and k==0):
                if(VOI[i+1,j,k]+VOI[i,j-1,k]+VOI[i,j+1,k]+VOI[i,j,k+1]): return True    
            elif(i==0 and k==max_k-1):
                if(VOI[i+1,j,k]+VOI[i,j-1,k]+VOI[i,j+1,k]+VOI[i,j,k-1]): return True   
            elif(i==max_i-1 and k==0):
                if(VOI[i-1,j,k]+VOI[i,j-1,k]+VOI[i,j+1,k]+VOI[i,j,k+1]): return True   
            elif(i==max_i-1 and k==max_k-1):
                if(VOI[i-1,j,k]+VOI[i,j-1,k]+VOI[i,j+1,k]+VOI[i,j,k-1]): return True   

            elif(j==0 and k==0):
                if(VOI[i-1,j,k]+VOI[i+1,j,k]+VOI[i,j+1,k]+VOI[i,j,k+1]): return True    
            elif(j==0 and k==max_k-1):
                if(VOI[i-1,j,k]+VOI[i+1,j,k]+VOI[i,j+1,k]+VOI[i,j,k-1]): return True    
            elif(j==max_j-1 and k==0):
                if(VOI[i-1,j,k]+VOI[i+1,j,k]+VOI[i,j-1,k]+VOI[i,j,k+1]): return True    
            elif(j==max_j-1 and k==max_k-1):
                if(VOI[i-1,j,k]+VOI[i+1,j,k]+VOI[i,j-1,k]+VOI[i,j,k-1]): return True    
            #Sides
            elif(i==0):
                if(VOI[i+1,j,k]+VOI[i,j-1,k]+VOI[i,j+1,k]+VOI[i,j,k-1]+VOI[i,j,k+1]>0.5): return True 
            elif(i==max_i-1):
                if(VOI[i-1,j,k]+VOI[i,j-1,k]+VOI[i,j+1,k]+VOI[i,j,k-1]+VOI[i,j,k+1]>0.5): return True 
            elif(j==0):
                if(VOI[i-1,j,k]+VOI[i+1,j,k]+VOI[i,j+1,k]+VOI[i,j,k-1]+VOI[i,j,k+1]>0.5): return True 
            elif(j==max_j-1):
                if(VOI[i-1,j,k]+VOI[i+1,j,k]+VOI[i,j-1,k]+VOI[i,j,k-1]+VOI[i,j,k+1]>0.5): return True 
            elif(k==0):
                if(VOI[i-1,j,k]+VOI[i+1,j,k]+VOI[i,j-1,k]+VOI[i,j+1,k]+VOI[i,j,k+1]>0.5): return True             
            elif(k==max_k-1):
                if(VOI[i-1,j,k]+VOI[i+1,j,k]+VOI[i,j-1,k]+VOI[i,j+1,k]+VOI[i,j,k-1]>0.5): return True             
            elif(VOI[i-1,j,k]+VOI[i+1,j,k]+VOI[i,j-1,k]+VOI[i,j+1,k]+VOI[i,j,k-1]+VOI[i,j,k+1]>0.5): return True
            else: return False
        else:
            if (VOI[i-1,j,k]+VOI[i+1,j,k]+VOI[i,j-1,k]+VOI[i,j+1,k]+VOI[i,j,k-1]+VOI[i,j,k+1]>0.5): return True
            else: return False

    def count_neighbours_other_class(self,VOI:np.ndarray,seed:np.ndarray,classValue:int,precise:bool = True):
        """
        Count the number of neighbours whose class is not the same as the seed.\n
        The neighbours checked are 1st degree.\n
        This function takes for granted that the image is 3-D. It also checks whether the voxel of
        interest is close to the edge or not.
        Keyword arguments:\n
        VOI -- VOI from which to check if the voxel is a neighbour for any voxel in the VOI\n
        seed -- voxel of interest, i.e. the one for which all neighbours are checked\n
        precise -- takes in consideration the side of the image if true, allows self-overlap if false (default True) 
        """
        i = seed[0]
        j = seed[1]
        k = seed[2]
        max_i = VOI.shape[0]
        max_j = VOI.shape[1]
        max_k = VOI.shape[2]
        #3-Corners
        value = 0
        count = 0

        if(i != 0):
            value += VOI[i-1,j,k]
            count += 1
        if(j != 0):
            value += VOI[i,j-1,k]
            count += 1
        if(k != 0):
            value += VOI[i,j,k-1]
            count += 1
        if(i != max_i-1):
            value += VOI[i+1,j,k]
            count += 1
        if(j != max_j-1):
            value += VOI[i,j+1,k]
            count += 1
        if(k != max_k-1):
            value += VOI[i,j,k+1]
            count += 1

        if(classValue == 0):
            return value
        elif(classValue==1):
            return (count-value)

    def axis(self,order,d = 1):
        """
        Gives the neighbours for 1st, 2nd, and 3rd.\n
        Keyword arguments:\n
        order -- order of the neighbours to look at. Can be 1, 2, or 3, or an array of these.\n
        d -- distance to stretch the axes (default 1)\n
        """
        first_order = np.array([[1,0,0],[-1,0,0],
                                [0,1,0],[0,-1,0],
                                [0,0,1],[0,0,-1]])
        second_order = np.array([[1,1,0],[-1,-1,0],[-1,1,0],[1,-1,0],
                                [0,1,1],[0,-1,-1],[0,-1,1],[0,1,-1],
                                [1,0,1],[-1,0,-1],[-1,0,1],[1,0,-1]])
        third_order = np.array([[1,1,1],[-1,-1,-1],
                                [1,1,-1],[-1,-1,1],
                                [1,-1,1],[-1,1,-1],
                                [-1,1,1],[1,-1,-1]])
        all_orders = np.array([first_order,second_order,third_order],dtype=object)
        if isinstance(order,(int)) and isinstance(d,(int,float)):
            if order == 1 or order == 2 or order == 3:
                return d*all_orders[order-1]
            else:
                raise Exception(f"Invalid value for the order.\nThe value given was {order} and must be 0, 1, or 2.")
        elif isinstance(order,(np.ndarray,list)):
            order = np.array(order) - 1 #To fit with the position of the array
            if isinstance(d,(int,float)):
                d = d*np.ones_like(order)
            else: d = np.array(d)
            if order.shape[0]!=d.shape[0]:
                raise Exception(f"'d' must be an integer or an array of the same length as 'order'.\nHere, d had shape {d.shape[0]} and order had shape {order.shape[0]}")
            order = np.array(order)
            for i in range(order.shape[0]):
                if i == 0:
                    axes = d[i]*all_orders[order[i]]
                else:
                    axes = np.concatenate((axes,d[i]*all_orders[order[i]]))
            return axes
############################################################
#                                                          #
# This section has utility functions                       #
#                                                          #
############################################################      

    def FindRadioNuclide(self) -> str:  
        """
        This function finds the good name of the radionuclide from the util list.
        If not found, returns the default F18
        """

        name_tmp = self.radioNuclideInit
        for dict, names in util.radioNuclideNameVariations.items():
            if name_tmp in names.values():
                return dict       
            
        #If nothing else is found
        return "F18" 

class CombinedResults(object):
    """Combines the Results from Different DicomImage Files"""
    def __init__(self):
        """Initialisation"""
        self.TotalAcqNbr = 0
        self.SegmSchemeNbr = 0
        self.SegmSchemeNbrInconstant = False

        self.VoiStatisticsTotal = {}

        self.Dice = {}
        self.Jaccard = {}

        self.VoiStatisticsAvgTotal = {}
        self.VoiStatisticsStdTotal = {}

        self.BayesianStdTotal = {}
        self.BayesianEUpTotal = {}
        self.BayesianEDownTotal = {}

    def addResult(self,path : str, name: str = "", scheme: str = "", newAcq : bool = False, dim : int = 1):
        """Opens a DicomImage class and adds the Result to this class"""

        if scheme == "":
            raise Exception("For a new entry, 'scheme' must not be empty.")
        if newAcq:
            if name == "":
                raise Exception("For a new entry, 'name' must not be empty.")

        with open(path, 'rb') as input:
            DI = pickle.load(input)

        if newAcq:
            self.TotalAcqNbr += 1
            if dim != self.SegmSchemeNbr:
                self.SegmSchemeNbrInconstant = True
                if dim > self.SegmSchemeNbr:
                    self.SegmSchemeNbr = dim

            self.VoiStatisticsTotal[f"{name}"] = {}

            self.Dice[f"{name}"] = {}
            self.Jaccard[f"{name}"] = {}

            self.VoiStatisticsAvgTotal[f"{name}"] = {}
            self.VoiStatisticsStdTotal[f"{name}"] = {}
            
            self.BayesianStdTotal[f"{name}"] = {}
            self.BayesianEUpTotal[f"{name}"] = {}
            self.BayesianEDownTotal[f"{name}"] = {}

        self.VoiStatisticsTotal[f"{name}"][f"{scheme}"] = DI.voi_statistics

        self.Dice[f"{name}"][f"{scheme}"] = DI.dice_all
        self.Jaccard[f"{name}"][f"{scheme}"] = DI.jaccard_all

        self.VoiStatisticsAvgTotal[f"{name}"][f"{scheme}"] = DI.voi_statistics_avg
        self.VoiStatisticsStdTotal[f"{name}"][f"{scheme}"] = DI.voi_statistics_std
        try:
            if len(DI.bayesian_results_avg) != 0:
                self.BayesianStdTotal[f"{name}"][f"{scheme}"] = DI.bayesian_results_avg
                self.BayesianEUpTotal[f"{name}"][f"{scheme}"] = DI.bayesian_results_e_up
                self.BayesianEDownTotal[f"{name}"][f"{scheme}"] = DI.bayesian_results_e_down
            else:
                #DI.Bayesian_analyses(key = -1, curves = 'Errors', verbose = True)

                self.BayesianStdTotal[f"{name}"][f"{scheme}"] = DI.bayesian_results_avg
                self.BayesianEUpTotal[f"{name}"][f"{scheme}"] = DI.bayesian_results_e_up
                self.BayesianEDownTotal[f"{name}"][f"{scheme}"] = DI.bayesian_results_e_down                
        except: pass



    