import cv2
import os
import sys
from os import path
from threading import Thread

import numpy as np
from flask import Flask, render_template, Response

from .network import network_table

FORCE_RECORD = 'record' in sys.argv

stream = Flask(__name__)
image = np.zeros((360, 480, 3), np.uint8)

@stream.route('/')
def index():
    return 'mean machine rulez'

def gen():
    global image
    while True:
        _, img = cv2.imencode('.jpg', image)
        img = img.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')

@stream.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

outputs = None

# create data folder
DATA_DIR = 'data'
if not path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

def serve():
    global stream
    stream.run(host='0.0.0.0', port=5801, debug=False)

def update(feed_img, ir_img, color_img, depth_img):
    global DATA_DIR, outputs, image

    image = feed_img
    if network_table.getBoolean('Record', False) or FORCE_RECORD:
        if not recording:
            four_cc = cv2.VideoWriter_fourcc(*'XVID')
            n = 0
            while not path.isdir('{}/capture-{}'.format(DATA_DIR, n)):
                n += 1
            out_path = '{}/capture-{}'.format(DATA_DIR, n)
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
        # stop recording
        for out in outputs:
            out.release()
        outputs = None

def release():
    if outputs:
        for out in outputs:
            out.release()
