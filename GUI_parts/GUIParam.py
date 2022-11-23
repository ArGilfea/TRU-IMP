from MyFunctions.DicomImage import DicomImage
import numpy as np

class GUIParameters(object):
    """
    Class that stores all the parameters used by the user for segmentations and subimages.\n
    This allows to store everything in a single instance, instead of having a gazillion variables in the main GUI.\n
    To instantiate this class, there needs to be an Image.
    Keyword arguments:\n
    Image -- DicomImage from the class\n
    """
    def __init__(self,Image:DicomImage):
        """Initialization of the class.\n
        Only requires the DicomImage, from which it takes the value, without keeping the full image and the segmentations"""
        self._size = np.array([Image.nb_acq,Image.nb_slice,Image.width,Image.length])
        self._nbSeg = Image.voi_counter
        self._nbError = Image.voi_statistics_counter
        self.seed = np.array([0,0,0])
        self.subImage = np.array([[0,Image.nb_acq],[0,Image.nb_slice],[0,Image.width],[0,Image.length]])
        self.SegmAcq = 0
        self.ErrorSegm = 0
        self.SaveSegm = True
        self.doCurves = True
        self.doStats = True
        self.doMoments = True
        self.doCoefficients = True
        self.verbose = True
        self.verbosePrecise = True
        self.SegmType = "None"
        self.ErrorType = "None"
        self.alphaICM = 1
        self.max_iter_ICM = 100
        self.max_iter_kmean_ICM = 100
        self.sigmaCanny = 1
        self.combinationCanny = 2
        self.methodCanny = "TaxiCab"
        self.steps_filling = 1000
        self.max_iter_fill = 300
        self.factor_Fill_range = [0.1,2.8]
        self.factor_fill_f = 1
        self.growth = -1
        self.min_f_growth = 0
        self.threshold_fill = 0.99
        self.verbose_graph_fill = False

        self.centerEllipsoid = np.array([2,2,2])
        self.axesEllipsoid = np.array([1,1,1])

        self.doThreshold = False
        self.threshold = 0.5

        self.orderShift = 1
        self.distanceShift = 1
        self.weightShift = 1

        self.BayesianAcq = -1
        self.BayesianType = "None"
        self.ModelBayesian = "2_Comp_A2"
        self.CurveTypeBayesian = "Average"
        self.Bayesian_thresh_perc = 0
        self.Bayesian_thresh_value = 0
        del Image