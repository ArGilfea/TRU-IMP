import os
import numpy as np
import matplotlib.pyplot as plt
import pydicom #To read Dicom Files
import time #To monitor time to run program
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.Pickle_Functions as PF

def Linear_Shifts_Many(linear_shifts,k=-1, 
                            name_segmentation = '',path_in='',name_in='',path_out = '',name_out='',save=True,
                            verbose = False):
    '''
    Keyword arguments:\n
    linear_shifts -- array consisting of the shifts of interest. Each line will be an independent linear shift which will be applied to each segmentations k.\n
    k -- segmentation keys on which to do the translations (must be an array or -1 for all timeframes) (default -1)\n
    name_segmentation -- used to name all the segmentations saved (default '')\n
    path_in -- path from where to get the image, as a DicomImage class (default '')\n    
    name_in -- name of the DicomImage opened (default '')\n
    path_out -- path to save the result, as long as save is True (default '')\n    
    name_out -- name of the new DicomImage saved (if save is set to True).
            That name will be appended to name_in (default '')\n
    save -- save the final result as a new instance of a DicomImage class (default True)\n
    verbose -- prints running information of the program (default False)\n
    '''
    linear_shifts = np.array(linear_shifts)
    initial = time.time()
    Image = PF.pickle_open(path_in+name_in+'.pkl')
    if verbose:
        print(f"Opened the file in {(time.time()-initial):.1f}")
    if k == -1:
        k = np.arange(Image.voi_counter)
    else:
        k = np.array(k)

    for i in range(k.shape[0]):
        for j in range(linear_shifts.shape[0]):
            Image.linear_shift(shifts = linear_shifts[j,:],counter = k[i],name=name_segmentation)
            if verbose:
                print(f"Part done: {(i*linear_shifts.shape[0]+j+1)/(k.shape[0]*linear_shifts.shape[0])*100:.1f} % in {(time.time()-initial):.1f} s")
    if save:
        PF.pickle_save(Image,path_out+name_out+'.pkl')