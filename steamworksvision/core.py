import pyrealsense as pyrs
from threading import Thread
from queue import Queue

from .boiler import run as run_boiler

pyrs.start()
rs = pyrs.Device()

boiler_q = Queue(maxsize = 6)
gear_q = Queue(maxsize = 6)
pyrs.start()


boiler_thread = Thread(target=run_boiler, args = (rs,))
boiler_thread.daemon = True
boiler_thread.start()

## main loop
while True:
    rs.wait_for_frame() # TODO: do stuff with frames
