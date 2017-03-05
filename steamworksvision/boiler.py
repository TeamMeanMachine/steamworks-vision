import cv2
import sys
import numpy as np

from .util import IntervalCalculator

INTENSITY_THRESHOLD = 150
CONTOUR_SIZE_THRESHOLD = 100
ASPECT_RATIO_ERROR = 8.0
TARGET_TILT_ERROR = 16
FOV = 70

DEBUG = 'debug' in sys.argv and 'boiler' in sys.argv

def contour_filter(contour):
    x, y, width, height = cv2.boundingRect(contour)
    area = width * height
    if area < CONTOUR_SIZE_THRESHOLD:
        return False
    aspect_ratio = float(width)/height

    if aspect_ratio < 1.5: return False
    return True

def locate_boiler(contours):
    count = len(contours)
    for i in range(0, count - 1):
        fst_cnt = contours[i]
        fst_leftmost = tuple(fst_cnt[fst_cnt[:,:,0].argmin()][0])
        fst_rightmost = tuple(fst_cnt[fst_cnt[:,:,0].argmax()][0])
        for j in range(i+1, count):
            snd_cnt = contours[j]
            snd_leftmost = tuple(snd_cnt[snd_cnt[:,:,0].argmin()][0])
            left_error = abs(fst_leftmost[0] - snd_leftmost[0])
            if left_error > TARGET_TILT_ERROR: continue

            snd_rightmost = tuple(snd_cnt[snd_cnt[:,:,0].argmax()][0])
            right_error = abs(fst_rightmost[0] - snd_rightmost[0])
            if right_error <= TARGET_TILT_ERROR:
                return (fst_leftmost[0] + fst_rightmost[0]) / 2, fst_leftmost, fst_rightmost, snd_leftmost, snd_rightmost
    return None

last_image_number = 0
def run(in_q, out_q):
    global last_image_number

    if DEBUG:
        fps_counter = IntervalCalculator()

    while True:
        image_number, ir_img, depth_img, color_img = in_q.get()
        width = len(ir_img[0])
        raw_ir_img = ir_img

        if last_image_number > image_number: continue
        last_image_number = image_number

        ret, ir_img = cv2.threshold(ir_img.astype(np.uint8), INTENSITY_THRESHOLD, 255, cv2.THRESH_BINARY)

        start_ticks = cv2.getTickCount()
        ir_img, contours, heirarchy = cv2.findContours(ir_img, cv2.CHAIN_APPROX_SIMPLE, cv2.RETR_LIST)

        find_contours_ticks = cv2.getTickCount() - start_ticks

        if False: #len(contours) > 50:
            contours = []
            print('no contours')
        else:
            contours = filter(contour_filter, contours)
        contour_filter_ticks = cv2.getTickCount() - start_ticks

        data = locate_boiler(contours)
        locate_boiler_ticks = cv2.getTickCount() - start_ticks
        target_angle = None

        if data != None:
            target, fst_leftmost, fst_rightmost, snd_leftmost, snd_rightmost = data
            target_angle = (float(target) / width * FOV) - (FOV / 2)
            target_angle = -target_angle # camera is upside down
            if DEBUG:
                height = len(ir_img[0])
                
                if target != None:
                    ir_img =  cv2.cvtColor(ir_img, cv2.COLOR_GRAY2BGR)
                    cv2.line(ir_img, (int(target), 0), (int(target), height), (0, 0, 255), 3)
                    cv2.line(ir_img, fst_leftmost, fst_rightmost, (255, 0, 0), 2)
                    cv2.line(ir_img, snd_leftmost, snd_rightmost, (0, 255, 0), 2)

        if DEBUG:
            fps = fps_counter.calc_interval()

            cv2.putText(ir_img, 'FPS: {}'.format(fps), (0, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
            total_ticks = find_contours_ticks + locate_boiler_ticks + contour_filter_ticks
            fc = float(find_contours_ticks) / total_ticks * 100
            cf = float(contour_filter_ticks) / total_ticks * 100
            lb = float(locate_boiler_ticks) / total_ticks * 100
            cv2.putText(ir_img, 'fc: {}, cf: {}, lb: {}'.format(fc, cf, lb), (0, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
            cv2.drawContours(ir_img, contours, -1, (0, 255, 0), 2)

            cv2.imshow('color', color_img)
            cv2.imshow('raw', raw_ir_img)
            cv2.imshow('boiler', ir_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                pass

        out_q.put('BOILER;{};{};0'.format(image_number, target_angle))
