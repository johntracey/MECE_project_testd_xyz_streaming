#Test the operation in Hardware
from scipy.signal import lfilter
from pynq import Xlnk
import numpy as np

# Allocate buffers for the input sample signals and the outputs
xlnk_x = Xlnk()
xlnk_y = Xlnk()
xlnk_z = Xlnk()


# X_BUFFERS
in_buffer_x = xlnk_x.cma_array(shape=(n,), dtype=np.int32)
out_buffer_x = xlnk_x.cma_array(shape=(n,), dtype=np.int32)

# Y_BUFFERS
in_buffer_y = xlnk_y.cma_array(shape=(n,), dtype=np.int32)
out_buffer_y = xlnk_y.cma_array(shape=(n,), dtype=np.int32)

# Z_BUFFERS
in_buffer_z = xlnk_z.cma_array(shape=(n,), dtype=np.int32)
out_buffer_z = xlnk_z.cma_array(shape=(n,), dtype=np.int32)


# Copy the samples to the in_buffer
np.copyto(in_buffer_x,samples)
np.copyto(in_buffer_y,samples)
np.copyto(in_buffer_z,samples)



# Trigger the DMA transfer of the samples to the PL 
# Start the timer and wait for the result

import time
start_time = time.time()

#set up send channel xyz
dma_x.sendchannel.transfer(in_buffer_x)
dma_y.sendchannel.transfer(in_buffer_y)
dma_z.sendchannel.transfer(in_buffer_z)

#set up recieve channel xyz
dma_x.recvchannel.transfer(out_buffer_x)
dma_y.recvchannel.transfer(out_buffer_y)
dma_z.recvchannel.transfer(out_buffer_z)

# wait for the result
dma_x.sendchannel.wait()
dma_y.sendchannel.wait()
dma_z.sendchannel.wait()

dma_x.recvchannel.wait()
dma_y.recvchannel.wait()
dma_z.recvchannel.wait()

#Stop the timer and print total execution time of transfer and operation on the samples
stop_time = time.time()
hw_exec_time = stop_time-start_time
print('Hardware execution time: ',hw_exec_time)

#print('Hardware acceleration factor: ',sw_exec_time / hw_exec_time) ************

# Plot to the notebook
plot_to_notebook(t,samples,1000,out_signal=out_buffer_x)
plot_to_notebook(t,samples,1000,out_signal=out_buffer_y)
plot_to_notebook(t,samples,1000,out_signal=out_buffer_z)

# Free the buffers
in_buffer_x.close()
in_buffer_y.close()
in_buffer_z.close()

out_buffer_x.close()
out_buffer_y.close()
out_buffer_z.close()