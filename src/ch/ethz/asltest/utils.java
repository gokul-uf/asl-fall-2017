package ch.ethz.asltest;

import java.nio.ByteBuffer;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class utils {
	public static char getRequestType(ByteBuffer byteBuffer) {
		String reqType = new String(byteBuffer.array(), 0, 3, Charset.forName("UTF-8"));
		if(reqType.equals("get"))return 'g';
		else if(reqType.equals("set"))return 's';
		else
			throw new IllegalArgumentException("Got a weird request: " + "'" + reqType + "'"); 
	}

	public static boolean isSingleGet(ByteBuffer byteBuffer) {
		byte[] array = byteBuffer.array();
		int numSpaces = 0;
		for(int i = 0; i < byteBuffer.limit(); i++) {
			if((array[i] == ' '))numSpaces++; // Is this the best way to compare a byte with a char in Java?
		}
		if(numSpaces > 1)return false;
		else return true;
	}

	public static int countNewLines(String str) {
		String findStr = "\r\n";
		int lastIndex = 0;
		int count = 0;

		while(lastIndex != -1){
		    lastIndex = str.indexOf(findStr,lastIndex);

		    if(lastIndex != -1){
		        count ++;
		        lastIndex += findStr.length();
		    }
		}
		return count;
	}

	public static boolean isCompleteRequest(ByteBuffer byteBuffer) {
		String request = new String(byteBuffer.array(), 0, byteBuffer.position(), Charset.forName("UTF-8"));
		int numNew = countNewLines(request);
		if(request.charAt(0) == 's') {
			if(numNew == 2) return true;
			else return false;
		}
		else if(request.charAt(0) == 'g') {
			if(numNew == 1) return true;
			else return false;
		}
		else
			throw new IllegalArgumentException("Too many newlines, request is" + "'" + request + "'");
	}

	public static boolean isCompleteResponse(ByteBuffer byteBuffer) {
		String request = new String(byteBuffer.array(), 0, byteBuffer.position(), Charset.forName("UTF-8"));
		if(request.endsWith("END\r\n")) {
			return true;
		}
		else 
			return false;
	}

	public static ArrayList<ByteBuffer> getShards(Request request, int numServers) {
		ArrayList<ByteBuffer> shardedRequests = new ArrayList<ByteBuffer>();

		// just like python's .strip().split()[1:] I miss python *sigh*
		// .limit because we flip the buffer while creating the Request object
		// .trim because there's a \r\n at the end of the request we don't want
		String multiGetRequest = new String(request.byteBuffer.array(), 0, request.byteBuffer.limit(), Charset.forName("UTF-8")).trim();
		String[]splits = multiGetRequest.split(" ");
		List<String> keys = Arrays.asList(splits).subList(1, splits.length);

		for(int i = 0; i < keys.size(); i++) {
			ByteBuffer byteBuffer;
			if(i < numServers) {
				// create a new byteBuffer, put "get" inside, add to the ArrayList
				byteBuffer = ByteBuffer.allocate(5*1024); // TODO put the right range here
				byteBuffer.put("get".getBytes((Charset.forName("UTF-8"))));
				shardedRequests.add(byteBuffer);
			}
			else { // just use the right byteBuffer
				byteBuffer = shardedRequests.get(i % numServers);
			}
			byteBuffer.put((" " + keys.get(i)).getBytes(Charset.forName("UTF-8")));
		}

		for(ByteBuffer shardedRequest: shardedRequests) {
			shardedRequest.put(("\r\n").getBytes(Charset.forName("UTF-8"))); // don't flip here, flip before reading to make sure you have flipped
		}

		if(shardedRequests.size() > numServers) {
			throw new IllegalArgumentException("getShards fucked up, want < numServers shardeds, have " + Integer.toString(shardedRequests.size()));
		}

		return shardedRequests;
	}

	public static ByteBuffer joinShards(ArrayList<ByteBuffer> responses) {
		ByteBuffer response = ByteBuffer.allocate(14*10240); // TODO find the right size, 20 to spare
		for(ByteBuffer byteBuffer: responses) {
			// TODO handle cases when return is ERROR\r\n, this should not happen
			response.put(byteBuffer.array(), 0, byteBuffer.position() - 5); // strip off END\r\n
		}
		response.put("END\r\n".getBytes(Charset.forName("UTF-8")));

		return response;
	}
}
