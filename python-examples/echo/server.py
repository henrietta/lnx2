#!/usr/bin/python
import sys, lnx2, socket, threading, time, select

"""
    Invoke:

        ./server.py bind_ip bind_port
"""
# -------- Create socket
ip_addr = sys.argv[1]
ip_port = int(sys.argv[2])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip_addr, ip_port))

# -------- LNX2 getup
def on_connected(addr):
    c0 = lnx2.Channel(0, lnx2.RTM_AUTO_ORDERED, 2)
    print 'Connected %s' % (addr, )
    return [c0], 120

def on_disconnected(addr, connection):
    print 'Disconnected %s' % (addr, )

s = lnx2.ServerSocket(sock, on_connected, on_disconnected)

while True:
    time.sleep(0.2)
    rs, ws, xs = select.select([sock], [sock], [])
    if len(rs) > 0: s.on_readable()
    if len(ws) > 0: s.on_sendable()
    s.check_timeouts()

    for addr, connection in s.connections.iteritems():
        try:
            p = connection[0].read()
        except lnx2.NothingToRead:
            continue

        print 'Received %s from %s' % (p, addr)

        connection[0].write(p)