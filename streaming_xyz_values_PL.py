# 	Source code freely availble for use from : http://eecs6111.mit.edu/6s193/pynq_lab5/
# 	ammended by John Tracey DCU for project testing
#	6/7/19
# X-Y-Z input values at varying input sample rates

from pynq import Overlay
import pynq.lib.dma

%matplotlib notebook
import matplotlib.pyplot as plt

#Function to plot values to notebook for graphical display
def plot_to_notebook(time_sec,in_signal,n_samples,out_signal=None):
    plt.figure()
    plt.subplot(1, 1, 1)
    plt.xlabel('Time (usec)')
    plt.grid()
    plt.plot(time_sec[:n_samples]*1e6,in_signal[:n_samples],'y-',label='Input signal')
    if out_signal is not None:
        plt.plot(time_sec[:n_samples]*1e6,out_signal[:n_samples],'g-',linewidth=2,label='Module output')
    plt.legend()
    
overlay = Overlay('/home/xilinx/pynq/overlays/testing/xyz_stream/stream_xyz.bit') # load the bitstream

#Check the Overlay for IPs and fullpaths
#x_function/dmax --- y_function/dmay -- z_function/dmaz
#print(overlay.ip_dict)

#assign the DMAs
dma_x = overlay.x_function.dmax
dma_y = overlay.y_function.dmay
dma_z = overlay.z_function.dmaz



import numpy as np

# Total time
T = 0.000001
# Sampling frequency
fs = 100e6
#number of samples = 0.000001 * 100,000,000 = 100 samples
n = int(T * fs)
# Time vector in seconds
t = np.linspace(0, T, n, endpoint=False)
# Samples of the signal - generate the noisy signal
samples = 10000*np.sin(0.2e6*2*np.pi*t) + 1500*np.cos(46e6*2*np.pi*t) + 2000*np.sin(12e6*2*np.pi*t)
# Convert samples to 32-bit integers
samples = samples.astype(np.int32)
print('Number of samples: ',len(samples))

# Plot signal to the notebook
plot_to_notebook(t,samples,1000)