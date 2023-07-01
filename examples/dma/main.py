from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from pynq import allocate, Overlay

resize_design = Overlay("resizer.bit")
dma = resize_design.axi_dma_0
resizer = resize_design.resize_accel_0

image_path = "images/sahara.jpg"
original_image = Image.open(image_path)

canvas = plt.gcf()
size = canvas.get_size_inches()
canvas.set_size_inches(size*2)

old_width, old_height = original_image.size
print("Image size: {}x{} pixels.".format(old_width, old_height))
plt.figure(figsize=(12, 10));
_ = plt.imshow(original_image)

resize_factor = 2
new_width = int(old_width/resize_factor)
new_height = int(old_height/resize_factor)

in_buffer = allocate(shape=(old_height, old_width, 3), 
                           dtype=np.uint8, cacheable=1)
out_buffer = allocate(shape=(new_height, new_width, 3), 
                            dtype=np.uint8, cacheable=1)

in_buffer[:] = np.array(original_image)

def run_kernel():
    dma.sendchannel.transfer(in_buffer)
    dma.recvchannel.transfer(out_buffer)    
    resizer.write(0x00,0x81) # start
    dma.sendchannel.wait()
    dma.recvchannel.wait()

resizer.register_map.src_rows = old_height
resizer.register_map.src_cols = old_width
resizer.register_map.dst_rows = new_height
resizer.register_map.dst_cols = new_width

run_kernel()
resized_image = Image.fromarray(out_buffer)
print("Image size: {}x{} pixels.".format(new_width, new_height))
plt.figure(figsize=(12, 10));
_ = plt.imshow(resized_image)

del in_buffer
del out_buffer