import unittest

from lnx2.packet import Packet
from lnx2.exceptions import PacketMalformedError

class PacketUnitTests(unittest.TestCase):

    def test_serialization(self):
        p = Packet(bytearray('DUPA'), 4, 6)

        self.assertEqual(p.to_bytearray(), bytearray('\x06\x04DUPA'))

        p = Packet.create_ack(4, 6)

        self.assertEqual(p.to_bytearray(), bytearray('\x86\x04'))

    def test_unserialization(self):
        s = bytearray('\x06\x04DUPA')
        p = Packet.from_bytearray(s)

        self.assertEqual(p.channel_id, 4)
        self.assertEqual(p.window_id, 6)        
        self.assertEqual(p.data, bytearray('DUPA'))
        self.assertEqual(p.is_ack, False)


        s = bytearray('\x86\x04')
        p = Packet.from_bytearray(s)

        self.assertEqual(p.channel_id, 4)
        self.assertEqual(p.window_id, 6)        
        self.assertEqual(p.is_ack, True)

        s = bytearray('\x86\x04DUPA')

        self.assertRaises(PacketMalformedError, lambda: Packet.from_bytearray(s))

    def test_equality(self):
        p1 = Packet('DUPA', 4, 2)
        p2 = Packet.from_bytearray('\x02\x04DUPA')

        self.assertEqual(p1.is_equal(p2), True)

        p3 = Packet.create_ack(4, 2)

        self.assertEqual(p1.is_equal(p3), False)