import MyFunctions.Pickle_Functions as PF

import matplotlib.pyplot as plt
import time
import numpy as np
import os

os.system("clear")
print(f"Starting program at {time.strftime('%H:%M:%S')}")
initial = time.time()
basePath = "/Users/philippelaporte/Desktop/Test/AllResults_"

Fan = np.array(["FanDyn6","FanDyn7","FanDyn8","FanDyn9","FanDyn10"])
FanNbr = Fan.shape[0]
SegmSchemes = np.array(["Canny","Filling","ICM"])
SegmSchemesCat = np.array(["Gradient","Filling","Statistics"])
SegmSchemesNbr = SegmSchemes.shape[0]
ParamList = np.array(["A_0","k_0","k_1"])
ParamListNbr = ParamList.shape[0]
color = ["r","b","g"]
Extension = "Errors.pkl"
Extension2 = "Bayesian.pkl"

AllResultsE = PF.pickle_open(basePath + Extension)
AllResultsB = PF.pickle_open(basePath + Extension2)

SegmStart = np.array([
    [7,5,6],
    [1,1,1],
    [3,2,5],
    [3,3,3],
    [5,4,5]
])
timeAxis = np.arange(0,40) + 0.5

figE, axE = plt.subplots(FanNbr,SegmSchemesNbr,sharex = True,sharey = False,tight_layout= True)
for i in range(FanNbr):
    maxTmp = 0
    maxTmp2 = 0
    for j in range(SegmSchemesNbr):
        for k in range(len(AllResultsB.VoiStatisticsStdTotal[Fan[i]][SegmSchemes[j]])):
            maxTmp2 = np.max(AllResultsB.VoiStatisticsAvgTotal[Fan[i]][SegmSchemes[j]][k])
            maxTmp = np.max([maxTmp,maxTmp2])
    for j in range(SegmSchemesNbr):
        for k in range(len(AllResultsB.VoiStatisticsStdTotal[Fan[i]][SegmSchemes[j]])):
            axE[i,j].errorbar(x = timeAxis + 0.02 * k,
                              y = AllResultsB.VoiStatisticsAvgTotal[Fan[i]][SegmSchemes[j]][k]/maxTmp,
                              yerr = AllResultsB.VoiStatisticsStdTotal[Fan[i]][SegmSchemes[j]][k]/maxTmp)
        axE[i,j].grid()
        if i == 0:
            axE[i,j].set_title(SegmSchemesCat[j])
        if j == 0:
            axE[i,j].set_ylabel(Fan[i])
figE.supxlabel("Time (min)")
figE.supylabel("Normalized Activity")
figE.suptitle("Time-Activity Curves")
figE.align_ylabels(axE[:, 0])
figE.set_size_inches(11.69,8.27)

figD, axD = plt.subplots(FanNbr,SegmSchemesNbr,sharex = False,sharey = False)
"""for i in range(FanNbr):
    for j in range(SegmSchemesNbr):
        axD[i,j].colormesh(AllResultsE[Fan[i]][SegmSchemes[j]])
        if i == 0:
            axD[i,j].set_title(SegmSchemesCat[j]) 
        if j == 0:
            axD[i,j].set_ylabel(Fan[i])       
figD.supxlabel("Segmentation 1")
figD.supylabel("Segmentation 2")
figD.suptitle("Sørensen-Dice Coefficients")
figD.set_size_inches(11.69,8.27)
"""

figJ, axJ = plt.subplots(FanNbr,SegmSchemesNbr,sharex = False,sharey = False)

figB, axB = plt.subplots(FanNbr,ParamListNbr,sharex = True,sharey = False,tight_layout= True)
for i in range(FanNbr):
    for j in range(ParamListNbr):
        if j == 0:
            axB[i,j].set_ylabel(Fan[i])
        for k in range(SegmSchemesNbr):
            axB[i,j].errorbar(x = np.arange(AllResultsB.BayesianStdTotal[Fan[i]][SegmSchemes[k]][:,j].shape[0])+0.2*k + SegmStart[i,j],
                              y = AllResultsB.BayesianStdTotal[Fan[i]][SegmSchemes[k]][:,j],
                              yerr = [AllResultsB.BayesianEUpTotal[Fan[i]][SegmSchemes[k]][:,j],AllResultsB.BayesianEDownTotal[Fan[i]][SegmSchemes[k]][:,j]],
                              color = color[k],
                              marker = 'o', markersize = 2,
                              linestyle = 'None')  
        if i == FanNbr - 1:
            axB[i,j].set_xlabel("Segm.")
        if i == 0:
            axB[i,j].set_title(ParamList[j])
        axB[i,j].grid()
figB.suptitle("Pharmacokinetic Parameters")
figB.align_ylabels(axB[:, 0])
figB.set_size_inches(11.69,8.27)

figE.savefig(basePath+"Errors.png")
figD.savefig(basePath+"Dice.png")
figJ.savefig(basePath+"Jaccard.png")
figB.savefig(basePath+"Bayesian.png")

print(f"Ending program after {(time.time()-initial):.2f} at {time.strftime('%H:%M:%S')}")
plt.show()