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
print(time.strftime('%H:%M:%S'))
path_in ='/Volumes/Backup_Stuff/Python/Data/'
path_out ='/Volumes/Backup_Stuff/Python/Data_Results/'

name_in = np.array(['Fantome_1_1min','Fantome_5_1min','Fantome_6_1min','Fantome_7_1min','Fantome_8_1min'])
name_region = np.array(['Compartment 1','Compartment 2','Compartment 3'])
name_out_comp = np.array(['_comp_1','_comp_2','_comp_3'])
name_out_type = np.array(['_C_k_all','_I_k_all','_F_k_all'])

initial = time.time()

seed = [[[2,52,93,118],[10,48,108,91],[25,69,120,74]],
        [[2,30,75,130],[10,30,88,99],[25,29,103,65]],
        [[2,26,86,130],[10,30,98,102],[25,29,113,75]],
        [[2,26,82,124],[10,30,93,94],[25,20,107,60]],
        [[2,31,82,130],[10,30,95,102],[25,30,107,68]]]
region = [[[[45,58],[89,102],[116,122]],[[15,80],[104,112],[82,100]],[[6,101],[118,128],[49,82]]],
            [[[23,36],[70,82],[125,135]],[[10,50],[83,92],[91,108]],[[4,55],[102,107],[55,87]]],
            [[[19,33],[80,95],[125,138]],[[10,43],[90,104],[94,111]],[[1,50],[108,118],[58,89]]],
            [[[16,35],[74,88],[118,130]],[[3,52],[85,100],[85,107]],[[1,43],[100,115],[45,82]]],
            [[[20,40],[74,88],[125,136]],[[5,55],[87,100],[91,112]],[[9,55],[100,116],[53,88]]]]
initial = time.time()
for i in range(3,name_in.shape[0]):
    print(f"Now doing phantom {name_in[i]}")
    for j in range(name_out_comp.shape[0]):
        print(f"Now doing compartment {name_out_comp[j]}")
        BS.Batch_Segmentations(segmentation_type='Canny',seed=seed[i][j],k=-1,subimage=region[i][j],
                            name_segmentation = name_region[j],show_pre = False,threshold=0.5,
                            path_in = path_in,name_in=name_in[i],path_out=path_out+name_in[i]+'/',name_out=name_out_comp[j]+name_out_type[0])
        BS.Batch_Segmentations(segmentation_type='ICM',seed=seed[i][j],k=-1,subimage=region[i][j],
                            name_segmentation = name_region[j],show_pre = False,threshold=0.5,
                            path_in = path_in,name_in=name_in[i],path_out=path_out+name_in[i]+'/',name_out=name_out_comp[j]+name_out_type[1])
        BS.Batch_Segmentations(segmentation_type='Filling',seed=seed[i][j],k=-1,subimage=region[i][j],
                            name_segmentation = name_region[j],show_pre = False,threshold=0.5,growth = 2.5,min_f_growth=50,
                            path_in = path_in,name_in=name_in[i],path_out=path_out+name_in[i]+'/',name_out=name_out_comp[j]+name_out_type[2])
        print(f"Compartments done: {j+1}/{name_out_comp.shape[0]} in {time.time()-initial:.1f} s at {time.strftime('%H:%M:%S')}")
    print(f"Rats done: {(i+1)/name_in.shape[0]*100:.2f} % in {time.time()-initial:.1f} s at {time.strftime('%H:%M:%S')}")

print('Program ran until the end in ',"{:.1f}".format(time.time()-initial),' s')
plt.show()
