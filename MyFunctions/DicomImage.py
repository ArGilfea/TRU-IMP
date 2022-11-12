from operator import sub
from unicodedata import name
import numpy as np
from scipy.optimize import curve_fit
from skimage import feature
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import time
from numba import jit
from dynesty import NestedSampler
from dynesty import plotting as dyplot

class DicomImage(object):
    """
    Contains an image from Nuclear Medicine with many functions to compute segmentations, statistics, parameters and outputs images.
    """
    def __init__(self,Image:np.ndarray,time:list = [0],name:str='',rescaleSlope:list = [1],rescaleIntercept:list = [0],
                voxel_thickness:int=1,voxel_width:int=1,voxel_length:int=1,time_scale:str='min',
                flat_images:bool=False,units:str='',mass:int = 1,Dose_inj:int = 0,Description:str=''):
        #General Info
        self.version = '4.0.0'
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
        self.rescaleSlope = rescaleSlope
        self.rescaleIntercept = rescaleIntercept
        self.voxel_thickness = voxel_thickness
        self.voxel_width = voxel_width
        self.voxel_length = voxel_length
        self.voxel_volume = voxel_thickness*voxel_width*voxel_length
        self.Instances = self.nb_acq*self.nb_slice*self.width*self.length
        self.mass = mass
        self.Dose_inj = Dose_inj
        if np.array(time).size != Image.shape[0]:
            self.time = np.zeros((self.nb_acq))
        else:
            self.time = time
        self.time_scale = time_scale
        self.units = units
        self.voi_counter = 0
        self.voi = {}
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
        self.axial_flats = np.zeros((self.nb_acq,self.width,self.length))
        self.coronal_flats = np.zeros((self.nb_acq,self.nb_slice,self.length))
        self.sagittal_flats = np.zeros((self.nb_acq,self.nb_slice,self.width))
        if flat_images: #Added in 1.1.2
            for i in range(self.nb_acq):
                self.axial_flats[i,:,:] = self.axial_flat(i)
                self.sagittal_flats[i,:,:] = self.sagittal_flat(i)
                self.coronal_flats[i,:,:] = self.coronal_flat(i)

    def select_acq(self,acq:int = -1): #Done in 1.1
        """Returns a specific 3D (spatial) volume image, determined by the key input
        
        Keyword arguments:\n
        acq -- the timeframe of interest (default -1)
        """
        region = np.zeros((self.nb_slice,self.width,self.length))
        if(acq>= 0) and (acq < self.nb_acq):
            region = self.Image[acq,:,:,:]
        return region
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
    def show_flats(self,acq:int=-2,key:int=-2,name:str=''): #Done in 1.2.1
        """Outputs three flat images in one figure of the three cuts (axial, sagittal and coronal) 
        of a given timeframe or voi.\n
        The specific image flattened and shown is given by the argument which is greater or equal to 0.
        (There must only one, otherwise an error is raised).\n
        Keyword arguments:\n
        acq -- the timeframe of interest (default -2)\n
        key -- the VOI of interest (default -2). (-1 for all VOIs)\n
        name -- optional name for the graphs (default '')\n
        """
        if ((acq >= 0 and key >= 0) or (acq < -1 and key < -1)):
            raise Exception("Key xor Acq argument must be greater than 0 to select a valid image to check")
        if key >= self.voi_counter:
            raise Exception("Key argument must be lower than the number of VOIs")
        if acq >= 0:
            fig, axs = plt.subplots(2,2)
            axs[0,0].pcolormesh(self.axial_flat(acq=acq));axs[0,0].set_title("Axial");axs[0,0].set_xlabel("y (voxels)");axs[0,0].set_ylabel("z (voxels)")
            axs[1,0].pcolormesh(self.sagittal_flat(acq=acq));axs[1,0].set_title("Sagittal");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("y (voxels)")
            axs[0,1].pcolormesh(self.coronal_flat(acq=acq));axs[0,1].set_title("Coronal");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("z (voxels)")
            fig.suptitle(f"Time Acquisition {acq} {name}")
        elif key >= 0:
            fig, axs = plt.subplots(2,2)
            axs[0,0].pcolormesh(self.axial_flat(counter = key));axs[0,0].set_title("Axial");axs[0,0].set_xlabel("y (voxels)");axs[0,0].set_ylabel("z (voxels)")
            axs[1,0].pcolormesh(self.sagittal_flat(counter = key));axs[1,0].set_title("Sagittal");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("y (voxels)")
            axs[0,1].pcolormesh(self.coronal_flat(counter = key));axs[0,1].set_title("Coronal");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("z (voxels)")
            fig.suptitle(f"VOI {key} {name} {self.voi_name[key]}")
        elif key == -1:
            for i in range(self.voi_counter):
                fig, axs = plt.subplots(2,2)
                axs[0,0].pcolormesh(self.axial_flat(counter = i));axs[0,0].set_title("Axial");axs[0,0].set_xlabel("y (voxels)");axs[0,0].set_ylabel("z (voxels)")
                axs[1,0].pcolormesh(self.sagittal_flat(counter = i));axs[1,0].set_title("Sagittal");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("y (voxels)")
                axs[0,1].pcolormesh(self.coronal_flat(counter = i));axs[0,1].set_title("Coronal");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("z (voxels)")
                fig.suptitle(f"VOI {i} {name} {self.voi_name[i]}")                         
    def show_point(self,point:list = [-1,0,0,0],star:bool=False,log:bool=False, sub_im:list = [[-1,-1],[-1,-1],[-1,-1]]): #Done in 1.2.1
        """Outputs three images in one figure of the three cuts (axial, sagittal and coronal) 
        at a given acquisition and spatial point.\n
        The specific image flattened and shown is given by the argument which is greater or equal to 0.
        (There must only one, otherwise an error is raised).\n
        Keyword arguments:\n
        point -- point from which to look in the three planes (default [-1,0,0,0])\n
        star -- indicates with a star the location of the point (default False)\n
        log -- apply a log_e on all voxels of the image, which is useful for low contrast images (default True)\n
        """
        sub_im = np.array(sub_im)
        if (point[0]<0 or point[0] >= self.nb_acq):
            raise Exception("Acquisition must be between 0 and the number of acquisitions")
        if (point[1]<0 or point[1]>= self.nb_slice) or (point[2]<0 or point[2]>= self.width) or (point[3]<0 or point[3]>= self.length):
            raise Exception("Spatial values must be within the image")
        fig, axs = plt.subplots(2,2)
        if np.sum(sub_im < 0):
            if log:
                axs[0,0].pcolormesh(np.log(self.Image[point[0],point[1],:,:]));axs[0,0].set_title("Axial")
                axs[1,0].pcolormesh(np.log(self.Image[point[0],:,:,point[3]]));axs[1,0].set_title("Sagittal")
                axs[0,1].pcolormesh(np.log(self.Image[point[0],:,point[2],:]));axs[0,1].set_title("Coronal")
            else:
                axs[0,0].pcolormesh(self.Image[point[0],point[1],:,:]);axs[0,0].set_title("Axial")
                axs[1,0].pcolormesh(self.Image[point[0],:,:,point[3]]);axs[1,0].set_title("Sagittal")
                axs[0,1].pcolormesh(self.Image[point[0],:,point[2],:]);axs[0,1].set_title("Coronal")
            fig.suptitle(f"Three slice around point: {point}")      
        else:
            if log:
                axs[0,0].pcolormesh(np.log(self.Image[point[0],point[1],sub_im[1,0]:sub_im[1,1],sub_im[2,0]:sub_im[2,1]]));axs[0,0].set_title("Axial")
                axs[1,0].pcolormesh(np.log(self.Image[point[0],sub_im[0,0]:sub_im[0,1],sub_im[1,0]:sub_im[1,1],point[3]]));axs[1,0].set_title("Sagittal")
                axs[0,1].pcolormesh(np.log(self.Image[point[0],sub_im[0,0]:sub_im[0,1],point[2],sub_im[2,0]:sub_im[2,1]]));axs[0,1].set_title("Coronal")
            else:
                axs[0,0].pcolormesh(np.arange(sub_im[2,0],sub_im[2,1]),np.arange(sub_im[1,0],sub_im[1,1]),
                                    self.Image[point[0],point[1],sub_im[1,0]:sub_im[1,1],sub_im[2,0]:sub_im[2,1]]);axs[0,0].set_title("Axial")
                axs[1,0].pcolormesh(np.arange(sub_im[1,0],sub_im[1,1]),np.arange(sub_im[0,0],sub_im[0,1]),
                                    self.Image[point[0],sub_im[0,0]:sub_im[0,1],sub_im[1,0]:sub_im[1,1],point[3]]);axs[1,0].set_title("Sagittal")
                axs[0,1].pcolormesh(np.arange(sub_im[2,0],sub_im[2,1]),np.arange(sub_im[0,0],sub_im[0,1]),
                                    self.Image[point[0],sub_im[0,0]:sub_im[0,1],point[2],sub_im[2,0]:sub_im[2,1]]);axs[0,1].set_title("Coronal")
            fig.suptitle(f"Three slice around point: {point} for a reduced image around ({sub_im[0,0]}-{sub_im[0,1]},{sub_im[1,0]}-{sub_im[1,1]},{sub_im[2,0]}-{sub_im[2,1]})")    
        if star:
            axs[0,0].plot(point[3],point[2],'*',markersize = 6,color='y') 
            axs[1,0].plot(point[2],point[1],'*',markersize = 6,color='y') 
            axs[0,1].plot(point[3],point[1],'*',markersize = 6,color='y') 
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
            for i in range(int(dim_sub[0][0]),int(dim_sub[0][1])+1):
                for j in range(int(dim_sub[1][0]),int(dim_sub[1][1])+1):
                    for k in range(int(dim_sub[2][0]),int(dim_sub[2][1])+1):
                        new_image[t,i,j,k] = self.Image[t,i,j,k]
        return new_image
    def linear_shift(self,shifts:np.ndarray=np.array([0,0,0]),counter:int = -1,save:bool=True,name:str=''):
        """
        Shift a given VOI linearly according to the input shifts.\n
        Each voxel of the VOI is shifted linearly along the three axes.\n
        Keyword arguments:\n
        shifts --
        counter --
        save -- save the VOI if True, else, return it as an output (default False)
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
            print(f"Nothing happened, for counter argument ({counter}) is not valid. It needed to be between 0 and {self.voi_counter}")
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
                print(f"% done for key {key}: {(i+1)/shift_axis.shape[0]*100:.2f}% in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}")
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
            if verbose: print(f"Errors done: {(i+1)/keys.shape[0]*100:.2f}% in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}")
############################################################
#                                                          #
# This section deals with the adding and removal of VOIs   #
#                                                          #
############################################################
    def save_VOI(self,VOI:np.ndarray,name:str='',do_stats:bool=True,do_moments:bool=True): #Added in 1.3.1
        """
        Save the VOI being worked with in the dictionary
        Keyword arguments:\n
        VOI -- VOI to be saved\n
        name -- name of the VOI to be saved (default '')\n
        do_stats -- compute the statistics for the VOI of interest (default True)\n
        do_moments -- compute the moments for the VOI of interest (default True)\n
        """        
        self.voi[f"{self.voi_counter}"] = VOI
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
            new_voxels = []
            new_name = []
            new_CM = []
            new_moment = []
            new_stats = []
            for i in range(key,self.voi_counter):
                self.voi[f"{i-1}"] = self.voi[f"{i}"]
            for i in range(self.voi_counter):
                if i!=key:
                    new_voxels.append(self.voi_voxels[i])
                    new_name.append(self.voi_name[i])
                    new_CM.append(self.voi_center_of_mass[key])
                    new_moment.append(self.voi_moment_of_inertia[key])
                    new_stats.append(self.voi_statistics[key])
            del self.voi[f"{key}"]
            self.voi_counter -= 1
            self.voi_voxels = new_voxels
            self.voi_name = new_name
            self.voi_center_of_mass = new_CM
            self.voi_moment_of_inertia = new_moment
            self.voi_statistics = new_stats
                
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

    def VOI_canny(self,subimage:np.ndarray = np.array([]),combination:int = 2,sigma:float=1,name:str='',do_moments:bool = False,save:bool = True,do_stats:bool=False): #Done in 1.2.0
        """This function creates the contour of a 3D image using Canny edge detection algorithm, with sigma for the Gaussian filter.
        The Canny edge detection algorithm works in 2D, so every 2D plane has to be considered individually.
        The combination options determine how many of the voxels in a given dimension have to be on the 2D contour to be counted.        
        Keyword arguments:\n
        subimage -- image on which to apply the Canny edge algorithm (default [], i.e. all the 3D volume)\n
        combination -- combination parameter for the number of necessary 2D Canny on a given voxel to make that voxel part of the 
        VOI (default 2)\n
        sigma -- standard deviation of the Gaussian filter used in the Canny algorithm (default 1)\n
        name -- name of the VOI (default '')\n
        do_moments -- compute the moments of the VOI and store them (default False)\n
        save -- add the VOI to the dictionary of VOIs, with relevant infos (default True); if False, return instead the VOI alone\n
        do_stats -- compute the TACs relative to the VOI (default False)\n
        """
        if subimage.size == 0:
            subimage = self.select_acq(0)
        VOI = np.zeros_like(subimage)
        Canny_2D_sagittal = np.zeros_like(subimage)
        Canny_2D_coronal = np.zeros_like(subimage)
        Canny_2D_axial = np.zeros_like(subimage)
        for i in range(subimage.shape[0]):
            im_tmp = subimage[i,:,:]
            Canny_2D_axial[i,:,:] = feature.canny(im_tmp,sigma=sigma)
        for j in range(subimage.shape[1]):
            im_tmp = subimage[:,j,:].reshape((subimage.shape[0],subimage.shape[2]))
            Canny_2D_coronal[:,j,:] = feature.canny(im_tmp,sigma=sigma)
        for k in range(subimage.shape[2]):
            im_tmp = subimage[:,:,k].reshape((subimage.shape[0],subimage.shape[1]))
            Canny_2D_sagittal[:,:,k] = feature.canny(im_tmp,sigma=sigma)
        Canny_total = Canny_2D_axial+Canny_2D_coronal+Canny_2D_sagittal
        for i in range(subimage.shape[0]):
            for j in range(subimage.shape[1]):
                for k in range(subimage.shape[2]):
                    if Canny_total[i,j,k] >= int(combination):
                        VOI[i,j,k] = 1
        if save:
            self.save_VOI(VOI,name=name,do_stats=do_stats,do_moments=do_moments)
        return VOI
    def VOI_Canny_filled(self,subinfo = [[-1,0],[0,0],[0,0]],acq=0,combination = 2,
                        sigma=1,name='',do_moments = False,method='taxicab',
                        do_stats = False,save=True): #Done in 1.2.0
        """
        Computes a segmentation using Canny for the contour, then filling it.
        Keyword arguments:\n
        acq -- timeframes on which to base the static segmentations (default 0)\n
        subinfo -- smaller region upon which to do the segmentations (default [-1], i.e. the whole image will be considered)\n
        sigma -- used for the Canny segmentation (default 5)\n
        combination -- combination parameter for the number of necessary 2D Canny on a given voxel to make that voxel part of the 
        VOI (default 2)\n
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
        Cannied = self.VOI_canny(Image,combination,sigma,name,do_moments,save=False)
        Canny_filled = self.fill_3D(Cannied,method)
        if save:
            self.save_VOI(Canny_filled,name=name,do_stats=do_stats,do_moments=do_moments)
        else:
            return Canny_filled
    def VOI_filled_noNumba(self,seed: np.ndarray = [[-1,-1,-1]],factor:float = 1,
        acq:int=0,sub_im: np.ndarray = [[-1,-1],[-1,-1],[-1,1]],
        name: str = '',max_iter: int = 100,do_moments: bool = False,
        save:bool=True,do_stats:bool=False,
        verbose:bool=True,save_between:bool=False,fraction_f:np.ndarray=[-1,0],
        size_f:np.ndarray=[-1,0],voxels_f:np.ndarray=[-1,0],counter_save: int = 0): #Done in 1.3.2
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
                print("Iter:", iteration,", x=",region_mean,", std=",region_std,", voxels =",np.sum(VOI_old))
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
            #print(f"Saving VOI with f = {factor}, for size = {fraction_VOI} is within the range [{fraction_f[0]},{fraction_f[1]}].")
            save_between = True
        if size_VOI*self.voxel_volume/1000 >= size_f[0] and size_VOI*self.voxel_volume/1000 <= size_f[1]:
            #print(f"Saving VOI with f = {factor}, for size = {size_VOI*self.voxel_volume/1000} is within the range [{size_f[0]},{size_f[1]}].")
            save_between = True
        if size_VOI >= voxels_f[0] and size_VOI <= voxels_f[1]:
            #print(f"Saving VOI with f = {factor:.3f}, for size = {size_VOI} is within the range [{voxels_f[0]:.3f},{voxels_f[1]:.3f}].")
            save_between = True
        if verbose:
            print('Stopped the filling at iter', {iteration},', while the max_iter was ',{max_iter})
        if save or save_between:
            counter_save += 1
            self.save_VOI(VOI,name=name,do_stats=do_stats,do_moments=do_moments)
        return VOI, counter_save
    def VOI_filled(self,seed: np.ndarray = [[-1,-1,-1]],factor:float = 1,
        acq:int=0,sub_im: np.ndarray = [[-1,-1],[-1,-1],[-1,1]],
        name: str = '',max_iter: int = 100,do_moments: bool = False,
        save:bool=True,do_stats:bool=False,
        verbose:bool=True,save_between:bool=False,fraction_f:np.ndarray=[-1,0],
        size_f:np.ndarray=[-1,0],voxels_f:np.ndarray=[-1,0],counter_save: int = 0,
        loop = 0): #Done in 1.3.2
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
                #print(f"Iter: {iteration}, x={region_mean:.5e}, std={region_std:.5e}, voxels ={np.sum(VOI_old):.8e}")
                print("Iter:", iteration,", x=",region_mean,", std=",region_std,", voxels =",np.sum(VOI_old))
            ### Numba
            ###
            VOI, range_im = loop(VOI,VOI_old,range_im,range_im_tmp,region_mean,region_std,factor,subimage,min_i,min_j,min_k,max_i,max_j,max_k)
        size_VOI = np.sum(VOI)
        fraction_VOI = np.sum(VOI)/(self.nb_acq*self.width*self.length)
        if fraction_VOI >= fraction_f[0] and fraction_VOI <= fraction_f[1]:
            #print(f"Saving VOI with f = {factor}, for size = {fraction_VOI} is within the range [{fraction_f[0]},{fraction_f[1]}].")
            save_between = True
        if size_VOI*self.voxel_volume/1000 >= size_f[0] and size_VOI*self.voxel_volume/1000 <= size_f[1]:
            #print(f"Saving VOI with f = {factor}, for size = {size_VOI*self.voxel_volume/1000} is within the range [{size_f[0]},{size_f[1]}].")
            save_between = True
        if size_VOI >= voxels_f[0] and size_VOI <= voxels_f[1]:
            #print(f"Saving VOI with f = {factor:.3f}, for size = {size_VOI} is within the range [{voxels_f[0]:.3f},{voxels_f[1]:.3f}].")
            save_between = True
        if verbose:
            print('Stopped the filling at iter', {iteration},', while the max_iter was ',{max_iter})
        if save or save_between:
            counter_save += 1
            self.save_VOI(VOI,name=name,do_stats=do_stats,do_moments=do_moments)
        return VOI, counter_save
    def VOI_filled_f(self,seed:np.ndarray=[-1,-1,-1],factor:np.ndarray = [0,1],
        steps:int=5,acq:int=0,sub_im:np.ndarray = [[-1,-1],[-1,-1],[-1,-1]],
        name:str='',
        max_iter:int = 100,do_moments:bool= False,do_stats:bool=False,
        verbose:bool=False,verbose_graphs:bool=False,
        save_between:bool=False,max_number_save:int=10000,
        threshold:float=0.99,fraction_f:np.ndarray=[-1,0],size_f:np.ndarray=[-1,0],
        voxels_f:np.ndarray=[-1,0],
        min_f_growth:float = 0,growth:float=-1,break_after_f:bool=False,
        numba = True): #Done in 1.3.2
        """
        Segment by filling over a range of f to determine which is best.
        Keyword parameters:\n
        steps -- number of separations for the factor parameter (default 5)\n
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
            if verbose:
                print(f"f value = {f_range[f]:.3f}, step {f+1}/{steps}")
            if counter_save >= max_number_save:
                fraction_f=[-1,0];size_f=[-1,0];voxels_f=[-1,0]
                break
            if numba:
                VOI_filled = self.VOI_filled(seed=np.array(seed),factor=f_range[f],acq=acq,sub_im=np.array(sub_im),max_iter=max_iter,save=False,
                    verbose=verbose,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f}",
                    do_moments=do_moments,do_stats=do_stats,fraction_f=fraction_f,size_f=size_f,voxels_f=voxels_f,counter_save=counter_save,loop=loop)
            else:
                VOI_filled = self.VOI_filled_noNumba(seed=np.array(seed),factor=f_range[f],acq=acq,sub_im=np.array(sub_im),max_iter=max_iter,save=False,
                    verbose=verbose,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f}",
                    do_moments=do_moments,do_stats=do_stats,fraction_f=fraction_f,size_f=size_f,voxels_f=voxels_f,counter_save=counter_save)
            counter_save = VOI_filled[1]
            voxels[f] = self.count_voxels(VOI=VOI_filled[0])
            ratio_range[f] = (voxels[f]/image_size)
            if (fraction_f[0] + fraction_f[1])!=-1 or (size_f[0] + size_f[1])!=-1 or (voxels_f[0] + voxels_f[1])!=-1:
                if((break_after_f and voxels[f] > voxels_f[1]) \
                        and (ratio_range[f] > fraction_f[1] and voxels[f]*self.voxel_volume/1000 > size_f[1])) \
                        and (counter_save == 0 and max_number_save > 0):
                    print(f"Saving the least worst segmentation.")
                    self.save_VOI(VOI_filled[0],name=name,do_stats=do_stats,do_moments=do_moments)
                    break
            if size_sub_im>0 and voxels[f]/size_sub_im > threshold:
                print(f"Stopping at iter {f+1}, because threshold of {threshold} has been reached with {voxels[f]/size_sub_im:.3f}.")
                if counter_save == 0 and max_number_save > 0:
                    print(f"Saving a backup segmentation, for nothing was satisfactory.")
                    if numba:
                        self.VOI_filled(seed=seed,factor=f_range[f-1],acq=acq,max_iter=max_iter,save=True,
                            verbose=verbose,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f} backup",
                            do_moments=do_moments,do_stats=do_stats,loop=loop)
                    else:
                        self.VOI_filled_noNumba(seed=seed,factor=f_range[f-1],acq=acq,max_iter=max_iter,save=True,
                            verbose=verbose,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f} backup",
                            do_moments=do_moments,do_stats=do_stats)
                break
            if f > min_f_growth and growth>=0:
                if voxels[f]/voxels[f-1] > growth:
                    print(f"Saving the previous segmentation, for the growth factor is {(voxels[f]/voxels[f-1]):.2f}, which is over the allowed {growth}.\
                            \nThe index was {f-1}, which is >= to {min_f_growth}.")
                    if numba:
                        self.VOI_filled(seed=seed,factor=f_range[f-1],acq=acq,max_iter=max_iter,save=True,
                            verbose=verbose,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f} growth {(voxels[f]/voxels[f-1]):.2f}>{growth}",
                            do_moments=do_moments,do_stats=do_stats,loop=loop)   
                    else: 
                        self.VOI_filled_noNumba(seed=seed,factor=f_range[f-1],acq=acq,max_iter=max_iter,save=True,
                            verbose=verbose,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f} growth {(voxels[f]/voxels[f-1]):.2f}>{growth}",
                            do_moments=do_moments,do_stats=do_stats)   
                    break               
            if voxels[f]/image_size >= threshold:
                print(f"Stopping at iter {f+1}, because threshold of {threshold} has been reached with {voxels[f]/image_size:.3f}.")
                if counter_save == 0 and max_number_save > 0:
                    print(f"Saving a backup image, for nothing was satisfactory.")
                    if numba:
                        self.VOI_filled(seed=seed,factor=f_range[f-1],acq=acq,max_iter=max_iter,save=True,
                            verbose=verbose,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f} backup",
                            do_moments=do_moments,do_stats=do_stats,loop=loop)
                    else:
                        self.VOI_filled_noNumba(seed=seed,factor=f_range[f-1],acq=acq,max_iter=max_iter,save=True,
                            verbose=verbose,save_between=save_between,name=f"{name} VOI filled acq {acq} f {f_range[f]:.3f} backup",
                            do_moments=do_moments,do_stats=do_stats)
                break
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
        This function segments an image using a k-mean algorithm.\n
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
        mean = np.zeros(2)
        var = np.zeros(2)
        old_mean[0] = np.min(subimage)
        old_mean[1] = np.max(subimage)
        iter_now = 0
        
        while(iter_now < max_iter and (not (old_mean==mean).all())):
            VOI_0 = np.zeros_like(subimage)
            VOI_1 = np.zeros_like(subimage)
            if(iter_now != 0):
                old_mean = np.copy(mean)
            mid_value = (old_mean[0]+old_mean[1])/2
            iter_now += 1
            for i in range(subimage.shape[0]):
                for j in range(subimage.shape[1]):
                    for k in range(subimage.shape[2]):
                        if(subimage[i,j,k]<mid_value):
                            VOI_0[i,j,k] = 1
                        else:
                            VOI_1[i,j,k] = 1
            mean[0] = np.sum(np.multiply(VOI_0,subimage))/np.sum(VOI_0)
            mean[1] = np.sum(np.multiply(VOI_1,subimage))/np.sum(VOI_1)
            var[0] = np.sum(np.multiply(VOI_0,(subimage-mean[0])**2))/np.sum(VOI_0)
            var[1] = np.sum(np.multiply(VOI_1,(subimage-mean[1])**2))/np.sum(VOI_1)
            if verbose:
                print(f"Average of the groups for iter {iter_now}: {mean[0]:.1f} and {mean[1]:.1f}.")
                print(f"Variance of the groups for iter {iter_now}: {var[0]:.1f} and {var[1]:.1f}.")

        VOI = np.zeros_like(self.Image[int(acq),:,:,:])
        for i in range(subimage.shape[0]):
            for j in range(subimage.shape[1]):
                for k in range(subimage.shape[2]):
                    prob0 = np.exp(-(subimage[i,j,k]-mean[0])**2/(2*var[0]))/(2*3.141592*var[0])**(1/2)
                    prob1 = np.exp(-(subimage[i,j,k]-mean[1])**2/(2*var[1]))/(2*3.141592*var[1])**(1/2)
                    if(prob1>prob0):
                        VOI[i+subinfo[0][0],j+subinfo[1][0],k+subinfo[2][0]] = 1
        if save:
            self.save_VOI(VOI,name=name,do_stats=do_stats,do_moments=do_moments)
        if not save:
            return VOI, mean, var
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
                        E_0 = -np.log(np.exp(-(subimage[i,j,k]-mean[0])**2/(2*var[0]))/(2*3.141592*var[0])**(1/2)) + alpha* neighbour0
                        E_1 = -np.log(np.exp(-(subimage[i,j,k]-mean[1])**2/(2*var[1]))/(2*3.141592*var[1])**(1/2)) + alpha* neighbour1
                        #print(E_0,E_1)
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
                print(f"Iter {iter_now}, size of classes: {np.sum(new_VOI):.0f} and {(subinfo[0][1]-subinfo[0][0])*(subinfo[1][1]-subinfo[1][0])*(subinfo[2][1]-subinfo[2][0])-np.sum(new_VOI):.0f}, with total energy {E_tot}")
                print(f"Number of voxels changed: {counter}")
        for i in range(old_VOI.shape[0]):
            for j in range(old_VOI.shape[1]):
                for k in range(old_VOI.shape[2]):
                    VOI[i+subinfo[0][0],j+subinfo[1][0],k+subinfo[2][0]] = new_VOI[i,j,k]
        if save:
            self.save_VOI(VOI,name=name,do_stats=do_stats,do_moments=do_moments)
        if not save:
            return VOI, E_tot
        return E_tot
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
                print("No voxels in the image, center of mass not determined and set to (0,0,0)")
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
                #print("No voxels in the image, center of mass not determined and set to (0,0)")
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
            #print("No voxels in the image, moment of inertia not determined and set to (0,0,0)")
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
            print('Invalid combination of origin and target units, no change made')
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
    def model_three_compartment_A1(self,t:np.ndarray,param:np.ndarray): #Added in 3.0.0
        """Model of the first compartment in a two_compartment model.\n
        Form: A_1(t) = A_0 e^(-k_1/V_1 t)\n

        Keyword arguments:\n
        param -- list of parameters [A_0,k_1/V1]
        """
        return param[0]*(np.exp(-param[1]*t)-np.exp(-param[2]*t))
    def model_three_compartment_A2(self,t:np.ndarray,param:np.ndarray): #Added in 3.0.0
        """Model of the second compartment in a two_compartment model\n
        Form: A_2(t) = A_0 (k_1V_2/(k_1V_2-k_2V_1))[e^(-k_2/V_2 t)-e^(-k_1/V_1 t)]\n

        Keyword arguments:\n
        param -- list of parameters [A_0,k_1,k_2/V2]
        """
        return param[0]*(np.exp(-param[1]*t)-np.exp(-param[2]*t))
    def model_three_compartment_A2_pause(self,t:np.ndarray,param:np.ndarray): #Added in 3.0.0
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
            print(f"Error for a fitting, setting all to 0")
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
        param_init[:,0] *= 1e-5
        param_init[:,1] *= 1e4
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

        fig,axes = dyplot.traceplot(results, show_titles=True,trace_cmap='viridis', connect=True,connect_highlight=range(5),title_fmt=".4f")
        std_up = np.zeros(ndim)
        std_down = np.zeros(ndim)
        for i in range(ndim):
            param = axes[i,1].title.get_text()
            std_down[i] = float(param[param.find("-")+1:param.find("^")-1])
            std_up[i] = float(param[param.find("+")+1:param.rfind("}$")])
        if keep_im_open != True: plt.close()

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
                            verbose:bool = False,save:bool = True):
        """Takes an array of index for a curve and fit it using a given model and algorithm.

        Keyword arguments:\n
        key -- array of the curves to fit (default [-1])\n
        curves -- Type of curves to be fitted: average or errors (default average)\n
        method -- algorithmic method of Bayesian analysis; can take scipy.optimize.curve_fit or Dynesty (default Dynesty)
        Other possibilities will include EMCEE (To be added).\n
        model -- pharmacokinetic model to fit the data (default '2-compartment'). 
        Other possibilities will include 1-compartment, 2-comparment-with-reference (To be added).\n
        param -- array of the subcharacteristic of the curves to fit (default [])\n
        verbose -- print the progress of the process (default False)\n
        """
        if (not isinstance(key,(np.ndarray,list))):
            if key == -1 and curves == 'Average': key = np.arange(self.voi_counter);print("Selecting all TACs")
            elif key == -1 and curves == 'Errors': key = np.arange(len(self.voi_statistics_avg));print("Selecting all curves with errors")
            else:
                raise Exception("Key argument must be a list or np.array of indices for the curves to fit")
        key = np.array(key)
        if verbose: initial = time.time()
        for i in range(key.shape[0]):
            if verbose: print(f"Iter {i+1} of {key.shape[0]} after {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")
            value, error_up, error_down = self.Bayesian_analysis(key[i],curves=curves,method=method,model=model)
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

    def Bayesian_analysis(self,key:int=-1,curves:str = 'Average',method:str='Dynesty',model:str='2_Comp_A2'):
        """Takes an index for a curve and fit it using a given model and algorithm.

        Keyword arguments:\n
        key -- value of the curve to fit (default [-1])\n
        curves -- Type of curves to be fitted: average or errors (default average)\n
        method -- algorithmic method of Bayesian analysis; can take scipy.optimize.curve_fit or Dynesty (default Dynesty)
        Other possibilities will include EMCEE (To be added).\n
        model -- pharmacokinetic model to fit the data (default '2-compartment'). 
        Other possibilities will include 1-compartment, 2-comparment-with-reference (To be added).\n
        param -- array of the subcharacteristic of the curves to fit (default [])\n
        """
        if (not isinstance(key,int)):
            if key < 0 or key > self.voi_counter:
                raise Exception("Key argument must be integer, greater than 0, and smaller than the total number of segmentations")
        if curves == 'Average':
            y_data = self.voi_statistics[key]
            e_data = np.zeros(self.time)
        elif curves == 'Errors':
            y_data = self.voi_statistics_avg[key]
            e_data = self.voi_statistics_std[key]
        else:
            raise Exception("Invalid choice of curves to fit. Please see function definition for acceptable choices.")
        if model == '2_Comp_A1':
            model = self.model_three_compartment_A1
            ndim = 3 #Number of parameters of the model
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
            value, error_up, error_down = technique(y_data,e_data,model,ndim=ndim)
        except:
            print(f"Unable to run the parameter extraction on key {key} using method {method}, giving out 0s")
            value = np.zeros(ndim)
            error_up = np.zeros(ndim)
            error_down = np.zeros(ndim)
        return value,error_up, error_down
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
    def fill_2D(self,array,iter_max = 1000,method='taxicab'): #Done in 1.2.0
        neighbour_filling = True
        VOI_pre = 4*array
        center_mass = self.center_of_mass(VOI_pre,D=2).astype(int)
        VOI_pre[int(center_mass[0]),int(center_mass[1])] = -1
        VOI_post = array
        #Filling by going toward the center
        iter_now = 0
        while (iter_now < iter_max and not(VOI_pre==VOI_post).all()):
            VOI_post = VOI_pre
            for i in range(array.shape[0]):
                for j in range(array.shape[1]):
                    if VOI_pre[i,j] > 3.5:
                        #Find neighbor
                        neigh = self.neighbour_towards_center([i,j],center_mass,method)
                        #Set value to 5, except for the CM
                        if ((int(neigh[0])!=center_mass[0] or int(neigh[1])!=center_mass[1]) and VOI_pre[int(neigh[0]),int(neigh[1])]<0.5):
                            VOI_pre[int(neigh[0]),int(neigh[1])] = 5
                        #Lower value of the used pixel by 2 
                        #(initial 4 ->2)
                        #(filling 5 ->3)
                        VOI_pre[i,j] -= 2
            iter_now += 1
        VOI_post[int(center_mass[0]),int(center_mass[1])] = 4
        #Second part of filling, according to holes left
        iter_now = 0
        VOI_pre = VOI_post
        VOI_post = array
        if neighbour_filling:
            while (iter_now < iter_max and not(VOI_pre==VOI_post).all()):
                VOI_post = VOI_pre
                iter_now += 1
                for i in range(1,array.shape[0]-1):
                    for j in range(1,array.shape[1]-1):
                        if (VOI_pre[i,j] < 0.5 and VOI_pre[i+1,j]+VOI_pre[i-1,j]+VOI_pre[i,j+1]+VOI_pre[i,j-1]>5.5):
                            VOI_pre[i,j] = 2.9
        VOI_post = np.zeros_like(array)
        for i in range(array.shape[0]):
            for j in range(array.shape[1]):
                if VOI_pre[i,j] > 0.5:
                    VOI_post[i,j] = 1
        if (center_mass == [0,0]).all():
            VOI_post[0,0] = 0
        return VOI_post


    def fill_3D(self,array,method='taxicab'): #Done 1.2.0
        VOI_filled_3D = np.zeros((self.nb_slice,self.width,self.length))
        VOI_filled_0 = np.zeros((self.nb_slice,self.width,self.length))
        VOI_filled_1 = np.zeros((self.nb_slice,self.width,self.length))
        VOI_filled_2 = np.zeros((self.nb_slice,self.width,self.length))

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
                    if(VOI_filled_all[i,j,k]>2.5):
                        VOI_filled_3D[i,j,k] = 1
        return VOI_filled_3D

    def neighbour_towards_center(self,point,target,method = 'taxicab'): #Done in 1.2.0
        neighbour = np.zeros_like(point)
        if method == 'taxicab':
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
        d -- distance to stretch the axes
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
        if isinstance(order,(int)) and isinstance(d,(int)):
            if order == 1 or order == 2 or order == 3:
                return d*all_orders[order-1]
            else:
                raise Exception(f"Invalid value for the order.\nThe value given was {order} and must be 0, 1, or 2.")
        elif isinstance(order,(np.ndarray,list)):
            order = np.array(order) - 1 #To fit with the position of the array
            if isinstance(d,(int)):
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