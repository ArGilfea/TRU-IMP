import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.ndimage.measurements import label
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.pickle_functions as PF
import time
import dynesty
import math
from dynesty import NestedSampler
from dynesty import plotting as dyplot
###---------------------------------------------------###
###-----------------Functions-------------------------###
###---------------------------------------------------###
def model(time,param):
    """Description Allo"""
    output = np.zeros_like(time)
    t_int_1 = 2/3
    t_int_2 = 5/3
    V_1 = 17
    A_0 = param[0]
    k_1 = param[1]
    for t in range(len(output)):
        if time[t] < t_int_1:
            output[t] = A_0/t_int_1*time[t]
        elif time[t] < t_int_2:
            output[t] = np.max([output[t-1],0])
        else:
            output[t] = A_0*np.exp(-k_1/V_1*(time[t]-t_int_2))
    return output
def model_2(time,param):
    output = np.zeros_like(time)
    t_int_2 = 5/3
    V_1 = 17
    V_2 = 125
    A_0 = param[0]
    k_1 = param[1]
    k_2 = param[2]
    for t in range(len(output)):
        if time[t] >= t_int_2:
            output[t] = A_0*k_1*V_1/(k_1*V_2-k_2*V_1)*(np.exp(-k_2/V_2*(time[t]-t_int_2))-np.exp(-k_1/V_1*(time[t]-t_int_2)))
    return output    
def model_3(time,param):
    output = np.zeros_like(time)
    t_int_2 = 5/3
    V_1 = 17
    V_2 = 125
    A_0 = param[0]
    k_1 = param[1]
    k_2 = param[2]
    for t in range(len(output)):
        if time[t] >= t_int_2:
            output[t] = A_0/(k_1*V_2-k_2*V_1)*(k_2*V_1*np.exp(-k_1/V_1*(time[t]-t_int_2))-k_1*V_2*np.exp(-k_2/V_2*(time[t]-t_int_2)))+A_0
    return output 
def logprior(param,param_limit):
    lprior = np.zeros(param.shape[0])
    if param_limit[0,0]<param[0]<param_limit[0,1] and param_limit[1,0]<param[1]<param_limit[1,1]:
        lprior = np.log(1/(param[1]*np.log(param_limit[1,1]/param_limit[1,0])))#+1/(param[2])*np.log(param_limit[2,1]/param_limit[2,0])
    else:
        lprior = -np.inf
    return lprior
def prior_transform(param_unif_0_1,param_limit):
    param = np.ones_like(param_unif_0_1)
    param[0] = param_unif_0_1[0]*(param_limit[0,1]-param_limit[0,0])+param_limit[0,0]
    param[1] = param_unif_0_1[1]*(param_limit[1,1]-param_limit[1,0])+param_limit[1,0]
    return param
def prior_transform_2(param_unif_0_1,param_limit):
    param = np.ones_like(param_unif_0_1)
    param[0] = param_unif_0_1[0]*(param_limit[0,1]-param_limit[0,0])+param_limit[0,0]
    param[1] = param_unif_0_1[1]*(param_limit[1,1]-param_limit[1,0])+param_limit[1,0]
    param[2] = param_unif_0_1[2]*(param_limit[2,1]-param_limit[2,0])+param_limit[2,0]
    return param
def loglike(param,data_t,data_f,data_e):
    prob = 0
    #First compute the model the parameters
    m = np.zeros(len(data_t))
    #print(m.shape)
    m = model(data_t,param)
    #Now compute the probability of the model w.r.t. data
    for j in range(m.shape[0]): #This is a specific point for that model
        prob += np.log(2*np.pi*data_e[j])/2-((m[j]-data_f[j])/data_e[j])**2
    return prob
def loglike_2(param,data_t,data_f,data_e):
    prob = 0
    #First compute the model the parameters
    m = np.zeros(len(data_t))
    #print(m.shape)
    m = model_2(data_t,param)
    #Now compute the probability of the model w.r.t. data
    for j in range(m.shape[0]): #This is a specific point for that model
        prob += np.log(2*np.pi*data_e[j])/2-((m[j]-data_f[j])/data_e[j])**2
    return prob
def loglike_3(param,data_t,data_f,data_e):
    prob = 0
    #First compute the model the parameters
    m = np.zeros(3*len(data_t))
    #print(m.shape)
    m = np.append(np.append(model(data_t[:40],param),model_2(data_t[:40],param)),model_3(data_t[:40],param))
    #Now compute the probability of the model w.r.t. data
    for j in range(m.shape[0]): #This is a specific point for that model
        prob += np.log(2*np.pi*data_e[j])/2-((m[j]-data_f[j])/data_e[j])**2
    return prob
