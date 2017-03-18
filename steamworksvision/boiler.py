import cv2
import numpy as np
import os
from .constants import IR_RESOLUTION as RESOLUTION, IR_FOCAL_LENGTH as FOCAL_LENGTH, IR_FOV as FOV

INTENSITY_THRESHOLD = 220
CONTOUR_SIZE_THRESHOLD = 100
ASPECT_RATIO_ERROR = 8.0
TARGET_TILT_ERROR = 16

TARGET_WIDTH = 1.25 # in feet

def process(ir_img):
    ir_img = ir_img.astype(np.uint8)
    _, ir_img = cv2.threshold(ir_img, INTENSITY_THRESHOLD, 255, cv2.THRESH_BINARY)

    ir_img, all_contours, _ = cv2.findContours(ir_img, cv2.CHAIN_APPROX_SIMPLE, cv2.RETR_LIST)

    filtered_contours = []
    for contour in all_contours:
        x, y, width, height = cv2.boundingRect(contour)
        area = width * height
        if area < CONTOUR_SIZE_THRESHOLD: continue
        aspect_ratio = float(width)/height

        if aspect_ratio < 1.5: continue
        filtered_contours.append((contour, (x, y, width, height)))

    # locate boiler

    count = len(filtered_contours)
    for i in range(0, count - 1):
        fst_cnt, fst_bounding_data = filtered_contours[i]
        fst_bounding_x, fst_bounding_y, fst_bounding_width, fst_bounding_height = fst_bounding_data
        fst_left_x = fst_bounding_x
        fst_right_x = fst_bounding_x + fst_bounding_width
        for j in range(i+1, count):
            snd_cnt, snd_bounding_data = filtered_contours[i]
            snd_bounding_x, snd_bounding_y, snd_bounding_width, snd_bounding_height = snd_bounding_data

            snd_left_x = snd_bounding_x
            snd_right_x = snd_bounding_x + snd_bounding_width
            # compare
            if abs(fst_left_x - snd_left_x) < TARGET_TILT_ERROR and abs(fst_right_x - snd_right_x) < TARGET_TILT_ERROR:
                # target found
                target_x = (fst_left_x + fst_right_x) / 2
                target_angle = (float(target_x) / RESOLUTION[0] * FOV) - (FOV / 2)
                target_distance = (TARGET_WIDTH * FOCAL_LENGTH) / fst_bounding_width
                return 'BOILER', target_x, target_angle, target_distance
    return None
