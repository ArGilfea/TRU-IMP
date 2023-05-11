import numpy as np
import os
import matplotlib.pyplot as plt
import time
from MyFunctions.DicomImage import DicomImage
###
import MyFunctions.Batch_Segmentations as BS
import MyFunctions.Pickle_Functions as PF
import MyFunctions.Graph_Many as GM
####

os.system('clear')
print(f"Starting program at {time.strftime('%H:%M:%S')}")
initial = time.time()

path = "/Users/philippelaporte/Desktop/Test/FanDyn9_Errors_DicomImage.pkl"

Image = PF.pickle_open(path)

Image.show_flats(key=21)

Image.Bayesian_analyses(key=[21],curves = "Errors",method="Dynesty",
                                        model = "2_Comp_A2",
                                        thresh_perc=0.3,
                                        thresh_value=0.3,
                                        verbose = True,
                                        save=True,
                                        keep_im_open=True)

plt.close("all")

print(Image.bayesian_graphs_runplot[f"{0}"])
fig = Image.bayesian_graphs_runplot[f"{0}"]
fig2 = Image.bayesian_graphs_traceplot[f"{0}"]
dummy = plt.figure()
print(type(dummy))
new_manager = dummy.canvas.manager
new_manager.canvas.figure = fig
fig.set_canvas(new_manager.canvas)

fig.savefig("/Users/philippelaporte/Desktop/Test/Test1.png")
fig2.savefig("/Users/philippelaporte/Desktop/Test/Test2.png")

del dummy

print(type(fig2))
dummy2 = plt.figure(fig2.number)
print(f"Program ran until the end in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
plt.show()