def loglike_4(param,data_t,data_f,data_e):
    prob = 0
    #First compute the model the parameters
    m = np.zeros(2*len(data_t))
    #print(m.shape)
    m = np.append(model(data_t[:40],param),model_2(data_t[:40],param))
    #Now compute the probability of the model w.r.t. data
    for j in range(m.shape[0]): #This is a specific point for that model
        prob += np.log(2*np.pi*data_e[j])/2-((m[j]-data_f[j])/data_e[j])**2
    return prob
os.system('clear')
initial = time.time()
Acq = PF.pickle_open(os.path.dirname(os.path.realpath(__file__))+'/Fantome_1_1min_2.pkl')
now = time.time()


t_0 = 5/3 #début écoulement d'eau
t=np.arange(t_0,np.max(Acq.time),0.1)
t_inj = 2/3 #fin injection
t_inj_all = np.arange(0,t_inj,0.01)
t_inter = np.arange(t_inj,t_0,0.001)
A_star_0 = 39.10 #MBq
k_1 = 26/50/10*60 #mL/s
k_2 = 26/50/10*60 #mL/s
V_1 = 17 #mL
V_2 = 125 #mL
weight = 0.142 #kg

t_demie = 109.8 #min
delta_t = 16 #min
A_star = A_star_0*np.exp(-np.log(2)*delta_t/t_demie)
print(f'True Values: \nA_star = {A_star}\nk_1 = {k_1}\nk_2 = {k_2}')

A_1_0 = A_star/(2/3)*t_inj_all
A_1_inter = np.max(A_1_0)*np.ones_like(t_inter)
A_2_0 = 0*t_inj_all
A_3_0 = 0*t_inj_all
A_2_inter = 0*t_inter
A_3_inter = 0*t_inter
A_1 = A_star * np.exp(-k_1/V_1*(t-t_0))
A_2 = A_star*k_1*V_2/(k_1*V_2-k_2*V_1)*(np.exp(-k_2/V_2*(t-t_0))-np.exp(-k_1/V_1*(t-t_0)))
A_3 = A_star/(k_1*V_2-k_2*V_1)*(k_2*V_1*np.exp(-k_1/V_1*(t-t_0))-k_1*V_2*np.exp(-k_2/V_2*(t-t_0)))+A_star
t_1=np.arange(0,np.max(Acq.time),0.01)

print('Dynesty starting...')
ndim1=2
ndim2=3
#The parameters are A_0,k_1,k_2
param_init_1 = np.array([[1,400],[0.001,10.0]])
param_init_2 = np.array([[1,40],[0.001,100.0],[0.001,100.0]])
data_e = np.ones_like(Acq.time)*1
labels = ["A_0", "k1"]
labels_2 = ["A_0", "k1","k2"]

Acq.voi_statistics[0][:]=Acq.voi_statistics[0][:]/1000;Acq.voi_statistics[0][0]=0
Acq.voi_statistics[1][:]=Acq.voi_statistics[1][:]/1000;Acq.voi_statistics[1][0]=0
Acq.voi_statistics[2][:]=Acq.voi_statistics[2][:]/1000;Acq.voi_statistics[2][0]=0
Acq.voi_statistics[3][:]=Acq.voi_statistics[3][:]/1000;Acq.voi_statistics[3][0]=0
Acq.voi_statistics[4][:]=Acq.voi_statistics[4][:]/1000;Acq.voi_statistics[4][0]=0
All_values = np.append(np.append(Acq.voi_statistics[2][:],Acq.voi_statistics[3][:]),Acq.voi_statistics[4][:])
time2 = np.append(np.append(Acq.time,Acq.time),Acq.time)
data_e_2 = np.append(np.append(data_e,data_e),data_e)*1

