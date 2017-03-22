import cscore as cs
import numpy as np

output_source = cs.CvSource('camera-feed', cs.VideoMode.PixelFormat.kMJPEG, 640, 480, 30)
mjpeg_server = cs.MjpegServer('httpserver', 8081)
mjpeg_server.setSource(output_source)
print('mjpeg server listening on http://0.0.0.0:8081')

def send(feed_img):
    global output_source
    output_source.putFrame(feed_img)
