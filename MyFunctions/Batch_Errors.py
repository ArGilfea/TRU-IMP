import numpy as np
import time

from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.Pickle_Functions as PF

def Batch_Errors(Image:DicomImage = None,error_type:str = "None", k =-1,
                path_in:str='',name_in:str='',path_out:str = '',name_out:str='',saveResult:bool = False,
                verbose:bool=False,order:int=1,d:float=1,weight=1, angle:float = 0,factor:float = 1,
                iterations: int = 50, verboseNotGUI = True):
    """
    Computes errors on segmentations of a DicomImage class, which is either given directly as a parameter or whose path is given.
    This will compute the errors on TACs from segmentations. 
    This can run many types of errors on many segmentations, making this function an easy tool for batch processing.\n
    Keyword arguments:\n
    Image -- DicomImage class used\n
    error_type -- method to compute the error (default "None")\n
    k -- segmentation for which to compute the errors. -1 for all (default -1)\n
    path_in -- path from where to get the image, as a DicomImage class (default '')\n    
    name_in -- name of the DicomImage opened (default '')\n
    path_out -- path to save the result, as long as save is True (default '')\n    
    name_out -- name of the new DicomImage saved (if save is set to True).
            That name will be appended to name_in (default '')\n
    saveResult -- Save the new DicomImage class as a pickle file (default False)\n
    order -- linear shift order (default 1)\n
    d -- distance of the shift (default 1)\n
    weight -- weight for each axis, if compounded [TBA] (default 1)\n
    angle -- angle of rotation for the rotation error in radians (default 0)\n
    factor -- factor of expansion for the expansion error (default 1)\n
    iterations -- number of iterations for the FCM error (default 50)\n
    verbose -- outputs the progress (default False)\n
    verboseNotGUI -- hides print statements when in the GUI (default True)\n
    """
    initial = time.time()
    global verboseNotGUIGlobal
    verboseNotGUIGlobal = verboseNotGUI
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
        Linear_Shift_Errors_Batch(Image,k=k,order=order,d=d,weight=weight,verbose=verboseNotGUI)
    if error_type == "Rotation":
        Rotation_Error_Batch(Image,k=k,order=order,angle = angle, verbose = verboseNotGUI)
    if error_type == "Expansion":
        Expansion_Error_Batch(Image,k=k,order=order,factor = factor, verbose = verboseNotGUI)
    if error_type == "Reflection":
        Reflection_Error_Batch(Image,k=k, verbose = verboseNotGUI)
    if error_type == "FCM":
        FCM_Error_Batch(Image,k=k,iteration = iterations,verbose = verboseNotGUI)
    if error_type == "RadioNuclide":
        RadioNuclide_Error_Batch(Image, k = k, verbose = verboseNotGUI)
    if saveResult:
        PF.pickle_save(Image,path_out+name_in+name_out+'.pkl')
    if verboseNotGUI: print(f"All the errors were computed in {(time.time() - initial):.2f} s.")

def Linear_Shift_Errors_Batch(Image:DicomImage,k:np.ndarray,order:int=1,d:float=1,weight=1,verbose:bool=True):
    """
    Compute the linear errors of the curves based upon the given parameters.\n
    Keyword arguments:\n
    Image -- DicomImage class used\n
    k -- segmentation for which to compute the errors. -1 for all (default -1)\n
    order -- linear shift order (default 1)\n
    d -- distance of the shift (default 1)\n
    weight -- weight for each axis, if compounded [TBA] (default 1)\n
    verbose -- outputs the progress (default False)\n
    """
    Image.linear_shifts_errors(keys=k,order=order,d=d,weight=weight,verbose=verbose)

def Rotation_Error_Batch(Image:DicomImage,k:np.ndarray,order:int=1,angle:float=0,verbose:bool=True):
    """
    Compute the rotation errors of the curves based upon the given parameters.\n
    Keyword arguments:\n
    Image -- DicomImage class used\n
    k -- segmentation for which to compute the errors. -1 for all (default -1)\n
    order -- linear shift order (default 1)\n
    angle -- angle of the rotation (default 0)\n
    weight -- weight for each axis, if compounded [TBA] (default 1)\n
    verbose -- outputs the progress (default False)\n
    """
    Image.rotation_errors(keys = k, angle = angle, order = order, verbose = verbose)

def Expansion_Error_Batch(Image:DicomImage,k:np.ndarray,order:int=1,factor:float=1,verbose:bool=True):
    """
    Compute the expansion errors of the curves based upon the given parameters.\n
    Keyword arguments:\n
    Image -- DicomImage class used\n
    k -- segmentation for which to compute the errors. -1 for all (default -1)\n
    order -- linear shift order (default 1)\n
    d -- factor of the expansion (default 1)\n
    weight -- weight for each axis, if compounded [TBA] (default 1)\n
    verbose -- outputs the progress (default False)\n
    """
    Image.expansion_errors(keys = k, factor = factor, order = order, verbose = verbose)

def Reflection_Error_Batch(Image:DicomImage,k:np.ndarray,verbose:bool=True):
    """
    Compute the reflection errors of the curves based upon the given parameters.\n
    Keyword arguments:\n
    Image -- DicomImage class used\n
    k -- segmentation for which to compute the errors. -1 for all (default -1)\n
    verbose -- outputs the progress (default False)\n
    """
    Image.reflection_errors(keys = k, verbose = verbose)

def FCM_Error_Batch(Image:DicomImage,k:np.ndarray,iteration:int = 50, verbose:bool = True):
    """
    Compute the FCM errors of the curves by sampling the FCM distributions.\n
    Keyword arguments:\n
    Image -- DicomImage class used\n
    k -- segmentation for which to compute the errors. -1 for all (default -1)\n
    iteration -- number of iteration for the sampling (default 50)\n
    verbose -- outputs the progress (default False)\n
    """
    initial = time.time()
    for i in range(k.shape[0]):
        Image.FCM_errors(key = k[i], iterations = iteration, verbose = verbose)
        if verboseNotGUIGlobal: print(f"Part done: {(i+1)/k.shape[0]*100:.2f} % in {(time.time() - initial):.1f} s at {time.strftime('%H:%M:%S')}")

def RadioNuclide_Error_Batch(Image:DicomImage,k:np.ndarray, verbose:bool = True):
    """
    Compute the RadioNuclide errors of the curves using the physical parameters of the acquisition.\n
    Keyword arguments:\n
    Image -- DicomImage class used\n
    k -- segmentation for which to compute the errors. -1 for all (default -1)\n
    verbose -- outputs the progress (default False)\n
    """
    initial = time.time()
    for i in range(k.shape[0]):
        Image.RadioNuclide_Errors(key = k[i], verbose = verbose)
        if verboseNotGUIGlobal: print(f"Part done: {(i+1)/k.shape[0]*100:.2f} % in {(time.time() - initial):.1f} s at {time.strftime('%H:%M:%S')}")

