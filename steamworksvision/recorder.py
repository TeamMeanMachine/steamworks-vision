import cv2
import os
import sys
from os import path
from threading import Thread

import numpy as np

from .network import network_table

FORCE_RECORD = 'record' in sys.argv

outputs = None

network_table.putBoolean('Record', False)

def send(feed_img, ir_img, color_img, depth_img):
    global outputs

    image = feed_img
    if network_table.getBoolean('Record', False) or FORCE_RECORD:
        if not recording:
            four_cc = cv2.VideoWriter_fourcc(*'XVID')
            n = 0
            while not path.isdir('{}/capture-{}'.format(DATA_DIR, n)):
                n += 1
            out_path = '{}/capture-{}'.format(DATA_DIR, n)
            print('Recording to directory {}'.format(out_path))
            os.mkdir(out_path)

            feed_out = cv2.VideoWriter('{}/feed.avi'.format(out_path))
            ir_out = cv2.VideoWriter('{}/ir.avi'.format(out_path))
            color_out = cv2.VideoWriter('{}/color.avi'.format(out_path))
            depth_out = cv2.VideoWriter('{}/depth.avi'.format(out_path))
            outputs = (feed_out, ir_out, color_out, depth_out)
        else:
            feed_out, ir_out, color_out, depth_out = outputs
            feed_out.write(feed_img)
            ir_out.write(ir_img)
            color_out.write(color_img)
            depth_out.write(depth_img)
    elif outputs != None:
        release()

def release():
    print('Recording stopped')
    if outputs:
        for out in outputs:
            out.release()
