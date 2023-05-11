import numpy as np
import os
import matplotlib.pyplot as plt
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.pickle_functions as PF
import time

os.system('clear')
initial = time.time()
S036 = PF.pickle_open(os.path.dirname(os.path.realpath(__file__))+'/S036.pkl')
print('Opening took ',"{:.2f}".format(time.time()-initial),' s')
print("Name",S036.name,"\nVersion: ",S036.version,'\nNumber of VOI: ',S036.voi_counter,'\nMethods: ',S036.voi_methods,' in ',S036.time_scale)

print('Testing ellipsoid VOI')
now = time.time()
S036.add_VOI_ellipsoid(infos = np.array([[92,117,124],[10,10,10]]),name='Liver') #Les chiffres sont inversés par rapport à MatLab
print('Number of VOI: ',S036.voi_counter,' with ',S036.voi_voxels[0],' voxels')
print("Running the VOI took ","{:.2f}".format(time.time()-now),' s\nWith a total of ',S036.voi_counter,' VOIs')
print('Testing the average over the VOI')
now = time.time()
stats = S036.VOI_statistics(key=-1)
stats = S036.VOI_statistics(key=0)
figure1 = plt.figure(1)
plt.plot(S036.time,stats)
print("Running the curve took ","{:.2f}".format(time.time()-now),' s\nWith a total of ',S036.voi_counter,' VOIs with ',S036.voi_voxels[0],' voxels')
S036.remove_VOI(key=0)
print('Number of VOI: ',S036.voi_counter,' with ',S036.voi_voxels,' voxels')
print('Testing cuts')
now = time.time()
plt.figure(2)
plt.pcolormesh(S036.axial_flat(18))
plt.figure(3)
plt.pcolormesh(S036.sagittal_flat(18))
plt.figure(4)
plt.pcolormesh(S036.coronal_flat(18))
plt.colorbar()
print('Testing the slices took ',"{:.2f}".format(time.time()-now),' s')

print('Program ran until the end in ',"{:.2f}".format(time.time()-initial),' s')
plt.show()
