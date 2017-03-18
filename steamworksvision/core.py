import cv2
import sys
import numpy as np
import os

from threading import Thread
from time import time
from Queue import Queue

import camerastream
from .boiler import process as process_boiler
from .gear import process as process_peg
from .network import network_table, run as run_network
from .constants import IR_RESOLUTION

def main():
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
        rs = pyrs.Device(streams = [ColourStream(), DepthStream(), Infrared2Stream()])


    processor = None

    net_in_q = Queue()
    net_out_q = Queue()

    network_thread = Thread(target = run_network, args=(net_in_q, net_out_q))
    network_thread.daemon = True
    network_thread.start()

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

            ir_img = rs.infrared2
            color_img = rs.colour
            depth_img = rs.depth
        else:
            ir_img = np.zeros((360, 480), np.uint8)
            color_img = np.zeros((360, 480, 3), np.uint8)
            depth_img = np.zeros((360, 480), np.uint8)

        if processor:
            data = processor(ir_img)

            ir_color_img = cv2.cvtColor(ir_img, cv2.COLOR_GRAY2BGR)
            if data:
                name, x, angle, distance = data
                net_out_q.put('{};{};{};{}'.format(name, image_number, angle, distance))
                cv2.line(ir_color_img, (int(x), 0), (int(x), IR_RESOLUTION[1]), (0, 0, 255), 3)
            else:
                net_out_q.put('NONE')

            feed_img = ir_color_img
        else:
            net_out_q.put('NONE')
            feed_img = color_img

        # framerate stuff
        now_time = time()
        fps = round(1/(now_time - last_time), 2)
        last_time = now_time

        cv2.putText(feed_img, 'FPS: {}'.format(fps), (0, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 205, 50))

        ir_out_img = cv2.cvtColor(ir_img, cv2.COLOR_GRAY2BGR)
        depth_out_img = cv2.cvtColor(depth_img, cv2.COLOR_GRAY2BGR)
        camerastream.update(feed_img, ir_out_img, color_img, depth_out_img)

        if DEBUG:
            cv2.imshow('camera-feed', feed_img)
            cv2.waitKey(1)

main_thread = Thread(target=main)
main_thread.daemon = True
main_thread.start()

camerastream.serve()
camerastream.release()
