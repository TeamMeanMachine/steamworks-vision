import cv2
import numpy as np
import logging
import os
from .constants import IR_RESOLUTION as RESOLUTION, IR_FOCAL_LENGTH as FOCAL_LENGTH, IR_FOV as FOV

INTENSITY_THRESHOLD = 200
CONTOUR_SIZE_THRESHOLD = 200
ASPECT_RATIO_ERROR = 10.0
TARGET_TILT_ERROR = 14
HEIGHT_RATIO_TOLERANCE = 0.8

TARGET_WIDTH = 1.25 # in feet

def in_range(n1, n2, tolerance):
    return abs(n1 - n2) < tolerance

def process(ir_img):
    ir_img = ir_img.astype(np.uint8)
    _, threshold_img = cv2.threshold(ir_img, INTENSITY_THRESHOLD, 255, cv2.THRESH_BINARY)

    _, all_contours, _ = cv2.findContours(threshold_img, cv2.CHAIN_APPROX_SIMPLE, cv2.RETR_LIST)

    boxes = []
    for contour in all_contours:
        rect = cv2.boundingRect(contour)
        x, y, w, h = rect

        if h == 0:
            continue

        area = w * h
        if area < CONTOUR_SIZE_THRESHOLD:
            continue

        aspect_ratio = float(w)/h

        boxes.append(rect)


    count = len(boxes)
    for i in range(count - 1):
        fst_box = boxes[i]
        fst_x, fst_y, fst_w, fst_h = fst_box
        for j in range(i + 1, count):
            snd_box = boxes[j]
            snd_x, snd_y, snd_w, snd_h = snd_box

            if not in_range(fst_x, snd_x, TARGET_TILT_ERROR):
                continue
            if not in_range(fst_w, snd_w, TARGET_TILT_ERROR):
                continue

            target_x = (fst_x + fst_x + fst_w) / 2
            target_angle = (float(target_x) / RESOLUTION[0] * FOV) - (FOV / 2)
            target_distance = 573.0 / max(fst_y, snd_y) * 5 - 1.2 

            # draw output image
            out_img = cv2.cvtColor(ir_img, cv2.COLOR_GRAY2BGR)
            for contour in all_contours:
                cv2.drawContours(out_img, [contour], 0, (255, 0, 0), 2)
          
            cv2.line(out_img, (int(target_x), 0), (int(target_x), RESOLUTION[1]), (0, 0, 255), 3)

            return 'BOILER', target_angle, target_distance, out_img
    return None
