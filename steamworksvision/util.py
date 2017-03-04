from time import time

class IntervalCalculator():
    def __init__(self):
        self.last_time = time()

    def calc_interval(self):
        now_time = time()
        dt = now_time - self.last_time
        fps = 1/dt
        self.last_time = now_time
        return fps
