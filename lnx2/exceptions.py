class LNX2Error(Exception):
    """Generic LNX2 exception"""

class PacketMalformedError(LNX2Error):
    """Packet processed was malformed"""

class NothingToSend(LNX2Error):
    """There is nothing to send"""

class NothingToRead(LNX2Error):
    """There is nothing to read"""