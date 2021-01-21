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
	ArrayList<Entry<Time, Entry<Integer, Integer>>> call_backs;
	
	ArrayList<Integer> frames_sent;
	
	boolean off;
	boolean exec_call_back;
	boolean hold_switching;
	int call_back_stage;