import numpy as np
import os
import matplotlib.pyplot as plt
import time
###
import matplotlib.pyplot as plt
import MyFunctions.Batch_Segmentations as BS
import MyFunctions.Pickle_Functions as PF
import MyFunctions.Graph_Many as GM
from MyFunctions.DicomImage import DicomImage #Custom Class
####
os.system('clear')
print(f"Starting program at {time.strftime('%H:%M:%S')}")
initial = time.time()

path ='/Volumes/Backup_Stuff/Python/Data_Results/'
name_phantom=np.array(['Fantome_1_1min','Fantome_5_1min','Fantome_6_1min','Fantome_7_1min','Fantome_8_1min'])
name_type = np.array(['_C_k_all','_I_k_all','_F_k_all'])
name_comp = np.array(['_comp_1','_comp_2','_comp_3'])
name_rat = np.array(['S025','S026','S027','S028','S029'])

full_name_phantom = name_phantom[4]+name_comp[2]+name_type[2]+'.pkl'
full_name_rat = name_rat[4]+name_type[0]+'.pkl'
full_path_rat = path+name_rat[4]+'/'+full_name_rat
full_path_phantom = path+name_phantom[4]+'/'+full_name_phantom
full_path = full_path_rat

print(full_path)
Image = PF.pickle_open(full_path)
Image.show_flats(key=-1)
print(f"Program ran until the end in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")


plt.show()