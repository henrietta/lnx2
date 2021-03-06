package pl.com.henrietta.lnx2;

import java.util.Collection;
import java.util.Vector;
import java.util.HashMap;
import pl.com.henrietta.lnx2.Channel;
import pl.com.henrietta.lnx2.Packet;
import pl.com.henrietta.lnx2.exceptions.*;

/**
 * A LNX2 link between two peers
 */
public class Connection {
	/** Channels present **/
	private HashMap<Integer, Channel> channels;
	private long timeout;
	
	/** Time when a packet was received last */
	private long last_received;
	
	/**
	 * This flag is set to true if a LNX2 channel associated with this connection,
	 * during the course of receiving a packet, declares that it has new data
	 * to read.
	 * 
	 * This flag must be manually unset by whoever takes care of this Connection
	 * object.
	 */
	public boolean has_new_data = false;
	
	/**
	 * Creates a LNX2 connection
	 * @param channels sequence of channels supported by this connection
	 * @param timeout a period of inactivity (no packets received) after 
	 * which the connection will be considered broken
	 */
	public Connection(Vector<Channel> channels, float timeout) {
		this.channels = new HashMap<>();
		for (Channel chan : channels)
			this.channels.put(new Integer(chan.channel_id), chan);
		this.timeout = ((long)(timeout)) * 1000;
		this.last_received = System.currentTimeMillis();		
	}
	
	/** Returns whether connection timeouted */
	public boolean has_timeouted() {
		return (System.currentTimeMillis() - this.last_received) > this.timeout;
	}
	
	/** Called to return a packet to send */
	public Packet on_sendable() throws NothingToSend {
		for (Channel chan : this.channels.values()) {
			try {
				return chan.on_sendable();
			} catch (NothingToSend n) {}
		}
		throw new NothingToSend();
	}
	
	/** 
	 * Called when a packet received. If a packet is received for
	 * channel that does not exist, it is silently dropped
	 */
	public void on_received(Packet p) {
		Channel chan = this.channels.get(new Integer(p.channel_id));
		if (chan != null) 
			if (chan.on_received(p))
				this.has_new_data = true;
		this.last_received = System.currentTimeMillis();
	}
	
	/**
	 * Returns channel of given ID, or null if there's no channel of that ID
	 */
	public Channel getChannel(int id) {
		return this.channels.get(id);
	}

	public Collection<Channel> getChannels() {
		return this.channels.values();
	}	
	
}
