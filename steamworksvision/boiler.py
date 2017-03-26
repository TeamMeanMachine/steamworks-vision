import cv2
import numpy as np
import logging
import os

from .constants import IR_RESOLUTION as RESOLUTION, IR_FOCAL_LENGTH as FOCAL_LENGTH, IR_FOV as FOV
from .network import network_table

INTENSITY_THRESHOLD = 150
CONTOUR_SIZE_THRESHOLD = 100
ASPECT_RATIO_ERROR = 10.0
TARGET_TILT_ERROR = 14
HEIGHT_RATIO_TOLERANCE = 0.8

TARGET_WIDTH = 1.25 # in feet

def in_range(n1, n2, tolerance):
    return abs(n1 - n2) < tolerance

def process(ir_img):
    global a, b
    ir_img = ir_img.astype(np.uint8)
    #_, threshold_img = cv2.threshold(ir_img, INTENSITY_THRESHOLD, 255, cv2.THRESH_BINARY)
    edge_img = cv2.Canny(ir_img, 35, 350)

    _, all_contours, _ = cv2.findContours(edge_img, cv2.CHAIN_APPROX_SIMPLE, cv2.RETR_LIST)

    boxes = []
    for contour in all_contours:
        rect = cv2.boundingRect(contour)
        x, y, w, h = rect

        if h == 0:
            continue

        area = cv2.contourArea(contour)
        if area < CONTOUR_SIZE_THRESHOLD:
            continue
        hull_area = cv2.contourArea(cv2.convexHull(contour))
        solidity = float(area) / hull_area


        if solidity < 0.5:
            continue

        boxes.append(rect)

    out_img = cv2.cvtColor(ir_img, cv2.COLOR_GRAY2BGR)
    # crosshairs
    offset = int(network_table.getNumber('Crosshair Offset', 0))
    base = int(RESOLUTION[0]/2) + offset
    cv2.line(out_img, (base, 0), (base, RESOLUTION[1]), (0, 255, 255), 1)

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
            target_angle = -target_angle
            min_y = min(fst_y, snd_y)

            if min_y == 0: continue

            width = (fst_w + snd_w) / 2.0

            target_distance = (TARGET_WIDTH * FOCAL_LENGTH) / width

            # draw output image
            for contour in all_contours:
                cv2.drawContours(out_img, [contour], 0, (255, 0, 0), 2)

            for box in boxes:
                x, y, w, h = box
                cv2.rectangle(out_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # target line
            cv2.line(out_img, (int(target_x), 0), (int(target_x), RESOLUTION[1]), (0, 0, 255), 2)
            cv2.putText(out_img, 'Distance: {}'.format(round(target_distance, 3)), (0, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 205, 50))

            return (target_angle, target_distance), out_img
    return None, out_img
