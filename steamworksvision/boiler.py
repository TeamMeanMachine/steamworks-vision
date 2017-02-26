import cv2

INTENSITY_THRESHOLD = 254
CONTOUR_SIZE_THRESHOLD = 500
BOILER_TILT_ERROR = 12

def contour_filter(contour):
    return cv2.contourArea(contour) > CONTOUR_SIZE_THRESHOLD

def locate_boiler(contours):
    count = len(contours)
    for i in range(0, count - 1):
        fst_cnt = contours[i]
        fst_leftmost_x = tuple(fst_cnt[fst_cnt[:,:,0].argmin()][0])[0]
        fst_rightmost_x = tuple(fst_cnt[fst_cnt[:,:,0].argmax()][0])[0]
        for j in range(i, count):
            snd_cnt = contours[i]
            snd_leftmost_x = tuple(snd_cnt[snd_cnt[:,:,0].argmin()][0])[0]
            left_error = abs(fst_leftmost_x - snd_leftmost_x)
            if left_error > BOILER_TILT_ERROR: break

            snd_rightmost_x = tuple(snd_cnt[snd_cnt[:,:,0].argmax()][0])[0]
            right_error = abs(fst_rightmost_x - snd_rightmost_x)
            if right_error < BOILER_TILT_ERROR



def run(q):
    while True:
        ir_img, depth_img = q.get()

        ret, ir_img = cv2.threshold(ir_img, INTENSITY_THRESHOLD, 255, cv2.THRESH_BINARY)
        ir_img, contours, heirarchy = cv2.findContours(ir_img, cv2.RETR_LIST)
        contours = filter(contour_filter, contours)
        cv2.imshow('', ir_img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            pass
        q.task_done()
