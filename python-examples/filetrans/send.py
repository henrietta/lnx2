#!/usr/bin/python
import sys, lnx2, socket, threading, time, select, struct

"""
    Invoke:

        ./sent.py target_ip target_port file_to_send

    Keep that file small, it will be loaded into memory
    in full!
"""
# -------- Create socket
ip_addr = sys.argv[1]
ip_port = int(sys.argv[2])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip_addr, 0))

# -------- LNX2 getup
c0 = lnx2.Channel(0, lnx2.RTM_AUTO_ORDERED, 30)
c = lnx2.Connection([c0], 120)
s = lnx2.ClientSocket(sock, (ip_addr, ip_port), c)


with open(sys.argv[3]) as infile:
    indata = infile.read()

c[0].write(bytearray(struct.pack('!L', len(indata))))

# enqueue the file to be sent
while len(indata) > 0:
    ixa = indata[:500]
    indata = indata[500:]

    c[0].write(bytearray(ixa))

while True:
    rs, ws, xs = select.select([sock], [sock], [])

    if len(ws) > 0:
        s.on_sendable()
    if len(rs) > 0:
        s.on_readable()
    if s.check_timeouts(): 
        print 'Timeout'
        break

    if len(c[0].buffer) == 0:
        if len(c[0].packs_in_transit) == 0:
            print 'File sent!'
            break

