import socket
import sys

IP = 'roborio-2471-frc.local'
PORT = 5800

DEBUG = 'debug' in sys.argv and 'network' in sys.argv

def run(q):
    global IP, PORT
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        message = q.get()
        if DEBUG:
            print(message)
        try:
            pass#sock.sendto(message, (IP, PORT))
        except:
            pass
