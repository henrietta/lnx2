import time, collections

from lnx2.exceptions import LNX2Error, PacketMalformedError, \
                            NothingToRead, NothingToSend
from lnx2.packet import Packet

RTM_NONE = 0
RTM_MANUAL = 1
RTM_AUTO = 2
RTM_AUTO_ORDERED = 3

class Channel(object):
    """A single LNX2 channel"""

    def __init__(self, channel_id,
                       retransmission_mode=RTM_NONE, 
                       retransmission_timeout=60,
                       max_bundle_size=20):
        """
        Initializes a LNX2 channel

        @param channel_id: this channel ID
        @param retransmission_mode: specifies retransmission behaviour
        @param retransmission_timeout: number of seconds after which delivery
            will be retried
        @param max_bundle_size: maximum amount of window IDs in use in a single
            moment. Maximum is 60.
        """
        self.retransmission_mode = retransmission_mode
        self.retransmission_timeout = retransmission_timeout
        self.channel_id = channel_id

        if max_bundle_size > 60:
            raise ValueError, 'Invalid max bundle size'

        self.max_bundle_size = max_bundle_size


        self.buffer = collections.deque()

        self.holding_buffer = {} # for received packets, window ID => data::Packet

        self.next_send_window_id = 0 # identifier of next window ID to send
        self.next_expc_window_id = 0 # identifier of next window ID to receive

        self.packs_in_transit = {}  # for unACKed, but sent, packets
                                    # window ID => (time_last_resent::float, 
                                    #               data::Packet)

        self.reassemble_buffer = {} # for reordering data in RTM_AUTO_ORDERED
                                    # window ID => data::Packet

        self.tx_requests = collections.deque()  # plain 

        self.data_to_read = collections.deque() # data available for user to read

    def write(self, data):
        """
        Arranges to have data sent.

        @type data: str or bytearray
        """
        data = bytearray(data)

        if self.retransmission_mode == RTM_NONE:
            self.tx_requests.appendleft(Packet(data, self.channel_id, 0))

        elif self.retransmission_mode in (RTM_AUTO, RTM_AUTO_ORDERED):
            self.buffer.appendleft(data)

        elif self.retransmission_mode == RTM_MANUAL:
            self.buffer.clear()
            self.buffer.appendleft(data)

        else:
            raise LNX2Exception, 'Invalid retransmission mode'


    def read(self):
        """
        Reads a piece of data

        Returns a bytearray of data is present or raises
        L{lnx2.NothingToRead} if there's nothing to read
        @return: bytearray
        """
        try:
            return self.data_to_read.pop()
        except IndexError:
            raise NothingToRead

    def _enq_ack(self, window_id):
        """Enqueues an ACK packet to be sent in output buffer"""
        ackp = Packet.create_ack(self.channel_id, window_id)
        self.tx_requests.appendleft(ackp)


    def on_sendable(self):
        """
        Called when something can be sent. 

        Returns a packet when it wants something to be sent,
        or raises L{lnx2.NothingToSend} if nothing is to be sent

        @return: L{lnx2.Packet}
        """
        # tx_requests take precedence
        # RTM_NONE write()s directly to tx_requests
        if len(self.tx_requests) > 0:
            return self.tx_requests.pop()

        if self.retransmission_mode == RTM_MANUAL:
            # Two cases are possible: either a new packet
            # can be dispatched, or retransmission should be considered

            if len(self.packs_in_transit) == 0:
                # It seems that a new packet can be sent

                if len(self.buffer) == 0:
                    # There's nothing to send
                    raise NothingToSend

                # A packet can be sent
                data = self.buffer.pop()
                pk = Packet(data, self.channel_id, self.next_send_window_id)
                self.next_send_window_id = (self.next_send_window_id + 1) % 64
                self.packs_in_transit[pk.window_id] = time.time(), pk
                return pk

            else:   
                # Consider a retransmission
                ctime = time.time()

                time_sent, pack = self.packs_in_transit.itervalues().next()
                if ctime - time_sent > self.retransmission_timeout:
                    # Yes, a retransmission is in works
                    if len(self.buffer) > 0:
                        # User ordered a change to packet in meantime
                        pack = Packet(self.buffer.pop(), \
                                      self.channel_id, pack.window_id)

                    self.packs_in_transit[pack.window_id] = ctime, pack
                    return pack

                raise NothingToSend     # no retransmission needed

        elif self.retransmission_mode in (RTM_AUTO, RTM_AUTO_ORDERED):
            if len(self.buffer) > 0:
                # We can consider sending a new packet
                if len(self.packs_in_transit) < self.max_bundle_size:
                    # We seem to be allowed to sent a new packet
                    nwid = self.next_send_window_id

                    # Check if there's an unsent window ID that has not
                    # been confirmed
                    naxid = nwid - self.max_bundle_size
                    if naxid < 0: naxid += 64

                    if naxid not in self.packs_in_transit:
                        # there are no missing windows. Go on.
                        self.next_send_window_id = (self.next_send_window_id + 1) % 64

                        pk = Packet(self.buffer.pop(), self.channel_id, nwid)
                        self.packs_in_transit[nwid] = time.time(), pk
                        return pk

            ctime = time.time()
            # Check for retransmissions then
            for time_sent, pack in self.packs_in_transit.itervalues():
                if ctime - time_sent > self.retransmission_timeout:
                    # A retransmission needs to be made
                    self.packs_in_transit[pack.window_id] = ctime, pack
                    return pack

        raise NothingToSend


    def is_tx_in_progress(self):
        """Checks whether there are any unacknowledged packets or any
        data to send.
        @return: true if there are any unACKed packets or tx buffers not empty"""
        return (len(self.packs_in_transit) > 0) or (len(self.buffer) > 0) or \
               (len(self.tx_requests) > 0)

    def on_received(self, packet):
        """
        Signal from upper layer that a data package was received.
        Data may be available to read after this

        @type packet: L{lnx2.packet.Packet}
        """

        if packet.is_ack:       # -------------- This is an ACK
            if packet.window_id in self.packs_in_transit:
                # Acknowledgement for a real packet that we sent
                # earlier. Dequeue it from holding buffer
                del self.packs_in_transit[packet.window_id]

                if self.retransmission_mode in (RTM_AUTO, RTM_AUTO_ORDERED):
                    # Those may need to flush their holding_buffer to
                    # prevent it from overflowing

                    ind_to_flush = packet.window_id - self.max_bundle_size
                    if ind_to_flush < 0:
                        ind_to_flush += 64

                    try:
                        del self.holding_buffer[ind_to_flush]
                    except KeyError:
                        pass
            return

                                # -------------- Not an ACK

        try:
            rcd = self.holding_buffer[packet.window_id]
        except KeyError:
            pass
        else:
            # RTM_NONE couldn't care less
            # All retransmissions in RTM_MANUAL are important, as they
            # may contain fresh data. Verify if that's the case..
            # Both RTM_AUTO and RTM_AUTO_ORDERED care a lot about packets
            if rcd.is_equal(packet):
                # this is a plain retransmission. Enqueue an ACK
                self._enq_ack(packet.window_id)
                return

        # This is not a retransmission, this is a new packet
        if self.retransmission_mode == RTM_NONE:
            self.data_to_read.appendleft(packet.data)

        elif self.retransmission_mode in (RTM_MANUAL, RTM_AUTO):
            self.data_to_read.appendleft(packet.data)
            self._enq_ack(packet.window_id)

            self.holding_buffer[packet.window_id] = packet

        else:   # RTM_AUTO_ORDERED
            self._enq_ack(packet.window_id)
            self.reassemble_buffer[packet.window_id] = packet

            if self.next_expc_window_id == packet.window_id:
                # this is the next expected packet. Perform reassemblage
                while self.next_expc_window_id in self.reassemble_buffer:
                    pfb = self.reassemble_buffer[self.next_expc_window_id]
                    del self.reassemble_buffer[self.next_expc_window_id]

                    self.data_to_read.appendleft(pfb.data)

                    self.next_expc_window_id = (self.next_expc_window_id + 1) % 64
