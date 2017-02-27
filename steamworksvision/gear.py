
import cv2
import sys
import numpy as np

INTENSITY_THRESHOLD = 254
CONTOUR_SIZE_THRESHOLD = 25
TARGET_TILT_ERROR = 4
FOV = 70

DEBUG = 'debug' in sys.argv and 'gear' in sys.argv

def contour_filter(contour):
    return cv2.contourArea(contour) > CONTOUR_SIZE_THRESHOLD

def locate_boiler(contours):
    count = len(contours)
    for i in range(0, count - 1):
        fst_cnt = contours[i]
        fst_topmost = tuple(fst_cnt[fst_cnt[:,:,1].argmin()][0])
        fst_bottommost = tuple(fst_cnt[fst_cnt[:,:,1].argmax()][0])
        for j in range(i+1, count):
            snd_cnt = contours[j]
            snd_topmost = tuple(snd_cnt[snd_cnt[:,:,1].argmin()][0])
            top_error = abs(fst_topmost[1] - snd_topmost[1])
            if top_error > TARGET_TILT_ERROR: continue

            snd_bottommost = tuple(snd_cnt[snd_cnt[:,:,1].argmax()][0])
            bottom_error = abs(fst_bottommost[1] - snd_bottommost[1])
            if bottom_error <= TARGET_TILT_ERROR:
                fst_leftmost = tuple(fst_cnt[fst_cnt[:,:,0].argmin()][0])
                snd_rightmost = tuple(snd_cnt[snd_cnt[:,:,0].argmax()][0])
                return (fst_leftmost[0] + snd_rightmost[0]) / 2
    return None

last_image_number = 0
def run(in_q, out_q):
    global last_image_number
    while True:
        image_number, ir_img, depth_img = in_q.get()
        width = len(ir_img[0])

        if last_image_number > image_number: continue
        last_image_number = image_number

        ret, ir_img = cv2.threshold(ir_img.astype(np.uint8), INTENSITY_THRESHOLD, 255, cv2.THRESH_BINARY)
        ir_img, contours, heirarchy = cv2.findContours(ir_img, cv2.CHAIN_APPROX_SIMPLE, cv2.RETR_LIST)
        contours = filter(contour_filter, contours)

        data = locate_boiler(contours)
        target_angle = None

        if data != None:
            target = data
            target_angle = (float(target) / width * FOV) - (FOV / 2)
            if DEBUG:
                height = len(ir_img[0])
                
                if target != None:
                    ir_img =  cv2.cvtColor(ir_img, cv2.COLOR_GRAY2BGR)
                    cv2.line(ir_img, (int(target), 0), (int(target), height), (0, 0, 255), 3)

        if DEBUG:
            cv2.imshow('', ir_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                pass

        result = 'GEAR {} {} 0'.format(image_number, target_angle)
        out_q.put(result)
