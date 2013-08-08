So, how do you use LNX2?

A single datagram-based (as LNX2 is application layer, per IP layering) LNX2 connection consists of up to 256 logical channels. A channel is an independent sub-connection with it's own retransmission parameters. The primary parameter you can set is a retransmission mode:

* RTM_NONE: Classic UDP
* RTM_MANUAL: Can be sending only one packet at a time. If packet is not delivered in given time, retransmission will be attempted - but using the current buffer. This is useful for data that changes so frequently, that if a transmission fails, new data can be sent right away, and the old ignored.
* RTM_AUTO: Guaranteed, but not in-order delivery. As soon as a datagram arrives, it is marked as readable by LNX2.
* RTM_AUTO_ORDERED: Guaranteed in-order delivery. LNX2 will stall signalling that there is data to perform reordering.

LNX2 is not stream-oriented, but datagram oriented. Even datagrams sent with RTM_AUTO_ORDERED must keep that in mind. LNX2, as an UDP application, is very light, with only 2 bytes of overhead per UDP packet. Keep in mind that LNX2 datagrams will not be split, so attaching too big ones will result in permanent failure to delivery.

LNX2 does not keep track of connections. You must do that manually.

### Interesting stuff glossary

* _max_bundle_size_ - during RTM_AUTO or RTM_AUTO_ORDERED there can be many packets at-once "on wire" in order to speed up delivery. This value controls how many of these are in. Due to the fact that LNX2 - because of small header size - can track only up to 64 packets alive at one time, this value was arbitrarily limited to 60.

* _retransmission_timeout_ - amount of time in which a LNX2 acknowledge for remote host must be received in order not to schedule a retransmission.