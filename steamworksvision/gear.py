
import cv2
import system

INTENSITY_THRESHOLD = 254
CONTOUR_SIZE_THRESHOLD = 500
TARGET_TILT_ERROR = 12

DEBUG = 'debug' in system.argv

def contour_filter(contour):
    return cv2.contourArea(contour) > CONTOUR_SIZE_THRESHOLD

def locate_peg(contours):
    count = len(contours)
    for i in range(0, count - 1):
        fst_cnt = contours[i]
        fst_topmost_y = tuple(fst_cnt[fst_cnt[:,:,1].argmin()][0])[1]
        fst_bottommost_y = tuple(fst_cnt[fst_cnt[:,:,1].argmax()][0])[1]

        for j in range(i, count):
            snd_cnt = contours[i]
            snd_topmost_y = tuple(snd_cnt[snd_cnt[:,:,1].argmin()][0])[1]
            top_error = abs(fst_topmost_y - snd_topmost_y)
            if top_error > TARGET_TILT_ERROR: continue

            snd_bottommost_y = tuple(snd_cnt[snd_cnt[:,:,1].argmax()][0])[1]
            bottom_error = abs(fst_bottommost_y - snd_bottomost_y)
            if bottom_error <= TARGET_TILT_ERROR:
                fst_leftmost_x = tuple(fst_cnt[fst_cnt[:,:,0].argmin()][0])[0]
                fst_rightmost_x = tuple(fst_cnt[fst_cnt[:,:,0].argmax()][0])[0]

                return (fst_leftmost_x + fst_rightmost_x) / 2
    return None

last_image_number = 0
def run(in_q, out_q):
    global last_image_number
    while True:
        image_number, ir_img, depth_img = in_q.get()
        if last_image_number <= image_number: continue
        last_image_number = image_number

        ret, ir_img = cv2.threshold(ir_img, INTENSITY_THRESHOLD, 255, cv2.THRESH_BINARY)
        ir_img, contours, heirarchy = cv2.findContours(ir_img, cv2.RETR_LIST)
        contours = filter(contour_filter, contours)

        target = locate_boiler(contours)

        if DEBUG:
            cv2.imshow('', ir_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                pass

        out_q.put('PEG-{}-{}-0'.format(image_number, target))
