package tests;
import static org.junit.Assert.*;

import org.junit.Test;

import pl.com.henrietta.lnx2.Packet;
import pl.com.henrietta.lnx2.exceptions.PacketMalformedError;
import java.util.Arrays;

public class packettest {
	private byte[] test_data = {0, 1, 2, 3};
	
	@Test
	public void testSerialization() {
		
		Packet p = new Packet(this.test_data, (byte)4, (byte)6);
		byte[] should_be = {6, 4, 0, 1, 2, 3};
		
		if (!Arrays.equals(p.to_bytes(), should_be))
			fail("Serialization failed");
	}
		
	@Test
	public void testUnserialization() throws PacketMalformedError {
		// ------- test a packet with data
		byte[] data_packet_src = {6, 4, 0, 1, 2, 3};
		
		Packet data_packet = null;
		data_packet = Packet.from_bytes(data_packet_src);

		if (!Arrays.equals(data_packet.data, this.test_data)) fail("Data mismatch");
		if (data_packet.window_id != (byte)6) fail("Window mismatch");
		if (data_packet.channel_id != (byte)4) fail("Channel mismatch");
		
		// -------- test an ACK packet
		byte[] ack_packet_src = {(byte)(128+6), 4};
		Packet ack_packet = null;
		
		ack_packet = Packet.from_bytes(ack_packet_src);

		if (ack_packet.window_id != (byte)6) fail("Window mismatch");
		if (ack_packet.channel_id != (byte)4) fail("Channel mismatch");
		if (!ack_packet.is_ack) fail("Not ACK");
		
		// ------- test an invalid packet
		byte[] invalid_packet_src = {(byte)128, 4, 2};
		
		boolean was_thrown = false;
		try {
			@SuppressWarnings("unused")
			Packet invalid_packet = Packet.from_bytes(invalid_packet_src);
		} catch (PacketMalformedError e) {
			was_thrown = true;
		}
		
		if (!was_thrown) fail("Invalid packet readed correctly");
	}
	
	@Test
	public void testEquality() throws PacketMalformedError {
		byte[] testpak = {6, 4, 0, 1, 2, 3};
		Packet p1 = new Packet(this.test_data, (byte)4, (byte)6);
		Packet p2 = null;
		p2 = Packet.from_bytes(testpak);
		
		if (!p1.equals(p2)) fail("Not equal");
	}
	
	@Test
	public void testTooShort() {
		byte[] testpak = {1};
		boolean was_thrown = false;
		try {
			@SuppressWarnings("unused")
			Packet p = Packet.from_bytes(testpak);
		} catch (PacketMalformedError e) {
			was_thrown = true;
		}
		if (!was_thrown) fail("Exception not triggered");
	}
}
