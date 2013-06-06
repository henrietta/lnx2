class LNX2Error(Exception):
    """Generic LNX2 exception"""


class PacketMalformedError(LNX2Error):
    """Packet processed was malformed"""