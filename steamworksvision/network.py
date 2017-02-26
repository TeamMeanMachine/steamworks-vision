import socket

DEBUG = 'debug' in system.argv

IP = 'roborio-2471-frc.local'
PORT = 5800

def run(q):
    socket = socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        message = q.get()
        socket.sendto(message, (IP, PORT))
