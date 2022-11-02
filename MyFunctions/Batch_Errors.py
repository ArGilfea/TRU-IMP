from distutils.log import error
import os
from unicodedata import name
import numpy as np
import matplotlib.pyplot as plt
import pydicom #To read Dicom Files
import time

from torch import threshold #To monitor time to run program
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.Pickle_Functions as PF

def Batch_Errors(Image:DicomImage = None,error_type:str = "None", k =-1,
                path_in='',name_in='',path_out = '',name_out='',saveResult:bool = False,
                verbose:bool=False,order=1,d=1,weight=1):
    """
    TBA
    """
    initial = time.time()
    try: 
        a = Image.version
        del a
    except:
        if path_in == '':
            raise Exception("path_in must be specified.\\It is recommended that the path be absolute")
        if name_in == '':
            raise Exception("path_in must be specified.\\It is recommended that the path be absolute")
        if name_out == '':
            raise Exception("path_in must be specified.\\It is recommended that the path be absolute")
        if path_out == '':
            path_out = path_in
        Image = PF.pickle_open(path_in+name_in+'.pkl')
    if k == -1:
        k = np.arange(Image.voi_counter)
    else:
        k = np.array(k)

    if error_type == "Linear Shift":
        Linear_Shift_Errors_Batch(Image,k=k,order=order,d=d,weight=weight,verbose=verbose)

    if saveResult:
        PF.pickle_save(Image,path_out+name_in+name_out+'.pkl')
    print(f"All the errors were computed in {(time.time() - initial):.2f} s.")

def Linear_Shift_Errors_Batch(Image:DicomImage,k:np.ndarray,order=1,d=1,weight=1,verbose:bool=True):
    Image.linear_shifts_errors(keys=k,order=order,d=d,weight=weight,verbose=verbose)