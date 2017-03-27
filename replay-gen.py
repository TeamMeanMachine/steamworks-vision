import argparse
import cv2
import numpy as np
from steamworksvision.boiler import process as process_boiler

parser = argparse.ArgumentParser(description='Create a replay')
parser.add_argument('input', help='Directory containing video files from a match')
parser.add_argument('--out', '-o', help='Location of output video file', metavar='dir')

args = parser.parse_args()

in_dir = args.input
out_file = args.out

color_cap = cv2.VideoCapture('{}/color.avi'.format(in_dir))
ir_cap = cv2.VideoCapture('{}/infrared.avi'.format(in_dir))
depth_cap = cv2.VideoCapture('{}/depth.avi'.format(in_dir))
feed_cap = cv2.VideoCapture('{}/feed.avi'.format(in_dir))

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out_stream = cv2.VideoWriter(out_file, fourcc, 25.0, (1920, 1080))

while color_cap.isOpened() and ir_cap.isOpened() and depth_cap.isOpened() and feed_cap.isOpened():
    color_ret, color_frame = color_cap.read()
    ir_ret, ir_frame = ir_cap.read()
    depth_ret, depth_frame = depth_cap.read()
    feed_ret, feed_frame = feed_cap.read()

    if color_ret == False or ir_ret == False or depth_ret == False or feed_ret == False:
        break

    shrinked_color_frame = cv2.resize(color_frame, (640, 480), interpolation = cv2.INTER_AREA)

    assert color_frame.shape == (1080, 1920, 3)
    assert shrinked_color_frame.shape == (480, 360, 3)
    assert ir_frame.shape == (480, 360, 3)
    assert depth_frame.shape == (480, 360, 3)
    assert feed_frame.shape == (480, 360, 3)

    boiler_data, boiler_img = process_boiler(ir_frame)
    gear_img = np.zeros((360, 480, 3), np.uint8)
    rope_img = np.zeros((360, 480, 3), np.uint8)

    out_frame_top = np.concatenate(feed_frame, ir_frame, shrinked_color_frame, axis = 0)
    out_frame_bottom = np.concatenate(boiler_img, gear_img, rope_img, axis = 0)

    filler = np.zeros((120, 1920, 3), np.uint8)

    out_frame = np.concatenate(out_frame_top, out_frame_bottom, filler, axis = 1)

color_cap.release()
ir_cap.release()
depth_cap.release()
feed_cap.release()

out_stream.release()

