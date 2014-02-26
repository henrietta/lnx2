import unittest

from lnx2 import Packet, PacketMalformedError, Channel, RTM_NONE, \
                 RTM_MANUAL, RTM_AUTO, RTM_AUTO_ORDERED, \
                 NothingToRead, NothingToSend

from time import sleep
from random import randint

class ChannelUnitTests(unittest.TestCase):

    def test_RTM_NONE(self):
        alice_0 = Channel(0, RTM_NONE)
        bob_0 = Channel(0, RTM_NONE)

        alice_0.write(bytearray('DUPA'))

        pk = alice_0.on_sendable()

        bob_0.on_received(pk)

        self.assertEquals(bob_0.read(), bytearray('DUPA'))

    def test_RTM_MANUAL_normalsend(self):
        alice_0 = Channel(0, RTM_MANUAL)
        bob_0 = Channel(0, RTM_MANUAL)

        alice_0.write(bytearray('DUPA'))
        pk = alice_0.on_sendable()

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

        sleep(0.6)

        pk = alice_0.on_sendable()

        bob_0.on_received(pk)

        ack = bob_0.on_sendable()
        self.assertEquals(ack.is_ack, True)

        alice_0.on_received(ack)

        self.assertEquals(alice_0.is_tx_in_progress(), False)

    def test_RTM_MANUAL_duplication(self):
        pk = Packet(bytearray('DUPA'), 0, 0)

        bob_0 = Channel(0, RTM_MANUAL)

        bob_0.on_received(pk)
        bob_0.on_received(pk)

        self.assertEquals(bob_0.read(), bytearray('DUPA'))        
        self.assertRaises(NothingToRead, bob_0.read)

    def test_RTM_MANUAL_ackduplication(self):
        alice_0 = Channel(0, RTM_MANUAL)
        bob_0 = Channel(0, RTM_MANUAL)

        alice_0.write(bytearray('DUPA'))
        pk = alice_0.on_sendable()

        bob_0.on_received(pk)

        self.assertEquals(bob_0.read(), bytearray('DUPA'))

        ack = bob_0.on_sendable()
        self.assertEquals(ack.is_ack, True)

        alice_0.on_received(ack)
        alice_0.on_received(ack)

        self.assertEquals(alice_0.is_tx_in_progress(), False)
        
    def test_RTM_MANUAL_more64randomed(self):
        alice_0 = Channel(0, RTM_MANUAL)
        bob_0 = Channel(0, RTM_MANUAL)
        
        for i in xrange(0, 500):
            dts = bytearray([randint(0, 255) for x in xrange(0, 20)])
            alice_0.write(dts)
            p = alice_0.on_sendable()
            bob_0.on_received(p)
            alice_0.on_received(bob_0.on_sendable())
            
            self.assertEquals(bob_0.read(), dts)

    def test_RTM_MANUAL_more64(self):
        alice_0 = Channel(0, RTM_MANUAL)
        bob_0 = Channel(0, RTM_MANUAL)
        
        dts = bytearray([randint(0, 255) for x in xrange(0, 20)])
        
        for i in xrange(0, 500):
            alice_0.write(dts)
            p = alice_0.on_sendable()
            bob_0.on_received(p)
            alice_0.on_received(bob_0.on_sendable())
            
            self.assertEquals(bob_0.read(), dts)
            
            
    def test_RTM_MANUAL_handover(self):
        """Tests an in-transmission packet content change"""
        alice_0 = Channel(0, RTM_MANUAL, 0.5)
        bob_0 = Channel(0, RTM_MANUAL, 0.5)

        alice_0.write(bytearray('DUPA'))
        pk = alice_0.on_sendable()

        sleep(0.6)

        alice_0.write(bytearray('STEFAN'))

        pk = alice_0.on_sendable()

        bob_0.on_received(pk)

        ack = bob_0.on_sendable()
        self.assertEquals(ack.is_ack, True)

        alice_0.on_received(ack)

        self.assertEquals(alice_0.is_tx_in_progress(), False)
        self.assertEquals(bob_0.read(), bytearray('STEFAN'))

    def test_RTM_AUTO_normalsend(self):
        alice_0 = Channel(0, RTM_AUTO)
        bob_0 = Channel(0, RTM_AUTO)

        alice_0.write(bytearray('DUPA'))
        pk = alice_0.on_sendable()

        bob_0.on_received(pk)

        self.assertEquals(bob_0.read(), bytearray('DUPA'))

        ack = bob_0.on_sendable()
        self.assertEquals(ack.is_ack, True)

        alice_0.on_received(ack)

        self.assertEquals(alice_0.is_tx_in_progress(), False)

    def test_RTM_AUTO_ackduplication(self):
        alice_0 = Channel(0, RTM_AUTO)
        bob_0 = Channel(0, RTM_AUTO)

        alice_0.write(bytearray('DUPA'))
        pk = alice_0.on_sendable()
        self.assertEquals(alice_0.is_tx_in_progress(), True)

        bob_0.on_received(pk)

        self.assertEquals(bob_0.read(), bytearray('DUPA'))

        ack = bob_0.on_sendable()
        self.assertEquals(ack.is_ack, True)

        alice_0.on_received(ack)
        alice_0.on_received(ack)

        self.assertEquals(alice_0.is_tx_in_progress(), False)

    def test_RTM_AUTO_resend(self):
        alice_0 = Channel(0, RTM_AUTO, 0.5)
        bob_0 = Channel(0, RTM_AUTO, 0.5)

        alice_0.write(bytearray('DUPA'))
        pk = alice_0.on_sendable()

        sleep(0.6)

        pk = alice_0.on_sendable()
        self.assertEquals(alice_0.is_tx_in_progress(), True)

        bob_0.on_received(pk)

        ack = bob_0.on_sendable()
        self.assertEquals(ack.is_ack, True)

        alice_0.on_received(ack)

        self.assertEquals(alice_0.is_tx_in_progress(), False)

    def test_RTM_AUTO_duplication(self):
        pk = Packet(bytearray('DUPA'), 0, 0)

        bob_0 = Channel(0, RTM_AUTO)

        bob_0.on_received(pk)
        bob_0.on_received(pk)

        self.assertEquals(bob_0.read(), bytearray('DUPA'))        
        self.assertRaises(NothingToRead, bob_0.read)

    def test_RTM_AUTO_bundle_control_1(self):
        alice_0 = Channel(0, RTM_AUTO, 0.5, 2)
        bob_0 = Channel(0, RTM_AUTO, 0.5, 2)

        alice_0.write(bytearray('DUPA1'))
        alice_0.write(bytearray('DUPA2'))
        alice_0.write(bytearray('DUPA3'))

        pk1 = alice_0.on_sendable()
        pk2 = alice_0.on_sendable()

        self.assertRaises(NothingToSend, alice_0.on_sendable)

        bob_0.on_received(pk2)
        ack_win2 = bob_0.on_sendable()
        self.assertEquals(ack_win2.is_ack, True)
        self.assertEquals(ack_win2.window_id, 1)

        alice_0.on_received(ack_win2)    # Alice receives ACK for DUPA2

        self.assertEquals(bob_0.read(), bytearray('DUPA2'))

        self.assertRaises(NothingToSend, alice_0.on_sendable)
        # it is forbidden to send DUPA3 now because DUPA1
        # has not been acknowledged and max bundle size is 2

    def test_RTM_AUTO_bundle_control_2(self):
        alice_0 = Channel(0, RTM_AUTO, 0.5, 2)
        bob_0 = Channel(0, RTM_AUTO, 0.5, 2)

        alice_0.write(bytearray('DUPA1'))
        alice_0.write(bytearray('DUPA2'))
        alice_0.write(bytearray('DUPA3'))

        pk1 = alice_0.on_sendable()
        pk2 = alice_0.on_sendable()

        self.assertRaises(NothingToSend, alice_0.on_sendable)

        bob_0.on_received(pk1)
        ack_win1 = bob_0.on_sendable()
        self.assertEquals(ack_win1.is_ack, True)
        self.assertEquals(ack_win1.window_id, 0)

        alice_0.on_received(ack_win1)    # Alice receives ACK for DUPA2

        self.assertEquals(bob_0.read(), bytearray('DUPA1'))

        pk3 = alice_0.on_sendable()
        self.assertEquals(pk3.data, bytearray('DUPA3'))
        # it is allowed to send DUPA3, because DUPA1 was confirmed

    def test_RTM_AUTO_ORDER_reordering(self):
        alice_0 = Channel(0, RTM_AUTO_ORDERED, 0.5, 5)
        bob_0 = Channel(0, RTM_AUTO_ORDERED, 0.5, 5)

        alice_0.write(bytearray('DUPA1'))
        alice_0.write(bytearray('DUPA2'))
        alice_0.write(bytearray('DUPA3'))

        dupa1 = alice_0.on_sendable()
        dupa2 = alice_0.on_sendable()
        dupa3 = alice_0.on_sendable()

        bob_0.on_received(dupa3)

        self.assertRaises(NothingToRead, bob_0.read)

        bob_0.on_received(dupa2)

        self.assertRaises(NothingToRead, bob_0.read)

        bob_0.on_received(dupa1)

        self.assertEquals(bob_0.read(), bytearray('DUPA1'))
        self.assertEquals(bob_0.read(), bytearray('DUPA2'))
        self.assertEquals(bob_0.read(), bytearray('DUPA3'))

