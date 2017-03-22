import socket
import sys

from networktables import NetworkTables

IP = 'roborio-2471-frc.local'
PORT = 5800

NetworkTables.initialize(server=IP)

network_table = NetworkTables.getTable('Vision')

DEBUG = 'debug' in sys.argv and 'network' in sys.argv

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def run(in_q, out_q):
    global sock, IP, PORT

    while True:
        message = out_q.get()
        if DEBUG:
            print(message)
        raw_message = message.encode('ascii')
        try:
            sock.sendto(raw_message, (IP, PORT))
        except:
            if DEBUG:
                print('Failed to send packet to roborio')
