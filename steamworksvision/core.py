import pyrealsense as pyrs
import cv2
import sys

from threading import Thread
from time import time
from Queue import Queue
from pyrealsense.stream import ColourStream, DepthStream

from .boiler import process as process_boiler
from .network import run as run_network
from .streams import Infrared2Stream
from .constants import IR_RESOLUTION

DEBUG = 'debug' in sys.argv

pyrs.start()

rs = pyrs.Device(streams = [ColourStream(), DepthStream(), Infrared2Stream()])

processor = process_boiler

net_in_q = Queue()
net_out_q = Queue()

network_thread = Thread(target = run_network, args=(net_in_q, net_out_q))
network_thread.daemon = True
network_thread.start()

image_number = 0
last_time = time()
while True:
    image_number += 1
    rs.wait_for_frame()

    ir_img = rs.infrared2
    color_img = rs.colour


    if processor != None:
        data = processor(ir_img)

        if DEBUG:
            ir_img = cv2.cvtColor(ir_img, cv2.COLOR_GRAY2BGR)
        if data != None:
            name, x, angle, distance = data
            net_out_q.put('{};{};{};{}'.format(name, image_number, angle, distance))
            if DEBUG:
                cv2.line(ir_img, (int(x), 0), (int(x), IR_RESOLUTION[1]), (0, 0, 255), 3)
        else:
            net_out_q.put('NONE')
    else:
        net_out_q.put('NONE')

    # framerate stuff
    now_time = time()
    dt = now_time - last_time
    fps = 1/dt
    fps = round(fps, 2)
    last_time = now_time

    if DEBUG:
        if processor != None:
            feed_img = ir_img
        else:
            feed_img = color_img

        cv2.putText(feed_img, 'FPS: {}'.format(fps), (0, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 205, 50))

        cv2.imshow('camera-feed', feed_img)
        cv2.waitKey(1)
