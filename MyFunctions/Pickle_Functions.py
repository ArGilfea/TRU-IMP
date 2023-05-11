import pickle

from MyFunctions.DicomImage import DicomImage

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from dynesty import NestedSampler
from dynesty import plotting as dyplot
def pickle_save(obj:DicomImage, filename:str) -> None:
    """
    Saves a pickle file (format .pkl), with a given structure.\n
    N.B.: Updating an already existing pickle doesn't always work.\n
    Keyword arguments:\n
    obj -- object to save as a pickle file\n
    filename -- path where to save the file. Must include the name of the file itself.
    """
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def pickle_open(name:str) -> DicomImage:
    """
    Opens a pickle file given by the parameter name and return the structure opened.\n
    Keyword arguments:\n
    name -- string of the path to reach the .pkl file
    """
    with open(name, 'rb') as input:
        data = pickle.load(input)
    return data