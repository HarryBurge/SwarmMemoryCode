package lsi.wsn.sync;

import ptolemy.actor.TypedAtomicActor;
import ptolemy.actor.TypedIOPort;
import ptolemy.actor.util.Time;
import ptolemy.data.DoubleToken;
import ptolemy.data.RecordToken;
import ptolemy.data.BooleanToken;
import ptolemy.data.Token;
import ptolemy.data.type.BaseType;
import ptolemy.data.type.RecordType;
import ptolemy.data.type.Type;
import ptolemy.data.expr.StringParameter;
import ptolemy.data.IntToken;
import ptolemy.kernel.CompositeEntity;
import ptolemy.kernel.util.IllegalActionException;
import ptolemy.kernel.util.NameDuplicationException;

import java.util.AbstractMap;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map.Entry;
import java.util.Scanner;


public class Controller extends TypedAtomicActor{

	
	protected TypedIOPort input, clk;
	protected TypedIOPort output, out_channel;
	StringParameter channels_param;
	
	Integer channels[];
	int channel_PC;
	
	HashMap<Integer, Double> ChannelPeriods;
	
	ArrayList<ArrayList<Entry<Integer, Time>>> calc_tn_times;
	HashMap<Time, Entry<Integer, Integer>> call_backs;
	
	ArrayList<Integer> frames_sent;
	
	boolean off;
	boolean exec_call_back;
	boolean hold_switching;
	int call_back_stage;

	
	public Controller(CompositeEntity container, String name)
	throws NameDuplicationException, IllegalActionException  {

		super(container, name);

		// Ports
		input = new TypedIOPort(this, "input", true, false);
		input.setTypeEquals(BaseType.INT);
		
		clk = new TypedIOPort(this, "clk", true, false);
		
		output = new TypedIOPort(this, "output", false, true);
		output.setTypeEquals(BaseType.INT);
		
		out_channel = new TypedIOPort(this, "channel", false, true);
		out_channel.setTypeEquals(BaseType.INT);
		
		// Channels to be listened too
		channels_param = new StringParameter(this, "channels");
		
		// Channels t values
		ChannelPeriods = new HashMap<Integer, Double>(); //Channel, Period
		
		// Is used to log packets and at what time they came in
		calc_tn_times = new ArrayList<ArrayList<Entry<Integer, Time>>>(); //For each channel list of packets recieved and times
		
		// List of all callbacks and when to execute them
		call_backs = new HashMap<Time, Entry<Integer, Integer>>(); //Time, Instruction, Channel
		
		// How many frames sent
		frames_sent = new ArrayList<Integer>();
	}
	

