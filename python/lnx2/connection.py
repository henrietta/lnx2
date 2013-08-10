import time

from lnx2.exceptions import NothingToRead, NothingToSend

class Connection(object):
    """A LNX2 link between two peers"""

    def __init__(self, channels, timeout=10000):
        """
        Creates a LNX2 link

        @param channels: sequence of L{lnx2.Channel}
            supported by this protocol realization
        @param timeout: a period of inactivity (no packets received)
            after which connection will be considered broken
        """
        self.channels = {}
        for channel in channels:
            self.channels[channel.channel_id] = channel

        self.last_reception_on = time.time()    # time something was last
                                                # received
        self.timeout = timeout
        self.has_new_data = False 

    def has_timeouted(self):
        """Returns whether connection timeouted"""
        return time.time() - self.last_reception_on > self.timeout

    def on_sendable(self):
        """
        Called to return a packet to send

        Returns a L{lnx2.Packet} or raises NothingToSend
        if there's nothing to send

        @return: L{lnx2.Packet}
        """
        for channel in self.channels.itervalues():
            try:
                return channel.on_sendable()
            except NothingToSend:
                continue

        raise NothingToSend

    def on_received(self, packet):
        """
        Called when a packet arrives.
        This will set local flag .has_new_data to True if any of the channels
        has new data to read. You must unset this flag yourself later.
        This flag will be a instance variable 'has_new_data'

        @type packet: L{lnx2.Packet}
        """
        try:
            if self.channels[packet.channel_id].on_received(packet):
                self.has_new_data = True
        except KeyError:
            # we don't support this channel on this realization
            # silently drop the packet
            pass

        self.last_reception_on = time.time()

    def __getitem__(self, channel_id):
        return self.channels[channel_id]

    def get_channels(self):
        """Return a iterator of Channel objects 
        registered for this connection"""
        return self.channels.itervalues()