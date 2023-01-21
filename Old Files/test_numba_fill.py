import numpy as np
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import matplotlib.pyplot as plt
import time
###
import MyFunctions.Pickle_Functions as PF
####
###

os.system('clear')
print(f"Starting program at {time.strftime('%H:%M:%S')}")
initial = time.time()

Image = PF.pickle_open("/Users/philippelaporte/Desktop/Test/Fan9_Dyn_DicomImage.pkl")

subImage = [[10,70],[88,100],[90,112]]
seed = np.array([40,91,100])

Image.show_point(point = [10,40,91,100],star=True,sub_im=subImage)

now1 = time.time()
Image.VOI_filled_f(acq=20,seed=seed,sub_im=subImage,factor= [0.1,3],steps=100,numba=True,max_iter=300,verbose_graphs=True,verbose=False)
end1 = time.time()
print(f"Filled with Numba in {(end1-now1):.2f},' s at {time.strftime('%H:%M:%S')}")

now2 = time.time()
Image.VOI_filled_f(acq=20,seed=seed,sub_im=subImage,factor= [0.1,3],steps=100,numba=False,max_iter=300,verbose_graphs=True,verbose=False)
end2 = time.time()
print(f"Filled without Numba in {(end2-now2):.2f},' s at {time.strftime('%H:%M:%S')}")

Image.show_flats(key=0)
Image.show_flats(key=1)

print(f"Filled with Numba in {(end1-now1):.2f} s at {time.strftime('%H:%M:%S')}")
print(f"Filled without Numba in {(end2-now2):.2f} s at {time.strftime('%H:%M:%S')}")
print(f"Program ran until the end in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")
plt.show()