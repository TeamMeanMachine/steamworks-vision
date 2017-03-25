import numpy as np
import sys
import cv2
import os

from threading import Thread
from time import time
from queue import Queue

import steamworksvision.recorder as recorder
import steamworksvision.camerafeed as feed
from .boiler import process as process_boiler
from .gear import process as process_peg
from .network import network_table, run as run_network
from .constants import IR_RESOLUTION

# process argv
DEBUG = 'debug' in sys.argv
MOCK = 'mock' in sys.argv
if 'boiler' in sys.argv: FORCE = 'BOILER'
elif 'peg' in sys.argv: FORCE = 'PEG'
else: FORCE = None

if not MOCK:
    import pyrealsense as pyrs
    from pyrealsense.stream import ColourStream, DepthStream
    from .streams import Infrared2Stream
    pyrs.start()
    rs = pyrs.Device(streams = [ColourStream(width = 1920, height = 1080), DepthStream(), Infrared2Stream()])

processor = None

net_in_q = Queue()
net_out_q = Queue()

network_thread = Thread(target = run_network, args=(net_in_q, net_out_q))
network_thread.daemon = True
network_thread.start()

network_table.putString('Mode', 'IDLE')

image_number = 0
last_time = time()
while True:
    image_number += 1

    # read current state
    if FORCE:
        mode = FORCE
    else:
        mode = network_table.getString('Mode', 'IDLE')
    if mode == 'BOILER':
        processor = process_boiler
    elif mode == 'PEG':
        processor = process_peg
    else:
        processor = None

    if not MOCK:
        rs.wait_for_frame()

        ir_img = cv2.GaussianBlur(rs.infrared2, (5, 5), 0)
        full_color_img = rs.colour
        depth_img = rs.depth * rs.depth_scale

        ir_img = cv2.flip(ir_img, -1)
        full_color_img = cv2.flip(full_color_img, -1)
        depth_img = cv2.flip(depth_img, -1)

        color_img = cv2.resize(full_color_img, (640, 480), interpolation = cv2.INTER_AREA)
    else:
        ir_img = np.zeros((360, 480), np.uint8)
        full_color_img = np.zeros((1080, 1920, 3), np.uint8)
        color_img = np.zeros((360, 480, 3), np.uint8)
        depth_img = np.zeros((360, 480), np.uint16)

    if processor:
        data = processor(ir_img)

        if data:
            name, angle, distance, out_img = data
            net_out_q.put('{};{};{};{}'.format(name, image_number, angle, distance))
            feed_img = out_img
        else:
            net_out_q.put('NONE')
            ir_color_img = cv2.cvtColor(ir_img, cv2.COLOR_GRAY2BGR)
            feed_img = ir_color_img

    else:
        net_out_q.put('NONE')
        feed_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2RGB)
        #feed_img = np.rot90(np.rot90(feed_img))

    # framerate stuff
    now_time = time()
    fps = round(1/(now_time - last_time), 2)
    last_time = now_time

    cv2.putText(feed_img, 'FPS: {}'.format(fps), (0, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 205, 50))

    depth_out_img = depth_img * 1000
    depth_out_img = cv2.applyColorMap(depth_out_img.astype(np.uint8), cv2.COLORMAP_RAINBOW)


    feed.send(feed_img)
    recorder.send(feed_img, ir_img, full_color_img, depth_img)
    if DEBUG:
        cv2.imshow('camera-feed', feed_img)
        cv2.waitKey(1)

