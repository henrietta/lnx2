import unittest

from lnx2 import Channel, RTM_NONE, NothingToRead, NothingToSend, Connection

from time import sleep

class ConnectionUnitTests(unittest.TestCase):

    def test_channels(self):
        alice_0 = Channel(0, RTM_NONE)
        bob_0 = Channel(0, RTM_NONE)

        alice_1 = Channel(1, RTM_NONE)
        bob_1 = Channel(1, RTM_NONE)

        alice = Connection([alice_0, alice_1])
        bob = Connection([bob_0, bob_1])

        alice[0].write(bytearray('DUPA1'))

        pk1 = alice.on_sendable()

        self.assertEquals(pk1.channel_id, 0)

        bob.on_received(pk1)

        self.assertEquals(bob[0].read(), bytearray('DUPA1'))
        self.assertEquals(bob.has_new_data, True)

    def test_misrouting(self):
        alice_0 = Channel(0, RTM_NONE)
        alice_1 = Channel(1, RTM_NONE)
        bob_1 = Channel(1, RTM_NONE)

        alice = Connection([alice_0, alice_1])
        bob = Connection([bob_1])

        alice[0].write(bytearray('DUPA1'))

        pk = alice.on_sendable()

        bob.on_received(pk)

        self.assertRaises(NothingToRead, bob[1].read)
        self.assertEquals(bob.has_new_data, False)

    def test_nothingtosend(self):
        alice_0 = Channel(0, RTM_NONE)
        alice_1 = Channel(1, RTM_NONE)

        alice = Connection([alice_0, alice_1])

        self.assertRaises(NothingToSend, alice.on_sendable)

    def test_timeout(self):
        alice = Connection([], 0.5)
        self.assertEquals(alice.has_timeouted(), False)        
        sleep(0.6)

        self.assertEquals(alice.has_timeouted(), True)     
        self.assertEquals(alice.has_new_data, False) 