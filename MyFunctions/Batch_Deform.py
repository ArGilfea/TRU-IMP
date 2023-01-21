import numpy as np
import time

from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.Pickle_Functions as PF

def Batch_Deform(Image:DicomImage = None,deform_type:str = "None", k:int =-1,
                path_in:str='',name_in:str='',path_out:str = '',name_out:str='',saveResult:bool = False,
                linear_d: np.ndarray = np.array([0,0,0]), rotate_angle: np.ndarray = np.array([0,0,0]),
                factors_exp: np.ndarray = np.array([1,1,1]),
                verbose:bool=False):
    """
    Makes many deformations of given segmentations for a DicomImage, either loaded directly as a parameter or whose path is given.\n
    Keyword arguments:\n
    Image -- DicomImage class used (default None)\n
    deform_type -- method of deformation to apply (default "None")\n
    k -- segmentation for which to compute the deformations. Must be either an integer. -1 for all (default -1)\n
    path_in -- path from where to get the image, as a DicomImage class (default '')\n    
    name_in -- name of the DicomImage opened (default '')\n
    path_out -- path to save the result, as long as save is True (default '')\n    
    name_out -- name of the new DicomImage saved (if save is set to True).
            That name will be appended to name_in (default '')\n
    saveResult -- Save the new DicomImage class as a pickle file (default False)\n
    linear_d -- linear shift distance (default [0,0,0])\n
    rotate_angle -- angle for the rotations, in degrees (default [0,0,0])\n
    factors_exp -- factor for the expansions (default [1,1,1])\n
    verbose -- outputs the progress (default False)\n
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
        k = np.array([k])
    if deform_type == "Linear Shift":
        Linear_Shift_Batch(Image = Image,k=k,d=linear_d,verbose=verbose)
    if deform_type == "Rotation":
        Rotation_Batch(Image = Image, k = k, angle = rotate_angle, verbose = verbose)
    if deform_type == "Expansion":
        Expansion_Batch(Image = Image, k = k, factors= factors_exp, verbose= verbose)
    
    if saveResult:
        PF.pickle_save(Image,path_out+name_in+name_out+'.pkl')
    print(f"All the deformations were made in {(time.time() - initial):.2f} s.")

def Linear_Shift_Batch(Image:DicomImage,k:np.ndarray,d=[0,0,0],verbose:bool=True):
    """
    Compute the linear errors of the curves based upon the given parameters.\n
    Keyword arguments:\n
    Image -- DicomImage class used\n
    k -- segmentation for which to compute the errors\n
    d -- distance of the shift (default [0,0,0])\n
    verbose -- outputs the progress (default True)\n
    """
    initial = time.time()
    for i in range(k.shape[0]):
        Image.linear_shift(shifts = d,counter = k[i], save = True)
        if verbose:
            Image.update_log(f"Linear deformation {i + 1} of {k.shape[0]} done in {(time.time() - initial):.2f} s. at {time.strftime('%H:%M:%S')}")

def Rotation_Batch(Image:DicomImage,k:np.ndarray,angle:np.ndarray = np.array([0,0,0]),verbose:bool=True):
    """
    Compute the linear errors of the curves based upon the given parameters.\n
    Keyword arguments:\n
    Image -- DicomImage class used\n
    k -- segmentation for which to compute the errors\n
    angle -- angle of the rotation (default [0,0,0])\n
    verbose -- outputs the progress (default True)\n
    """
    initial = time.time()
    for i in range(k.shape[0]):
        Image.rotation_VOI(angles= angle, counter = k[i], save = True)
        if verbose:
            Image.update_log(f"Rotation deformation {i + 1} of {k.shape[0]} done in {(time.time() - initial):.2f} s. at {time.strftime('%H:%M:%S')}")

def Expansion_Batch(Image:DicomImage,k:np.ndarray,factors:np.ndarray = np.array([1,1,1]),verbose:bool=True):
    """
    Compute the linear errors of the curves based upon the given parameters.\n
    Keyword arguments:\n
    Image -- DicomImage class used\n
    k -- segmentation for which to compute the errors\n
    factors -- factor for the deformation (default [0,0,0])\n
    verbose -- outputs the progress (default True)\n
    """
    initial = time.time()
    for i in range(k.shape[0]):
        Image.expand_VOI(factors= factors, counter = k[i], save = True)
        if verbose:
            Image.update_log(f"Expansion deformation {i + 1} of {k.shape[0]} done in {(time.time() - initial):.2f} s. at {time.strftime('%H:%M:%S')}")
