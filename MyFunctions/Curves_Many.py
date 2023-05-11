import os
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.Pickle_Functions as PF

Fan1 = PF.pickle_open(os.path.dirname(os.path.realpath(__file__))+'/Fantome_1_1min_Canny.pkl')
Fan5 = PF.pickle_open(os.path.dirname(os.path.realpath(__file__))+'/Fantome_5_1min_Canny.pkl')
Fan6 = PF.pickle_open(os.path.dirname(os.path.realpath(__file__))+'/Fantome_6_1min_Canny.pkl')
Fan7 = PF.pickle_open(os.path.dirname(os.path.realpath(__file__))+'/Fantome_7_1min_Canny.pkl')
Fan8 = PF.pickle_open(os.path.dirname(os.path.realpath(__file__))+'/Fantome_8_1min_Canny.pkl')

