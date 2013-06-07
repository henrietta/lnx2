import struct

from lnx2.exceptions import PacketMalformedError

class Packet(object):
    """A LNX2 packet"""
# --------------------------------- constructors

    def __init__(self, data, channel_id, window_id):
        """
        @type data: bytearray
        @type channel_id: int
        @type window_id: int
        """
        self.data = data
        self.channel_id = channel_id
        self.window_id = window_id

        self.is_ack = False

    @staticmethod
    def create_ack(channel_id, window_id):
        """Creates an ACK packet"""
        x = Packet(bytearray(), channel_id, window_id)
        x.is_ack = True
        return x

    @staticmethod
    def from_bytearray(data):
        """Creates a packet from received data - including header"""

        try:
            fhb, channel_id = struct.unpack('!BB', str(data[0:2]))
        except struct.error:
            raise PacketMalformedError, 'too short'

        rest_of_pack = data[2:]

        window_id = fhb & 63     # Lower 6 bits

        is_ack = bool(fhb & 128)
        is_spc = bool(fhb & 64)

        if is_ack:      # Acknowledgement
            if len(rest_of_pack) > 0:
                raise PacketMalformedError, 'ACK received but body not empty'

            return Packet.create_ack(channel_id, window_id)
        elif is_spc:    # Special packet
            raise PacketMalformedError, 'SPC not supported in this LNX2 revision'

        else:           # Data packet
            return Packet(rest_of_pack, channel_id, window_id)


# --------------------------------- processors

    def to_bytearray(self):
        """
        Converts this packet to a bytearray

        @return: bytearray of packet + header
        """
        fhb = self.window_id + (int(self.is_ack) << 7)

        header = bytearray(struct.pack('!BB', fhb, self.channel_id))

        return header + self.data


    def is_equal(self, pack):
        """
        Check whether packets match exactly. Equality operator is not overloaded,
        because some may check for the same object instead.

        @type pack: Packet
        """

        return (self.is_ack == pack.is_ack) and (self.data == pack.data) and \
         (self.window_id == pack.window_id) and (self.channel_id == pack.channel_id) 