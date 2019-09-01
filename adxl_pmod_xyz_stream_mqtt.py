#Using the PMOD AD2 to collect live data from ADXL355 Accelerometer
#The data for XYZ of the ADXL335 values is collected and stored in Xlnk buffers of size 100 for each data set
#It is then sent to the Programmable logic via DMA transfer to custom IPs 
#The IPs built in the overlay will carry out a function for each data set sent in
#The X values are squared, the Y values are multiplied by 10 and the Z values are *5 + 450
#The output is then sent back to the PS and printed to the screen
#Certain values are taken from the returned data and sent over the network to another device using MQTT
#
#John Tracey DCU August 2019 MECE
#

#import libraries
from math import ceil
import time 
from pynq import Xlnk
import numpy as np
import matplotlib.pyplot as plt
from pynq.lib import Pmod_ADC
from pynq.overlays.base import BaseOverlay
import json

#load the Base overlay which is needed to operate the PMOD ADC
ol = BaseOverlay("base.bit")

#Initialize the PMOD device
adc = Pmod_ADC(ol.PMODB)

#instansiate an xlnk object to create the Xlnk buffers needed to collect and transfer data
#xlnk = Xlnk()
#xlnk.cma_stats() 
# Allocate buffers for the input sample signals and the outputs
#instansiate an xlnk objects to create the Xlnk buffers needed to collect and transfer data
xlnk_x = Xlnk()
xlnk_y = Xlnk()
xlnk_z = Xlnk()

#allocate input memory buffers 
px_buffer = xlnk_x.cma_array(shape=(100,), dtype=np.uint32)
py_buffer = xlnk_y.cma_array(shape=(100,), dtype=np.uint32)
pz_buffer = xlnk_z.cma_array(shape=(100,), dtype=np.uint32)

#allocate output memory buffers
out_buffer_x = xlnk_x.cma_array(shape=(100,), dtype=np.int32)
out_buffer_y = xlnk_x.cma_array(shape=(100,), dtype=np.int32)
out_buffer_z = xlnk_x.cma_array(shape=(100,), dtype=np.int32)


#collect samples from the ADXL355 attached to the PMOD AD2
samples = []
count = 0
while count < 100:
    count = count +1
    #read x-value
    samplex = adc.read_raw(1,0,0)
    #time.sleep(0.01)
    #samples.append(sample[0])
    #read y-value
    sampley = adc.read_raw(0,1,0)
    time.sleep(0.01)
    #read z-value
    samplez = adc.read_raw(0,0,1)
    
    #populate the Xlnk buffers with the sample data
    px_buffer[count-1] = samplex[0]
    py_buffer[count-1] = sampley[0]
    pz_buffer[count-1] = samplez[0]
    
#print the contents of the buffers 
print("Xlnk buffer x-values: ",px_buffer)
print("Xlnk buffer y-values: ",py_buffer)
print("Xlnk buffer Z-values: ",pz_buffer)

#reset the ADC
adc.reset()

# Now Transfer the contents of the buffers to the Custom IPs in PL via AXI DMA
# X-Values to X-Function, Y-Values to Y Function, Z-Values to Z-Function

#First delete the base overlay
del ol

#load the overlay for the custom streaming XYZ-values IP built and tested in TEST D
from pynq import Overlay
overlay = Overlay('/home/xilinx/pynq/overlays/stream_xyz/stream_xyz.bit')

#Test the overlay
#overlay? #returns the IP blocks contained in the Overlay which were built for each function
#overlay.ip_dict # returns full path to each dma x,y,z = x_function.dmaz, y_function.dmay, z_function.dmaz

#assign the DMAs which are the IPs built to recive and operate on the incomming buffer data
dma_x = overlay.x_function.dmax
dma_y = overlay.y_function.dmay
dma_z = overlay.z_function.dmaz

# Trigger the DMA transfer of the samples from buffers to the PL

#set up send channel xyz
dma_x.sendchannel.transfer(px_buffer)
dma_y.sendchannel.transfer(py_buffer)
dma_z.sendchannel.transfer(pz_buffer)

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

#Print out the buffer values after the transfer into the IP and back to PS
#X-Values should be (X*X), Y-values should be (Y*10), Z-values should be ((5*Z)+450)

print("X-Values Output Buffer Values after transfer: ",out_buffer_x)
print("Y-Values Output Buffer Values after transfer: ",out_buffer_x)
print("Z-Values Output Buffer Values after transfer: ",out_buffer_x)

#Testing a simple alarm condition
if out_buffer_x.any() == 0 and out_buffer_y.any() == 0 and out_buffer_z.any() <= 450 :
    print("Huston we have a problem!!")
else:
    print("system stable no alarms")

#Testing creating a json object for transfer over network using MQTT
#import json
#Testing JSON convert python to JSON 
#the python object is the adxl alarm readings

axdl_read = {
  "X-Value": int(out_buffer_x[30]),
  "Y-Value": int(out_buffer_y[30]),
  "Z-Value": int(out_buffer_z[30])
}       

# convert into JSON for transfer MQTT
axdl_tx = json.dumps(axdl_read)

# print the JSON string:
print(axdl_tx)


# Free the buffers
px_buffer.close()
py_buffer.close()
pz_buffer_z.close()

out_buffer_x.close()
out_buffer_y.close()
out_buffer_z.close()
