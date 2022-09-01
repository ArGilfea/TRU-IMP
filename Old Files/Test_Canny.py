import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.ndimage.measurements import label
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.pickle_functions as PF
import time
os.system('clear')
path_out='/Users/philippelaporte/Desktop/Programmation/Python'
initial = time.time()
print('Testing the program on S029')
S029 = PF.pickle_open(os.path.dirname(os.path.realpath(__file__))+'/S029.pkl')
print(S029.units)
now = time.time()
S029.add_VOI_ellipsoid(infos = np.array([[66,111,65],[26,16,17]]),name='Liver Ellipsoid',do_moments=True,do_stats=True) #Les chiffres sont inversés par rapport à MatLab
print("Running the ellipsoid VOI took ","{:.2f}".format(time.time()-now),' s\nWith a total of ',S029.voi_counter,' VOIs')

for t in range(18,21):#13
    now = time.time()
    S029.VOI_Canny_filled(subinfo=[[40,92],[95,128],[48,82]],acq = t,name = 'Kidney Canny Filled acq ' + f"{t}",sigma=2**(1/2),do_moments=True,do_stats=True)
    print("Running the Canny VOI took ","{:.2f}".format(time.time()-now),' s\nWith a total of ',S029.voi_counter,' VOIs')

figure = plt.figure(1)
for t in range(S029.voi_counter):
    plt.plot(S029.time,S029.voi_statistics[t][:]*S029.convert_units('SUVbw'),label=S029.voi_name[t])
plt.xlabel('t (min)');plt.ylabel('SUV'),plt.legend();plt.grid()
S029.show_flats(acq=18)
print('Program ran until the end in ',"{:.2f}".format(time.time()-initial),' s')
plt.show()

PF.pickle_save(S029, path_out+'/'+'S029_2'+'.pkl')
