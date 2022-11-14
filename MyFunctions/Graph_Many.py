import numpy as np
import matplotlib.pyplot as plt

def graph_all_specimens(all_rats,rats_name,rats,timeframes,begin=0,name1="",path_out='',name_out=''):
    """
    Test
    """
    each =timeframes.shape[0]
    fig, axs = plt.subplots(round(rats/2)+1,2)
    for i in range(rats):
        a = axs[int(i/2),(i+1)%2].pcolormesh(timeframes,timeframes,all_rats[i][begin:begin+each,begin:begin+each])
        axs[int(i/2),(i+1)%2].set_title(f"Rat {rats_name[i]}")
        axs[int(i/2),(i+1)%2].set_xlabel("Timeframe 1");axs[int(i/2),(i+1)%2].set_ylabel("Timeframe 2")
        axs[int(i/2),(i+1)%2].set_xticks(timeframes);axs[int(i/2),(i+1)%2].set_yticks(timeframes)
        fig.colorbar(a, ax=axs[int(i/2),(i+1)%2])
    fig.suptitle(f"{name1}")
    if path_out!='':
        plt.savefig(f"{path_out}{name_out}.pdf")

def graph_all_types(rat,name,types_name,timeframes,path_out='',name_out=''):
    """
    Test 2
    """
    each =timeframes.shape[0]
    types = types_name.shape[0]
    fig, axs = plt.subplots(round(types/2),2)
    for i in range(types):
        a = axs[int(i/2),(i+1)%2].pcolormesh(timeframes,timeframes,rat[i*each:(i+1)*each,i*each:(i+1)*each])
        axs[int(i/2),(i+1)%2].set_title(f"{types_name[i]} Segmentation")
        axs[int(i/2),(i+1)%2].set_xlabel("Timeframe 1");axs[int(i/2),(i+1)%2].set_ylabel("Timeframe 2")
        axs[int(i/2),(i+1)%2].set_xticks(timeframes);axs[int(i/2),(i+1)%2].set_yticks(timeframes)
        fig.colorbar(a, ax=axs[int(i/2),(i+1)%2])
    fig.suptitle(f"{name}")
    if path_out!='':
        plt.savefig(f"{path_out}{name_out}.pdf")