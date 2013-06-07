#!/usr/bin/python
import sys, lnx2, socket, threading, time, select, struct

"""
    Invoke:

        ./receive.py target_ip target_port save_as_path

    Keep that file small, it will be loaded into memory
    in full!
"""
# -------- Create socket
ip_addr = sys.argv[1]
ip_port = int(sys.argv[2])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip_addr, ip_port))

# -------- LNX2 getup

def on_connected(addr):
    c0 = lnx2.Channel(0, lnx2.RTM_AUTO_ORDERED, 30)
    return [c0], 50

def on_disconnected(addr, conn):
    pass

s = lnx2.ServerSocket(sock, on_connected, on_disconnected)

filedata = bytearray()
filelen = None

fixed_connection = None


exit_loop_on = None

while True:
    rs, ws, xs = select.select([sock], [sock], [])

    if len(ws) > 0:
        s.on_sendable()
    if len(rs) > 0:
        s.on_readable()
    if s.check_timeouts():
        print 'Timeouted'
        break

    if (fixed_connection == None) and (len(s.connections) == 1):
        # connection found, hey!
        fixed_connection = s.connections.itervalues().next()

    if exit_loop_on != None:
        if time.time() > exit_loop_on:
            break

    if fixed_connection != None:
        try:
            p = fixed_connection[0].read()
        except lnx2.NothingToRead:
            continue

        if filelen == None:
            filelen, = struct.unpack('!L', str(p))
        else:
            filedata.extend(p)

        if len(filedata) == filelen:
            print 'File received, exiting in 5s'
            with open(sys.argv[3], 'wb') as y:
                y.write(filedata)
            exit_loop_on = time.time() + 5


            


