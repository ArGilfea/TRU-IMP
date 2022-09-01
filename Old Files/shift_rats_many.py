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

extension = np.array(['_C_k_all','_I_k_all','_F_k_all'])

path_out = '/Volumes/Backup_Stuff/Python/Data_Results/'
extension_out = np.array(['_C_k_all_shifted_1_2','_I_k_all_shifted_1_2','_F_k_all_shifted_1_2'])
initial = time.time()
rats = 5
types = 3

rats_name=np.array(['S025','S026','S027','S028','S029'])
types_name = np.array(['Gradient','Statistics','Filling','Gradient Threshold','Statistics Threshold','Filling Threshold'])

shifts_base = np.array([[1,0,0],[-1,0,0],
            [0,1,0],[0,-1,0],
            [0,0,1],[0,0,-1]])

shifts = np.concatenate((shifts_base,shifts_base*2))
shifts = shifts_base
print(shifts)

for i in range(rats):
    for j in range(types):
        LSM.Linear_Shifts_Many(shifts,k=-1,path_in=path_in+rats_name[i]+'/',name_in = rats_name[i]+extension[j],
            path_out = path_out+rats_name[i]+'/',name_out = rats_name[i]+extension_out[j],verbose = True)
        print(f"{i*types+j+1} out of {rats*types} done in {(time.time()-initial):.1f} s at {time.strftime('%H:%M:%S')}")


print('Program ran until the end in ',"{:.2f}".format(time.time()-initial),' s')
plt.show()