import numpy as np
import os
import matplotlib.pyplot as plt
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.pickle_functions as PF
import MyFunctions.Extract_Images_r as Extract_r
import time
###
import numpy as np
import time
import matplotlib.pyplot as plt


os.system('clear')

initial = time.time()
Fan1 = PF.pickle_open(os.path.dirname(os.path.realpath(__file__))+'/Fantome_1_1min.pkl')
print('Opening took ',"{:.2f}".format(time.time()-initial),' s')

print('Testing kmean VOI')
now = time.time()
#3
#11
#39
maxi = 1

Fan1.VOI_kMean(subinfo = [[15,80],[104,112],[82,100]],acq=10,name='Poche Canny',do_moments=True,do_stats=True,verbose = True) 

alpha = np.array([0,0.01,0.1,1,10,100,1000,1e4,1e5,1e6,1e7,1e8,1e9,1e10])
E = np.zeros_like(alpha)
for k in range(alpha.shape[0]):
    print(f"Part done: {k} of {alpha.shape[0]}: {(k+1)/alpha.shape[0]*100}%. Time elpased: {time.time()-initial} s")
    E[k] = Fan1.VOI_ICM(subinfo = [[6,101],[118,128],[49,82]],alpha=alpha[k],max_iter=100,
                        acq=35,name='Poche Canny',do_moments=True,do_stats=True,verbose = True) 

print("Running the VOI took ","{:.2f}".format(time.time()-now),' s\nWith a total of ',Fan1.voi_counter,' VOIs, with ',Fan1.voi_voxels,' voxels')

for i in range(Fan1.voi_counter):
    Fan1.show_flats(key = i)

plt.figure()
plt.plot(E)

print('Program ran until the end in ',"{:.2f}".format(time.time()-initial),' s')
plt.show()