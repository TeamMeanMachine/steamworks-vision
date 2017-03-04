import pyrealsense as pyrs
import cv2
import numpy as np
from pyrealsense.stream import ColourStream, DepthStream

from threading import Thread
from Queue import Queue, LifoQueue, Full as FullException

from .boiler import run as run_boiler
from .gear import run as run_gear
from .network import run as run_network
from .streams import Infrared2Stream

pyrs.start()
#rs = pyrs.Device(streams = [ColourStream(), DepthStream(width=320, height=240), Infrared2Stream(width = 332, height=252)])
rs = pyrs.Device(streams = [ColourStream(), DepthStream(), Infrared2Stream()])

data_q = Queue()

boiler_q = LifoQueue(maxsize = 6)
gear_q = LifoQueue(maxsize = 6)

boiler_thread = Thread(target=run_boiler, args = (boiler_q, data_q))
boiler_thread.daemon = True
boiler_thread.start()

gear_thread = Thread(target=run_gear, args = (gear_q, data_q))
gear_thread.daemon = True
gear_thread.start()

network_thread = Thread(target = run_network, args = (data_q,))
network_thread.daemon = True
network_thread.start()

## main loop
image_number = 0
while True:
    image_number += 1
    rs.wait_for_frame()

    color_img = rs.colour
    ir_img = rs.infrared2
    depth_img = rs.depth * rs.depth_scale

    color_img = cv2.cvtColor(color_img, cv2.COLOR_RGB2BGR)


    try:
        boiler_q.put_nowait((image_number, ir_img, depth_img))
    except FullException:
        pass
    try:
        gear_q.put_nowait((image_number, ir_img, depth_img))
    except FullException:
        pass
