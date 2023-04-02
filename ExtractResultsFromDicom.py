from MyFunctions.DicomImage import DicomImage #Custom Class
from MyFunctions.DicomImage import CombinedResults #Custom Class
import MyFunctions.Pickle_Functions as PF

import matplotlib.pyplot as plt
import time
import numpy as np
import os

os.system("clear")
print(f"Starting program at {time.strftime('%H:%M:%S')}")
initial = time.time()
basePath = "/Volumes/Backup_Stuff/Results GUI/"

Fan = np.array(["FanDyn6","FanDyn7","FanDyn8","FanDyn9","FanDyn10"])
SegmSchemes = np.array(["Canny","Filling","ICM"])
Extension = "Errors_DicomImage.pkl"
Extension2 = "Bayesian_DicomImage.pkl"

AllResults = CombinedResults()

for i in range(len(Fan)):
    for j in range(len(SegmSchemes)):
        if j == 0:
            New = True
        else:
            New = False
        AllResults.addResult(basePath + Fan[i] + "/" + Fan[i] + "_" + SegmSchemes[j] + "_" + Extension, name= Fan[i], scheme= SegmSchemes[j], newAcq= New, dim = len(SegmSchemes))
        print(f"Part done: {i * len(SegmSchemes) + (j + 1)} of {len(SegmSchemes) * len(Fan)} in {(time.time()-initial):.2f} at {time.strftime('%H:%M:%S')}")

print(AllResults.VoiStatisticsTotal)

PF.pickle_save(AllResults,basePath + "AllResults_Errors.pkl")

print(f"Ending program after {(time.time()-initial):.2f} at {time.strftime('%H:%M:%S')}")
