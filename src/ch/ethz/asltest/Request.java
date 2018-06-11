package ch.ethz.asltest;

import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;

public class Request {

	ByteBuffer byteBuffer;
	SocketChannel socketChannel;
	public long timeCreated;

	public long timeEnqueued;
	public long timeDequeued;

	public long timeStartSendToMC;
	public long timeSentToMC;

	public long timeStartRecvdFromMC;
	public long timeRecvdFromMC;
	
	public long timeStartSentBack;
	public long timeSentBack;
	
	public char reqType;
	
	public Request(SocketChannel socketChannel, ByteBuffer byteBuffer) {
		this.socketChannel = socketChannel;
		this.byteBuffer = byteBuffer; 
		this.byteBuffer.flip(); // flipped here to be read from
		this.timeCreated = System.nanoTime();
		this.reqType = utils.getRequestType(byteBuffer);
	}

	public String GetLoggerLine() {
		StringBuilder str = new StringBuilder();
		str.append(this.reqType);
		str.append(" ");
		
		str.append(this.timeCreated);
		str.append(" ");
		
		str.append(this.timeEnqueued);
		str.append(" ");
		str.append(this.timeDequeued);
		str.append(" ");
		
		str.append(this.timeStartSendToMC);
		str.append(" ");
		str.append(this.timeSentToMC);
		str.append(" ");
		
		str.append(this.timeStartRecvdFromMC);
		str.append(" ");
		str.append(this.timeRecvdFromMC);
		str.append(" ");
		
		str.append(this.timeStartSendToMC);
		str.append(" ");
		str.append(this.timeSentBack);
		str.append("\n");
		return str.toString();
	}
}
