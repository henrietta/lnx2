package tests;

import static org.junit.Assert.*;

import org.junit.Test;
import java.util.Vector;
import java.util.Arrays;
import java.lang.Thread;
import pl.com.henrietta.lnx2.*;
import pl.com.henrietta.lnx2.exceptions.*;

public class connectiontest {

	private byte[] test_data = {0, 1, 2, 3};
	
	private boolean equals_test_data(byte[] data) {
		return Arrays.equals(data, this.test_data);
	}
	
	@Test
	public void test_channels() throws NothingToSend, NothingToRead {
		Channel alice_0 = new Channel((byte)0, RetransmissionMode.RTM_NONE, 1, 1);
		Channel bob_0 = new Channel((byte)0, RetransmissionMode.RTM_NONE, 1, 1);

		Channel alice_1 = new Channel((byte)1, RetransmissionMode.RTM_NONE, 1, 1);
		Channel bob_1 = new Channel((byte)1, RetransmissionMode.RTM_NONE, 1, 1);

		Vector<Channel> v1 = new Vector<>();
		Vector<Channel> v2 = new Vector<>();
		
		v1.add(alice_0); v1.add(alice_1);
		v2.add(bob_0); v2.add(bob_1);
		
		Connection alice = new Connection(v1, 1);
		Connection bob = new Connection(v2, 1);
		
		alice.getChannel(0).write(this.test_data);
		bob.on_received(alice.on_sendable());
		
		if (!this.equals_test_data(bob.getChannel(0).read())) fail("Not equal");
		if (!bob.has_new_data) fail("No 'has new data'");
	}
	
	@Test
	public void test_noflag_RTM_MANUAL() throws NothingToSend, NothingToRead {
		Channel alice_0 = new Channel((byte)0, RetransmissionMode.RTM_MANUAL, 1, 1);
		Channel bob_0 = new Channel((byte)0, RetransmissionMode.RTM_MANUAL, 1, 1);

		Vector<Channel> v1 = new Vector<>();
		Vector<Channel> v2 = new Vector<>();
		
		v1.add(alice_0);
		v2.add(bob_0);
		
		Connection alice = new Connection(v1, 1);
		Connection bob = new Connection(v2, 1);
		
		// Alice -> Bob -> Alice
		alice.getChannel(0).write(this.test_data);
		bob.on_received(alice.on_sendable());		
		bob.getChannel(0).write(this.test_data);		
		alice.on_received(bob.on_sendable());
		alice.on_received(bob.on_sendable());
		bob.on_received(alice.on_sendable());

		bob.getChannel(0).read(); alice.getChannel(0).read();
		if (!alice.has_new_data) fail("No new data");
		if (!bob.has_new_data) fail("No new data");
		alice.has_new_data = false;
		bob.has_new_data = false;		
				
		// A->B->A
		alice.getChannel(0).write(this.test_data);
		bob.on_received(alice.on_sendable());		
		bob.getChannel(0).write(this.test_data);		
		alice.on_received(bob.on_sendable());
		alice.on_received(bob.on_sendable());
		bob.on_received(alice.on_sendable());
		
		bob.getChannel(0).read(); alice.getChannel(0).read();
		if (!alice.has_new_data) fail("No new data");
		if (!bob.has_new_data) fail("No new data");
		alice.has_new_data = false;
		bob.has_new_data = false;
		
	}	
	
	@Test
	public void test_misrouting() throws NothingToSend, NothingToRead {
		Channel alice_0 = new Channel((byte)0, RetransmissionMode.RTM_NONE, 1, 1);

		Channel alice_1 = new Channel((byte)1, RetransmissionMode.RTM_NONE, 1, 1);
		Channel bob_1 = new Channel((byte)1, RetransmissionMode.RTM_NONE, 1, 1);

		Vector<Channel> v1 = new Vector<>();
		Vector<Channel> v2 = new Vector<>();
		
		v1.add(alice_0); v1.add(alice_1);
		v2.add(bob_1);
		
		Connection alice = new Connection(v1, 1);
		Connection bob = new Connection(v2, 1);
		
		alice.getChannel(0).write(this.test_data);
		bob.on_received(alice.on_sendable());
			
		boolean thrown = false;
		try { bob.getChannel(1).read(); } catch (NothingToRead n) { thrown = true; }
		if (!thrown) fail("Not thrown");
		if (bob.has_new_data) fail("Has new data");		
	}
	
	@Test
	public void test_timeout() throws InterruptedException {
		Vector<Channel> v1 = new Vector<>();
		Connection alice = new Connection(v1, (float)0.5);
		
		Thread.sleep(600);
		
		if (!alice.has_timeouted()) fail("Not timeouted");
		if (alice.has_new_data) fail("Has new data");
	}

	
}
