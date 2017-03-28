import ctypes
from pyrealsense.stream import Stream
from pyrealsense.constants import rs_stream, rs_format

class Infrared2Stream(Stream):
    def __init__(self, name='infrared2',
                       native=True,
                       stream=rs_stream.RS_STREAM_INFRARED2,
                       width=640,
                       height=480,
                       format=rs_format.RS_FORMAT_Y8,
                       fps=30):
        super(Infrared2Stream, self).__init__(name, native, stream, width, height, format, fps)
        self.shape = (height, width)
        self.dtype = ctypes.c_uint8

class InfraredStream(Stream):
    def __init__(self, name='infrared',
                       native=True,
                       stream=rs_stream.RS_STREAM_INFRARED,
                       width=640,
                       height=480,
                       format=rs_format.RS_FORMAT_Y8,
                       fps=30):
        super(InfraredStream, self).__init__(name, native, stream, width, height, format, fps)
        self.shape = (height, width)
        self.dtype = ctypes.c_uint8

