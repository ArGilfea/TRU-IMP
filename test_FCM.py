import numpy as np
import os
import matplotlib.pyplot as plt
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.Pickle_Functions as PF
import time
###
import numpy as np
import time
import matplotlib.pyplot as plt

os.system('clear')
print('Starting program...')
path ='/Users/philippelaporte/Desktop/Test/'
Fantome = 'FanDyn9_DicomImage'
ext = '.pkl'

initial = time.time()
Fan = PF.pickle_open(path+Fantome+ext)

Fan.voi_fuzzy = {}
Fan.energies = {}
Fan.mus = {}

classNumber = 2

alphas = np.array([1.5,2,3])
#alphas = np.array([2])
m = np.array([2])
 
#Fan.VOI_ICM(acq = 20, subinfo = np.array([[10,70],[88,100],[90,112]]))

for i in range(alphas.shape[0]):
    for j in range(m.shape[0]):
        Fan.VOI_FCM(acq=20, subinfo = np.array([[10,70],[88,100],[90,112]]), 
                                                m = m[j], alpha = alphas[i],
                                                convergenceStep = 1e-5,
                                                maxIter= 100, maxIterConvergence=1000,
                                                classNumber = classNumber,
                                                save=True)

for i in range(Fan.voi_counter):
    Fan.FCM_errors(key = i, iterations = 50, verbose = True)
    Fan.FCM_errors(key = i, iterations = 5, verbose = True)

plt.figure()
for i in range(Fan.voi_counter):
    plt.plot(Fan.energies[f"{i}"],label = Fan.voi_name[i])
plt.grid()
plt.legend()
plt.yscale("log")
plt.title("Energy")

plt.figure()
for i in range(Fan.voi_counter):
    for j in range(classNumber):
        plt.plot(Fan.mus[f"{i}"][j,:,0],label = Fan.voi_name[i])
plt.grid()
plt.legend()
plt.title("Mus")

plt.figure()
for i in range(Fan.voi_counter):
    for j in range(classNumber):
        plt.plot(Fan.mus[f"{i}"][j,:,-1],label = Fan.voi_name[i])
plt.grid()
plt.legend()
plt.title("Mus")

for i in range(Fan.voi_counter):
    Fan.show_flats(key = i)

plt.figure()
for i in range(Fan.voi_counter):
    plt.plot(Fan.time,Fan.voi_statistics[i],label = Fan.voi_name[i])
    plt.errorbar(Fan.time,Fan.voi_statistics_avg[2*i],Fan.voi_statistics_std[i],label = Fan.voi_name[i] + " 50")
    plt.errorbar(Fan.time,Fan.voi_statistics_avg[2*i + 1],Fan.voi_statistics_std[i],label = Fan.voi_name[i] + " 5")
plt.grid()
plt.legend()
plt.title("TACs")

print(f"Ending program after {(time.time()-initial):.2f}s at {time.strftime('%H:%M:%S')}")
plt.show()