import argparse

parser = argparse.ArgumentParser(description='Create a replay')
parser.add_argument('input', help='Directory containing video files from a match')
parser.add_argument('--output', '-o', help='Location of output video file')

print(parser.parse_args())

