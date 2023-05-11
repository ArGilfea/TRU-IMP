import numpy as np
import os
import matplotlib.pyplot as plt

import MyFunctions.Pickle_Functions as PF
import MyFunctions.Graph_Many as GM
import MyFunctions.Linear_Shifts_Many as LSM
import time
###
import numpy as np
import time
import matplotlib.pyplot as plt

os.system('clear')
print('Starting program...')
path_in ='/Volumes/Backup_Stuff/Python/Data_Results/'

extension_1 = np.array(['_C_k_all','_I_k_all','_F_k_all'])
extension_2 = np.array(['_comp_1','_comp_2','_comp_3'])

path_out = '/Volumes/Backup_Stuff/Python/Data_Results/'
extension_out = np.array(['_C_k_all_shifted_1_2','_I_k_all_shifted_1_2','_F_k_all_shifted_1_2'])
initial = time.time()
phantoms = 5
types = 3
comp = 3

name_in=np.array(['Fantome_1_1min','Fantome_5_1min','Fantome_6_1min','Fantome_7_1min','Fantome_8_1min'])
types_name = np.array(['Gradient','Statistics','Filling','Gradient Threshold','Statistics Threshold','Filling Threshold'])

shifts_base = np.array([[1,0,0],[-1,0,0],
            [0,1,0],[0,-1,0],
            [0,0,1],[0,0,-1]])

shifts = np.concatenate((shifts_base,shifts_base*2))
shifts = shifts_base
print(shifts)

for i in range(phantoms):
    for j in range(types):
        for k in range(comp):
            LSM.Linear_Shifts_Many(shifts,k=-1,path_in=path_in+name_in[i]+'/',name_in = name_in[i]+extension_2[k]+extension_1[j],
                path_out = path_out+name_in[i]+'/',name_out = name_in[i]+extension_2[k]+extension_out[j],verbose = True)
            print(f"\n\n\n{i*types*comp+j*types+k+1} out of {phantoms*types*comp} done in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}\n\n\n")


print('Program ran until the end in ',"{:.2f}".format(time.time()-initial),' s')
plt.show()