#samplerDynesty1 = NestedSampler(loglike,prior_transform,ndim1,logl_args=[Acq.time,Acq.voi_statistics[2][:],data_e],ptform_args=[param_init_1])
#samplerDynesty2 = NestedSampler(loglike_2,prior_transform_2,ndim2,logl_args=[Acq.time,Acq.voi_statistics[3][:],data_e],ptform_args=[param_init_2])
samplerDynesty3 = NestedSampler(loglike_3,prior_transform_2,ndim2,logl_args=[time2,All_values,data_e_2],ptform_args=[param_init_2])
samplerDynesty4 = NestedSampler(loglike_4,prior_transform_2,ndim2,logl_args=[np.append(Acq.time,Acq.time),np.append(Acq.voi_statistics[2][:],Acq.voi_statistics[3][:]),np.append(data_e,data_e)*1],ptform_args=[param_init_2])
#samplerDynesty1.run_nested(maxiter=20000)
#samplerDynesty2.run_nested(maxiter=20000)
samplerDynesty3.run_nested(maxiter=30000)
samplerDynesty4.run_nested(maxiter=30000)
#results = samplerDynesty1.results
#results_2 = samplerDynesty2.results
results_3 = samplerDynesty3.results
results_4 = samplerDynesty4.results
lnz_truth = ndim1 * -np.log(2 * 10.)  # analytic evidence solution
#figu, axes = dyplot.runplot(results, lnz_truth=lnz_truth)  # summary (run) plot
#fig, axes = dyplot.traceplot(results, show_titles=True,trace_cmap='viridis', connect=True,connect_highlight=range(5),labels=labels)
#fig, axes = dyplot.traceplot(results_2, show_titles=True,trace_cmap='viridis', connect=True,connect_highlight=range(5),labels=labels_2)
#fig, axes = dyplot.traceplot(results_3, show_titles=True,trace_cmap='viridis', connect=True,connect_highlight=range(5),labels=labels_2)
#fig, axes = dyplot.traceplot(results_4, show_titles=True,trace_cmap='viridis', connect=True,connect_highlight=range(5),labels=labels_2)
#fg, ax = dyplot.cornerplot(results, color='dodgerblue', show_titles=True,quantiles=None, max_n_ticks=3,labels=labels,title_fmt=".4f")
#fg, ax = dyplot.cornerplot(results_2, color='dodgerblue', show_titles=True,quantiles=None, max_n_ticks=3,labels=labels_2,title_fmt=".4f")
fg, ax = dyplot.cornerplot(results_3, color='dodgerblue', show_titles=True,quantiles=None, max_n_ticks=3,labels=labels_2,title_fmt=".4f")
fg, ax = dyplot.cornerplot(results_4, color='dodgerblue', show_titles=True,quantiles=None, max_n_ticks=3,labels=labels_2,title_fmt=".4f")
##optimal_Dynesty = results.samples[-1,:]
#optimal_Dynesty_2 = results_2.samples[-1,:]
optimal_Dynesty_3 = results_3.samples[-1,:]
optimal_Dynesty_4 = results_4.samples[-1,:]
print(f"Dynesty Results 3: {optimal_Dynesty_3}")
print(f"Dynesty Results 4: {optimal_Dynesty_4}")
#best_fit_Dynesty = model(Acq.time,optimal_Dynesty)
#best_fit_Dynesty_2 = model_2(Acq.time,optimal_Dynesty_2)
#best_fit_Dynesty_3 = model(t_1,optimal_Dynesty_3)
#best_fit_Dynesty_4 = model_2(t_1,optimal_Dynesty_3)
#best_fit_Dynesty_5 = model_3(t_1,optimal_Dynesty_3)
best_fit_Dynesty_6 = model(t_1,optimal_Dynesty_4)
best_fit_Dynesty_7 = model_2(t_1,optimal_Dynesty_4)
plt.figure(7)
for i in range(2,Acq.voi_counter):
    plt.plot(Acq.time,Acq.voi_statistics[i][:],label=Acq.voi_name[i])
#plt.plot(Acq.time,best_fit_Dynesty,label='Dynesty best fit separate',linewidth=1)
#plt.plot(Acq.time,best_fit_Dynesty_2,label='Dynesty best fit separate',linewidth=1)
plt.plot(t_1,best_fit_Dynesty_6,label='Dynesty best fit Vial',linewidth=1)
plt.plot(t_1,best_fit_Dynesty_7,label='Dynesty best fit Comp 1',linewidth=1)
#plt.plot(t_1,best_fit_Dynesty_5,label='Dynesty best fit Comp 2',linewidth=1)
plt.plot(t,A_1,'b',label='Vial Theorique');plt.plot(t_inj_all,A_1_0,'b');plt.plot(t_inter,A_1_inter,'b')
plt.plot(t,A_2,'r',label='Comp 1 Theorique');plt.plot(t_inj_all,A_2_0,'r');plt.plot(t_inter,A_2_inter,'r')
plt.plot(t,A_3,'m',label='Comp 2 Theorique');plt.plot(t_inj_all,A_3_0,'m');plt.plot(t_inter,A_3_inter,'m')
#plt.plot(t,A_1,'b',label='Vial');plt.plot(t_inj_all,A_1_0,'b');plt.plot(t_inter,A_1_inter,'b')
#plt.plot(t,A_2,'r',label='Comp 1');plt.plot(t_inj_all,A_2_0,'r');plt.plot(t_inter,A_2_inter,'r')
#plt.plot(t,A_3,'m',label='Comp 2');plt.plot(t_inj_all,A_3_0,'m');plt.plot(t_inter,A_3_inter,'m')
plt.xlabel('t (min)');plt.ylabel('MBq'),plt.legend();plt.grid()


print('Program ran until the end in ',"{:.2f}".format(time.time()-initial),' s')
plt.show()
