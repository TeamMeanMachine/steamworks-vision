from pyrealsense import pyrs

pyrs.start()

rs = pyrs.Device()


## main loop
while True:
    rs.wait_for_frame() # TODO: do stuff with frames
