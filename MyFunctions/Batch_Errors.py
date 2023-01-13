import numpy as np
import time

from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.Pickle_Functions as PF

def Batch_Errors(Image:DicomImage = None,error_type:str = "None", k =-1,
                path_in:str='',name_in:str='',path_out:str = '',name_out:str='',saveResult:bool = False,
                verbose:bool=False,order:int=1,d:float=1,weight=1, angle:float = 0):
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
        k = np.array(k)

    if error_type == "Linear Shift":
        Linear_Shift_Errors_Batch(Image,k=k,order=order,d=d,weight=weight,verbose=verbose)
    if error_type == "Rotation":
        Rotation_Error_Batch(Image,k=k,order=order,angle = angle, verbose = verbose)

    if saveResult:
        PF.pickle_save(Image,path_out+name_in+name_out+'.pkl')
    print(f"All the errors were computed in {(time.time() - initial):.2f} s.")

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
    d -- distance of the shift (default 1)\n
    weight -- weight for each axis, if compounded [TBA] (default 1)\n
    verbose -- outputs the progress (default False)\n
    """
    Image.rotation_errors(keys = k, angle = angle, order = order, verbose = verbose)