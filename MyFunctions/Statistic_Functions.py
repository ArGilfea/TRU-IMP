import numpy as np
import math
try:
    from scipy.integrate import trapezoid
except:
    from scipy.integrate import trapz as trapezoid
from functools import partial

def rayleigh_noise_pdf(value:float = 0,a:float = 0.0,b:float = 1.0,type:str = "icdf") -> float:
    """
    Probability Density Function (pdf), Cumulative Density Function (cdf) and inverse cdf for the 
    Rayleigh noise.\n
    Keyword arguments:\n
    value -- values for which to compute the function\n
    a -- first parameter for the Rayleigh noise distribution, its lowest value (default 0)\n
    b -- second parameter for the Rayleigh noise distribution, its spread (default 0)\n 
    type -- type of function to use: pdf, cdf or icdf (default "icdf")         
    """
    if type == "pdf":
        return np.where(value >= a, (2/b)*(value - a) * np.exp(-(value-a)**2/b), 0)
    elif type == "cdf":
        return np.where(value >= a, 1 - np.exp(-(value-a)**2/b), 0)
    elif type == "mu":
        return a + np.sqrt(np.pi * b/4)
    elif type == "sigma":
        return np.sqrt(b*(4-np.pi)/4)
    else: #This is the icdf
        return (-b * np.log(1 - value + 1e-10))**(1/2)+a

def Erlang_noise_pdf(value:float = 0, a:float = 2.0, b:int = 2, type:str = "icdf")-> float:
    """
    Probability Density Function (pdf), Cumulative Density Function (cdf) and inverse cdf for the 
    Erlang (Gamma) noise.\n
    Keyword arguments:\n
    value -- values for which to compute the function\n
    a -- first parameter for the Erlang noise distribution (default 2.0)\n
    b -- second parameter for the Erlang noise distribution; must be an integer (default 2)\n 
    type -- type of function to use: pdf, cdf or icdf (default "icdf")         
    """
    if type == "pdf":
        return np.where(value >= 0, a**b*value**(b-1)*np.exp(-a*value)/math.factorial(b-1), 0)
    elif type == "cdf":
        return sum_pdf(value,Erlang_noise_pdf,[a,b])
    elif type == "mu":
        return b/a
    elif type == "sigma":
        return np.sqrt(b)/a
    else: #This is the icdf
        return np.zeros_like(value)

def exponential_noise_pdf(value:float=0, a:float = 1.0, type:str = "icdf")-> float:
    """
    Probability Density Function (pdf), Cumulative Density Function (cdf) and inverse cdf for the 
    exponential noise.\n
    Keyword arguments:\n
    value -- values for which to compute the function\n
    a -- parameter for the exponential noise distribution\n
    type -- type of function to use: pdf, cdf or icdf (default "icdf")         
    """
    if type == "pdf":
        return np.where(value >= 0, a*np.exp(-a*value), 0)
    elif type == "cdf":
        return 1 - np.exp(-a*value)
    elif type == "mu":
        return 1/a
    elif type == "sigma":
        return 1/a
    else: #This is the icdf
        return -np.log(1 - value + 1e-10)/a

def uniform_noise_pdf(value:float=0, a:float = 0.0,b:float = 1.0, type:str = "icdf")-> float:
    """
    Probability Density Function (pdf), Cumulative Density Function (cdf) and inverse cdf for the 
    exponential noise.\n
    Keyword arguments:\n
    value -- values for which to compute the function (default 0)\n
    a -- first parameter for the uniform noise distribution, its minimum (default 0)\n
    b -- second parameter for the uniform noise distribution, its maximum (default 1)\n 
    type -- type of function to use: pdf, cdf or icdf (default "icdf")         
    """
    if type == "pdf":
        return np.where((value >= a) & (value <= b), 1/(b-a), 0)
    elif type == "cdf":
        tmp = np.where(value >= a, (value - a)/(b-a), 0)
        return np.where(value <= b, tmp, 1)
    elif type == "mu":
        return (a+b)/2
    elif type == "sigma":
        return (b-a)/np.sqrt(12)
    else: #This is the icdf
        return value*(b-a) + a


def sum_pdf(value: np.ndarray,fct,param:list) -> np.ndarray:
    """
    Computes the cdf from the pdf, given the function used\n
    Keyword arguments:\n
    value -- values of the pdf to use\n
    fct -- pdf function to use\n
    param -- parameters to be fed to the distributions
    """
    step = (value[-1] - value[0])/value.shape[0]
    try:
        pdf = fct(value,param[0],param[1],type = "pdf")
    except:
        try:
            pdf = fct(value,param[0],type = "pdf")
        except:
            pdf = np.zeros_like(value)
    value_tot = np.zeros_like(value)
    for i in range(value.shape[0]):
        value_tot[i] = trapezoid(pdf[0:i],dx=step)
    return value_tot

def inverse_cdf(x:np.ndarray,fct,param:np.ndarray,stretch:float = 100) -> np.ndarray:
    """
    Determines the inverse CDF to compute probabilities from the original pdf function,
    by computing as an intermediate state the cdf using sum_pdf function.\n
    Keyword arguments:\n
    x -- values of the pdf to use\n    
    fct -- pdf function to use\n
    param -- parameters to be given to the pdf function\n
    """
    ###
    """value = np.copy(x)*stretch
    cdf = sum_pdf(value,fct,param)
    icdf = np.interp(x, cdf, x)*stretch
    return icdf"""
    value = np.linspace(-10,10,x.shape[0])
    cdf = sum_pdf(value,fct,param)
    icdf = np.interp(x, cdf, value)
    return icdf

def get_pdf_from_uniform(y:np.ndarray,fct,param:list) -> np.ndarray:
    """
    From a given 1-D list values between 0 and 1, return a 1-D array of the values from the ICDF.\n
    In otherwise, this samples the icdf to return the \n
    Used to create noise.\n
    Keyword arguments:\n
    y -- array of values between 0 and 1 to sample the icdf and obtain the pdf\n    
    fct -- pdf function to use\n
    param -- parameters to be given to the pdf function\n    
    """
    ###
    """x = np.arange(0,1,0.0001)
    y = np.copy(y) * x.shape[0]
    y = y.astype(int)
    icdf = inverse_cdf(x,fct,param)

    return icdf[y]"""
    x = np.linspace(0,1-1e-100,10000)

    icdf = inverse_cdf(x,fct,param)
    return np.interp(y, x, icdf)