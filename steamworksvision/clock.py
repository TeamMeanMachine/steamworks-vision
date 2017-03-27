from time import time
import socket
import struct

from threading import Thread

offset = None

def run(ip, port):
    global offset
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', port))
    while True:
        best_rtt = None
        best_end_time = None

        for _ in range(5):
            start_time = time()
            sock.sendto(bytearray([0, 0, 0, 0, 0, 0, 0, 0]), (ip, port))
            data, _ = sock.recvfrom(8)
            end_time = time()
            rtt = end_time - start_time
            # take best sample (lowest round trip time)
            if not rtt or rtt < best_rtt:
                best_rtt = rtt
                best_end_time = end_time
                server_time = struct.unpack('d', data)
                samples.append((rtt, server_time))

        offset = best_server_time + (best_rtt / 2)
        time.sleep(10)
    pass

def init(ip, port):
    t = Thread(target = run, args=(ip, port))
    t.daemon = True
    t.start()

def time():
    global offset
    if offset:
        return time() - offset
    else:
        return 0