	public void initialize() throws IllegalActionException{
		// Channels to be listened too
		String[] channels_s = channels_param.stringValue().split(";");
		
		for(int i=0; i<channels_s.length; i++) {
			ChannelPeriods.put(Integer.parseInt(channels_s[i]), null);
		}
		
		// Put the channels to listens too into an array and a pointer to which channel to start at
		channels = ChannelPeriods.keySet().toArray(new Integer[ChannelPeriods.keySet().size()]);
		channel_PC = 0;
		
		// Assign a log for all channels
		for(int i=0; i<channels.length; i++) {
			calc_tn_times.add(new ArrayList< Entry<Integer, Time>>());
			frames_sent.add(0);
		}
		
		off = false; // Listening turned off
		exec_call_back = false; // Executing a call back currently
		hold_switching = false; // Stop the channels from switching
		call_back_stage = 0; // Type of callback we are doing
	}
	

	
	public void fire() throws IllegalActionException{
		
		if (input.hasToken(0)) {
			int packet = ((IntToken) input.get(0)).intValue();
			
			// If current channel has no guess for t
			if (ChannelPeriods.get(channels[channel_PC]) == null && !off) {
				
				// Adds a record of the packet into that channels log
				calc_tn_times.get(channel_PC).add(new AbstractMap.SimpleEntry<Integer, Time>(packet, getDirector().getModelTime()));
				
				// If the packet is above one then hold on channel till next value
				if (packet > 1) {
					hold_switching = true;
				
				// If the packet is one and it hasn't just come from a packet = 2
				// then create a listening callback in the future 11*0.5
				} else if (packet == 1 && calc_tn_times.get(channel_PC).size() <= 1) {
					call_backs.put(getDirector().getModelTime().add(11*0.5), new AbstractMap.SimpleEntry<Integer, Integer>(1, channels[channel_PC]));
				}
				
			
				//Predict t-value if said channel has two values in calc_tn_times
				if (calc_tn_times.get(channel_PC).size() > 1 && !off) {
					
					// Get the time and the value of that packet
					Time t1 = calc_tn_times.get(channel_PC).get(0).getValue();
					Integer x1 = calc_tn_times.get(channel_PC).get(0).getKey();
					
					Time t2 = calc_tn_times.get(channel_PC).get(1).getValue();
					Integer x2 = calc_tn_times.get(channel_PC).get(1).getKey();
					
					// These packets where sent straight after each other due to our locking mechanisims
					if (!(x1 == 1 && 1 <= x2)) {
						double t = Math.abs(t1.getDoubleValue() - t2.getDoubleValue()) / Math.abs(x1 - x2);
						
						if (t <= 1.5 && t >= 0.5) {
							// Therefore t is just the diffrence
							ChannelPeriods.put( channels[channel_PC], t );
						} else {
							calc_tn_times.set(channel_PC, new ArrayList< Entry<Integer, Time>>());
							return;
						}
						
					// This can only aquire when there is a callback listen if the first was a packet 1
					} else {
						double t = Math.abs(t1.getDoubleValue() - t2.getDoubleValue()) / (12);
						
						if (t <= 1.5 && t >= 0.5) {
							// Therefore t is one full cycle away but we have to account for if the packet is say of value 2
							ChannelPeriods.put( channels[channel_PC], t );
						} else {
							calc_tn_times.set(channel_PC, new ArrayList< Entry<Integer, Time>>());
							return;
						}
					}
					
					// If anything was solved then whatever callback being executed must have completed
					exec_call_back = false;
					hold_switching = false;
					
					// Create future callbacks to send frame in future
					double next_rec_frame = x2 * ChannelPeriods.get(channels[channel_PC]);
					
					// This was used due to the callbacks array not allowing to have multiple entrys of the same time
					// Therefore we need to add a small amount of time on so they are diffrent equal to how many channels
					// Have the same t
					
					
					// Sends a packet at predicted time
					for (int k=0; k<5; k++) {
						if ( call_backs.get(getDirector().getModelTime().add(next_rec_frame + k*0.03)) == null) {
							call_backs.put(getDirector().getModelTime().add(next_rec_frame + k*0.03), new AbstractMap.SimpleEntry<Integer, Integer>(2, channels[channel_PC]));
							break;
						}
					}
					
					
					//call_backs.put(getDirector().getModelTime().add(next_rec_frame), new AbstractMap.SimpleEntry<Integer, Integer>(2, channels[channel_PC]));
					
					// Does a resync with clock before it sends a frame to make sure nothing has gone wrong therefore under or overshooting the window
					for (int h=0; h<5; h++) {
						for (int k=0; k<5; k++) {
							if ( call_backs.get(getDirector().getModelTime().add(next_rec_frame + (h*12+9.8)*ChannelPeriods.get(channels[channel_PC]) + k*0.03)) == null) {
								call_backs.put(getDirector().getModelTime().add(next_rec_frame + (h*12+9.8)*ChannelPeriods.get(channels[channel_PC]) + k*0.03), new AbstractMap.SimpleEntry<Integer, Integer>(3, channels[channel_PC]));
								break;
							}
						}
						//call_backs.put(getDirector().getModelTime().add(next_rec_frame + (h*12+9.8)*ChannelPeriods.get(channels[channel_PC])), new AbstractMap.SimpleEntry<Integer, Integer>(3, channels[channel_PC]));
					}
				}
				
				
			// If channel has a predicted t
			} else {
				
				// If we are doing a resync then using the packets value we can predict time to actually send the packet
				if (exec_call_back && call_back_stage==3) {
					double next_rec_frame = packet * ChannelPeriods.get(channels[channel_PC]);
					
					// Sends a packet at predicted time
					call_backs.put(getDirector().getModelTime().add(next_rec_frame), new AbstractMap.SimpleEntry<Integer, Integer>(2, channels[channel_PC]));
					
					exec_call_back = false;
					hold_switching = false;
				}
				
			}
		}
		

		
		if (clk.hasToken(0)) {
			
			boolean token = ((BooleanToken) clk.get(0)).booleanValue();
			
			// Get next call_back to execute if any and at what index
			int exec_call = -1;
			
			for (int i=0; i<call_backs.size(); i++) {
				if (call_backs.keySet().toArray(new Time[call_backs.keySet().size()])[i].getDoubleValue() <= getDirector().getModelTime().getDoubleValue()) {
					exec_call = i;
				}
			}
			
			
			// If we were doing a send packet then we need to stop doing it because it only takes two clock cycles
			if (exec_call_back && call_back_stage == 2) {
				exec_call_back = false;
				hold_switching = false;
			}
			
			
			// Execute call_back if not already doing one
			else if (!exec_call_back && exec_call != -1) {
				
				Time key = call_backs.keySet().toArray(new Time[call_backs.keySet().size()])[exec_call];
				Integer channel = call_backs.get(key).getValue();
				Integer instruction = call_backs.get(key).getKey();
				
				// If packet equalled 1 then we need to listen after certain time to that 
				// channel to catch the next time it has a packet
				if (instruction == 1) {
					
					// Find the value of index of the channel for the channel pointer
					int index = -1;
				
					for (int i=0; i<channels.length; i++) {
						if (channels[i] == channel) {
							index = i;
							break;
						}
					}
				
					channel_PC = index;
					exec_call_back = true;
					hold_switching = true;
					call_back_stage = 1;

				
				// This means we need to send a packet on a specified channel
				} else if (instruction == 2) {
					
					// Find the value of index of the channel for the channel pointer
					int index = -1;
					
					for (int i=0; i<channels.length; i++) {
						if (channels[i] == channel) {
							index = i;
							break;
						}
					}
				
					channel_PC = index;
					call_back_stage = 2;
					exec_call_back = true;
					output.send(0, new IntToken(channel));
					
					frames_sent.set(channel_PC, frames_sent.get(channel_PC) + 1);

				
				// This means we need to do a resync before sending of the packet using a type 2 callback
				} else if (instruction == 3) {
					
					// Find the value of index of the channel for the channel pointer
					int index = -1;
					
					for (int i=0; i<channels.length; i++) {
						if (channels[i] == channel) {
							index = i;
							break;
						}
					}
				
					channel_PC = index;
					call_back_stage = 3;
					exec_call_back = true;
					hold_switching = true;
					
				}
				
			}
			
			// Remove all redundant callbacks so the callbacks time has gone past current time
			HashMap<Time, Entry<Integer, Integer>> call_backs_copy = call_backs;
			for (int i=0; i<call_backs_copy.size(); i++) {
				
				Time key = call_backs_copy.keySet().toArray(new Time[call_backs.keySet().size()])[i];
				Integer channel = call_backs_copy.get(key).getValue();
				Integer instruction = call_backs_copy.get(key).getKey();
				
				if (key.getDoubleValue() <= getDirector().getModelTime().getDoubleValue()) {
					call_backs.remove(key);
				} else {
					
					// Find the value of index of the channel for the channel pointer
					int index = -1;
					
					for (int j=0; j<channels.length; j++) {
						if (channels[j] == channel) {
							index = j;
							break;
						}
					}
					
					if (frames_sent.get(index) == 2) {
						call_backs.remove(key);
					}
					
				}
				
			}
			
			
			// Choose to switch channels if needed and the clock value equals true
			// This allows for switching speeds to be faster without coding them in
			if (!hold_switching && !exec_call_back && !off && token) {
				off = switch_channels();
			}
			
			
			// If normal listening or executing a callback
			if (exec_call_back || hold_switching) {
				while(clk.hasToken(0)) {
					clk.get(0);
				}
			}
			
			
			// Push a updated version of channel to listen too (Switch to chan 8 if finished)
			if (!off || exec_call_back) {
				out_channel.send(0, new IntToken(channels[channel_PC]));
			} else {
				out_channel.send(0, new IntToken(8));
			}
			
			
			// Debug messages to see internal state
			System.out.println("\nChannel predicted t's\n");
						
			for(int i=0; i<channels.length; i++) {
				System.out.print(ChannelPeriods.get(channels[i]));
				System.out.print("\t");
			}
			
			System.out.println("\n Super debugger");
			System.out.println("Time = " + getDirector().getModelTime().getDoubleValue() + "Current Channel = " + channels[channel_PC] + " ExecCallback = " + exec_call_back + " Hold = " + hold_switching);
			System.out.println("-----------");
			
			for (int i=0; i<frames_sent.size(); i++) {
				System.out.print(frames_sent.get(i));
			}
			
			System.out.println("\n__________");
			
			for (int i = 0; i<call_backs.size(); i++) {
				Time temp = call_backs.keySet().toArray(new Time[call_backs.keySet().size()])[i];
				Integer channel = call_backs.get(temp).getValue();
				Integer instruction = call_backs.get(temp).getKey();
				
				System.out.println(temp.getDoubleValue() + " " + channel + " " + instruction + " ");
			}
		}
	}
	
	public boolean switch_channels() {
		boolean check = true;
		
		// Move PC through the channels
		channel_PC++;
		if (channel_PC == channels.length) {
			channel_PC = 0;
		}
		
		// Checks whether all channels have predicted t-values
		for (int i=0; i<channels.length; i++) {
			if(ChannelPeriods.get(channels[i]) == null) {check = false;}
		}
		
		// If not all channels have a predicted t then switch until you get one that doesn't have a t
		while (ChannelPeriods.get(channels[channel_PC]) != null && !check) {
			channel_PC++;
			if (channel_PC == channels.length) {
				channel_PC = 0;
			}
		}
		
		//False if there is still channels without predicted t's
		//True otherwise
		return check;
	}
	
	
}