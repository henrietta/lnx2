from lnx2.connection import Connection
from lnx2.packet import Packet

from lnx2.exceptions import NothingToSend, NothingToRead, \
                            PacketMalformedError


class ClientSocket(object):
    """Wrapper around client (uniconnection) UDP socket
    providing LNX2 connectivity"""
    def __init__(self, socket, target_addr, connection):
        """
        @param socket: UDP socket
        @param target_addr: target of remote LNX2 peer
        @param connection: connection to support
        @type connection: L{lnx2.Connection}
        """
        self.socket = socket
        self.target_addr = target_addr
        self.connection = connection

    def on_readable(self):
        """Call when socket is readable, or needs to read (if blocking)"""
        data, addr = self.socket.recvfrom(1024)

        if addr != self.target_addr: return  # who sent that?

        data = bytearray(data)

        try:
            pkt = Packet.from_bytearray(data)
        except PacketMalformedError:
            pass

        self.connection.on_received(pkt)

    def on_sendable(self):
        """Call when socket is writable, or needs to send (if blocking).
        A single packet will be sent."""
        try:
            pkt = self.connection.on_sendable()
        except NothingToSend:
            return

        pkts = pkt.to_bytearray()
        self.socket.sendto(pkts, self.target_addr)

    def check_timeouts(self):
        """Returns whether this connection has timed out
        @return: bool"""
        return self.connection.has_timeouted()

class ServerSocket(object):
    """Wrapper around server (multiconnection) UDP socket
    providing LNX2 connectivity"""
    def __init__(self, socket, 
                        on_connected = lambda addr: None,
                        on_closed = lambda addr, connection: None):
        """
        @param socket: an UDP socket
        @param on_connected: callable/1 to call when new connection
            is detected. It's address will be passed along.
            This callable will be expected to return full set of
            parameters to pass to Connection's constructor!
        @param on_closed: callable/2 to call when connection
            has timed out or been closed. It's address and connection
            will be passed along
        """
        self.connections = {}   # address => Connection
        self.socket = socket
        self.on_closed = on_closed
        self.on_connected = on_connected


    def on_readable(self):
        """Call when socket is readable, or needs to read (if blocking)"""
        data, addr = self.socket.recvfrom(1024)
        data = bytearray(data)
        try:
            pkt = Packet.from_bytearray(data)
        except PacketMalformedError:
            pass

        if addr in self.connections:
            self.connections[addr].on_received(pkt)
        else:
            connargs = self.on_connected(addr)
            self.connections[addr] = Connection(*connargs)
            self.connections[addr].on_received(pkt)

    def on_sendable(self):
        """Call when socket is writable, or needs to send (if blocking).
        A single packet will be sent."""
        for addr, connection in self.connections.iteritems():
            try:
                pkt = connection.on_sendable()
            except NothingToSend:
                continue

            pkts = pkt.to_bytearray()
            self.socket.sendto(pkts, addr)
            return

    def check_timeouts(self):
        """Orders the socket to check timeouts"""
        for addr, connection in self.connections.iteritems():
            if connection.has_timeouted():
                self.on_closed(addr, connection)
                del self.connections[addr]
                return