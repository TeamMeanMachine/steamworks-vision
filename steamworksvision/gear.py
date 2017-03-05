import cv2
import sys
import numpy as np
import time

from .util import IntervalCalculator

INTENSITY_THRESHOLD = 254
CONTOUR_SIZE_THRESHOLD = 100
CONTOUR_MIN_EXTENT = 0.2
CONTOUR_MAX_EXTENT = 0.9
TARGET_TILT_ERROR = 12
FOV = 70

DEBUG = 'debug' in sys.argv and 'gear' in sys.argv

def contour_filter(contour):
    area = cv2.contourArea(contour)
    if area < CONTOUR_SIZE_THRESHOLD: return False
    x, y, w, h = cv2.boundingRect(contour)
    rect_area = w * h
    extent = float(area) / rect_area
    if extent < CONTOUR_MIN_EXTENT or extent > CONTOUR_MAX_EXTENT: return False


    return True

def locate(contours):
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
                x = (fst_leftmost[0] + snd_rightmost[0]) / 2
                y = (fst_topmost[1] + snd_bottommost[1]) / 2
                return x, y
    return None

def run(in_q, out_q):
    global depth_offset, last_time, fps_smooth, smoothing, fps
    last_image_number = 0

    if DEBUG:
        fps_counter = IntervalCalculator()

    while True:
        image_number, original_ir_img, depth_img = in_q.get()
        width = len(original_ir_img[0])

        if last_image_number > image_number: continue
        last_image_number = image_number

        ret, ir_img = cv2.threshold(original_ir_img.astype(np.uint8), INTENSITY_THRESHOLD, 255, cv2.THRESH_BINARY)
        ir_img, contours, heirarchy = cv2.findContours(ir_img, cv2.CHAIN_APPROX_SIMPLE, cv2.RETR_LIST)
        contours = filter(contour_filter, contours)

        data = locate(contours)
        target_angle = None

        depth_img = depth_img * 1000
        depth_img = cv2.applyColorMap(depth_img.astype(np.uint8), cv2.COLORMAP_RAINBOW)
        ir_img = cv2.cvtColor(original_ir_img, cv2.COLOR_GRAY2BGR)

        if data != None:
            target = data
            target_angle = (float(target[0]) / width * FOV) - (FOV / 2)
            if DEBUG:
                if target != None:
                    x, y = map(int, target)
                    height = len(ir_img[0])
                    cv2.line(ir_img, (x, 0), (x, height), (0, 0, 255), 3)
                    cv2.putText(ir_img, 'Target: {} degrees'.format(target_angle), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (50, 205, 50))

        if DEBUG:
            # get framerate
            fps = fps_counter.calc_interval()
            cv2.putText(ir_img, 'FPS: {}'.format(fps), (0, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))


            cv2.drawContours(ir_img, contours, -1, (0, 255, 0), 2)
            cv2.imshow('depth', depth_img)
            cv2.imshow('target', ir_img)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                pass

        result = 'GEAR;{};{};0'.format(image_number, target_angle)
        out_q.put(result)
