import numpy as np
import os
import matplotlib.pyplot as plt
from MyFunctions.DicomImage import DicomImage #Custom Class
import time
###
import numpy as np
import time
import matplotlib.pyplot as plt
import MyFunctions.Batch_Segmentations as BS

os.system('clear')
print('Starting program...')
path_in ='/Volumes/Backup_Stuff/Python/Data/'
path_out ='/Volumes/Backup_Stuff/Python/Data_Results/'

name_in = np.array(['S025','S026','S027','S028','S029'])
name_out = np.array(['_C_k_all','_I_k_all','_F_k_all'])

initial = time.time()

seed = [[17,32,107,60],
        [17,75,100,54],
        [17,70,100,72],
        [17,54,108,80],
        [17,60,108,62]]
region = [[[1,65],[90,130],[41,85]],
            [[50,110],[75,130],[30,94]],
            [[37,104],[80,125],[50,92]],
            [[36,82],[92,120],[60,100]],
            [[40,88],[88,128],[40,92]]]
initial = time.time()
for i in range(name_in.shape[0]-1):
    print(f"Now doing rat {name_in[i]}")
    BS.Batch_Segmentations(segmentation_type='Canny',seed=seed[i],k=-1,subimage=region[i],
                            name_segmentation = 'Left Kidney',show_pre = False,threshold=0.5,
                            path_in = path_in,name_in=name_in[i],path_out=path_out+name_in[i]+'/',name_out=name_out[0])
    BS.Batch_Segmentations(segmentation_type='ICM',seed=seed[i],k=-1,subimage=region[i],
                            name_segmentation = 'Left Kidney',show_pre = False,threshold=0.5,
                            path_in = path_in,name_in=name_in[i],path_out=path_out+name_in[i]+'/',name_out=name_out[1])
    BS.Batch_Segmentations(segmentation_type='Filling',seed=seed[i],k=-1,subimage=region[i],
                            name_segmentation = 'Left Kidney',show_pre = False,threshold=0.5,growth = 2.5,min_f_growth=50,
                            path_in = path_in,name_in=name_in[i],path_out=path_out+name_in[i]+'/',name_out=name_out[2])
    print(f"Rats done: {(i+1)/name_in.shape[0]*100:.2f} % in {time.time()-initial:.1f} s")

print('Program ran until the end in ',"{:.1f}".format(time.time()-initial),' s')
plt.show()
