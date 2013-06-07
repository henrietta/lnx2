#!/usr/bin/python
import sys, lnx2, socket, threading, time, select

"""
    Invoke:

        ./client.py target_ip target_port
"""
# -------- Create socket
ip_addr = sys.argv[1]
ip_port = int(sys.argv[2])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 0))

# -------- LNX2 getup
c0 = lnx2.Channel(0, lnx2.RTM_AUTO_ORDERED, 2)
c = lnx2.Connection([c0], 120)
s = lnx2.ClientSocket(sock, (ip_addr, ip_port), c)

class MessageListener(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while not s.check_timeouts():
            time.sleep(0.2)
            rs, ws, xs = select.select([sock], [sock], [])

            if len(ws) > 0:
                s.on_sendable()
            if len(rs) > 0:
                s.on_readable()

            try:
                dat = c[0].read()
            except lnx2.NothingToRead:
                continue
            else:
                print 'Received: %s' % dat

MessageListener().start()
while True:
    line = raw_input()
    c[0].write(bytearray(line))
