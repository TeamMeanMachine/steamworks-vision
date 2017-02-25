import cv2

def run(q):
    while True:
        ir_img, depth_img = q.get()

        cv2.imshow('', ir_img)
        cv2.waitKey(1)
        q.task_done()
