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
print(f"Starting to run...")
path ='/Volumes/Backup Stuff/Python'

Fan = PF.pickle_open(path+'/Fantome_7_1min.pkl')
#Fan1.VOI_filled(seed=[45,108,90],factor=1,acq=5,max_iter=100,verbose=True)

seed = [5,29,92,96]
Fan.show_point(seed,star=True)
Fan.show_curves(seed)

seed = [[29,92,96],[30,92,96]]
#Fan5 = [35,85,101]
#Fan6 = [25,98,103]
#Fan7 = [29,92,96]
#Fan8 = [31,95,102]

#for i in range(5):
    #Fan.VOI_filled_f(seed=seed,factor=[0.1,2.8],steps = 100,acq=3+i,max_iter=300,verbose=True,save_between=True)
Fan.VOI_filled_f(seed=seed,factor=[0.1,2.8],sub_im=[[10,48],[78,96],[85,108]],steps = 10,acq=3+0,max_iter=300,verbose=True,save_between=False,
                voxels_f=[1000,5500])

Fan.show_flats(acq=20)
Fan.show_flats(key=Fan.voi_counter-1)
for i in range(Fan.voi_counter):
    Fan.show_flats(key=i)
    pass

#PF.pickle_save(Fan,os.path.dirname(os.path.realpath(__file__))+'/Fantome_7_1min_Fill.pkl')

print('Program ran until the end in ',"{:.2f}".format(time.time()-initial),' s')
plt.show()