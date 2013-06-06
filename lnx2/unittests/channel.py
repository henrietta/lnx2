import unittest

from lnx2 import Packet, PacketMalformedError, Channel, RTM_NONE, \
                 RTM_MANUAL, RTM_AUTO, RTM_AUTO_ORDERED

from time import sleep

class ChannelUnitTests(unittest.TestCase):

    def test_RTM_NONE(self):
        alice_0 = Channel(0, RTM_NONE)
        bob_0 = Channel(0, RTM_NONE)

        alice_0.write(bytearray('DUPA'))

        pk = alice_0.on_sendable()

        self.assertEquals(isinstance(pk, Packet), True)

        bob_0.on_received(pk)

        self.assertEquals(bob_0.read(), bytearray('DUPA'))

    def test_RTM_MANUAL_normalsend(self):
        alice_0 = Channel(0, RTM_MANUAL)
        bob_0 = Channel(0, RTM_MANUAL)

        alice_0.write(bytearray('DUPA'))
        pk = alice_0.on_sendable()

        self.assertEquals(isinstance(pk, Packet), True)

        bob_0.on_received(pk)

        self.assertEquals(bob_0.read(), bytearray('DUPA'))

        ack = bob_0.on_sendable()
        self.assertEquals(ack.is_ack, True)

        alice_0.on_received(ack)

        self.assertEquals(len(alice_0.packs_in_transit), 0)


    def test_RTM_MANUAL_resend(self):
        alice_0 = Channel(0, RTM_MANUAL, 0.5)
        bob_0 = Channel(0, RTM_MANUAL, 0.5)

        alice_0.write(bytearray('DUPA'))
        pk = alice_0.on_sendable()
        self.assertEquals(isinstance(pk, Packet), True)

        sleep(0.6)

        pk = alice_0.on_sendable()
        self.assertEquals(isinstance(pk, Packet), True)

        bob_0.on_received(pk)

        ack = bob_0.on_sendable()
        self.assertEquals(ack.is_ack, True)

        alice_0.on_received(ack)

        self.assertEquals(len(alice_0.packs_in_transit), 0)

    def test_RTM_MANUAL_duplication(self):
        pk = Packet(bytearray('DUPA'), 0, 0)

        bob_0 = Channel(0, RTM_MANUAL)

        bob_0.on_received(pk)
        bob_0.on_received(pk)

        self.assertEquals(bob_0.read(), bytearray('DUPA'))        
        self.assertEquals(bob_0.read(), None)