package ch.ethz.asltest;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.logging.FileHandler;
import java.util.logging.Level;
import java.util.logging.Logger;

public class Worker implements Runnable {
	LinkedBlockingQueue<Request> requestQueue;
	ArrayList<SocketChannel> socketChannels = new ArrayList<SocketChannel>();
	Boolean isSharded;
	int whosNext;
	int workerId;
	Logger infoLogger;
	Logger errorLogger;

	public Worker(List<String> mcAddresses, LinkedBlockingQueue<Request> requestQueue, boolean readSharded, int workerId, String prefix) {
		try {
			this.requestQueue =requestQueue;
			this.isSharded = readSharded;
			this.whosNext = 0;
			this.workerId = workerId;
			for(String IpPort: mcAddresses) {
				String[] parts = IpPort.split(":");
				assert parts.length == 2;
				SocketChannel socketChannel = SocketChannel.open();
				socketChannel.connect(new InetSocketAddress(parts[0], Integer.parseInt(parts[1])));
				socketChannel.configureBlocking(true);
				this.socketChannels.add(socketChannel);
			}

			prefix += "id-" + Integer.toString(workerId);

			this.infoLogger = Logger.getLogger(Worker.class.getName() + Integer.toString(workerId) + "-INFO");
			this.infoLogger.setLevel(Level.INFO);
			FileHandler infoFileHandler = new FileHandler(prefix + ".info");
			infoFileHandler.setFormatter(new LogFormatter());
			this.infoLogger.addHandler(infoFileHandler);
			
			this.errorLogger = Logger.getLogger(Worker.class.getName() + Integer.toString(workerId) + "-ERROR");
			this.errorLogger.setLevel(Level.WARNING);
			FileHandler errorFileHandler = new FileHandler(prefix + ".error");
			errorFileHandler.setFormatter(new LogFormatter());
			this.errorLogger.addHandler(errorFileHandler);
			
			// Don't log to console as well
			this.infoLogger.setUseParentHandlers(false);
			this.errorLogger.setUseParentHandlers(false);
		}
		catch(Exception e) {
			System.out.println("Exception during init of Worker \n");
			e.printStackTrace();
		}
	}

	@Override
	public void run() {
		try {
			while(true) {
				Request request = this.requestQueue.take();
				request.timeDequeued = System.nanoTime();
				processRequest(request);
				this.infoLogger.log(Level.INFO, request.GetLoggerLine()); // log every request
			}
		}
		catch(Exception e) {
			System.out.println("Exception during run of Worker");
			this.errorLogger.log(Level.WARNING, e.getMessage() + "\n");
			e.printStackTrace();
		}
	}

	private void processRequest(Request request) {
		ByteBuffer byteBuffer = request.byteBuffer;
		char reqType = utils.getRequestType(byteBuffer);
		if(reqType == 'g') processGetRequest(request);
		else if(reqType == 's') processSetRequest(request);
	}

	private void processSetRequest(Request request) {
		try {
			ByteBuffer byteBuffer = ByteBuffer.allocate(2*1024); // TODO sets are always just one key, no?
			ArrayList<String> exceptions = new ArrayList<String>();

			
			// write to each server
			request.timeStartSendToMC = System.nanoTime();
			for(SocketChannel socketChannel: this.socketChannels){
				socketChannel.write(request.byteBuffer);
				request.byteBuffer.rewind();
			}
			request.timeSentToMC = System.nanoTime();

			// now read-back
			request.timeStartRecvdFromMC = System.nanoTime();
			for(SocketChannel socketChannel: this.socketChannels) {
				byteBuffer.clear();
				socketChannel.read(byteBuffer);

				String response = new String(Arrays.copyOfRange(byteBuffer.array(), 
																0, byteBuffer.position()), 
										 	Charset.forName("UTF-8"));
				if(!response.equals("STORED\r\n"))exceptions.add(response);
			}
			request.timeRecvdFromMC = System.nanoTime();

			if(exceptions.isEmpty()) {
				// If no exceptions, byteBuffer will contain "STORED\r\n", use it
				byteBuffer.flip();
			}
			else { // Write the exceptions to logger and send the first one back
				String exception = exceptions.get(0);
				byteBuffer = ByteBuffer.wrap(exception.getBytes(Charset.forName("UTF-8" )));

				// Writing exceptions to log
				this.errorLogger.log(Level.WARNING,"SET, NUM: " + Integer.toString(exceptions.size()));
				for(String exp: exceptions) {
					this.errorLogger.log(Level.WARNING, exp);
				}
			}
			request.timeStartSentBack = System.nanoTime();
			request.socketChannel.write(byteBuffer);
			request.timeSentBack = System.nanoTime();
			
		}
		catch (Exception e) {
			System.out.println("Exception in ProcessSetRequest of Worker");
			this.errorLogger.log(Level.WARNING, e.getMessage() + "\n");
			e.printStackTrace();
		}
	}

	private void processGetRequest(Request request) {
		try {
			if(utils.isSingleGet(request.byteBuffer)) {
				processSingleGetRequest(request);
			}
			else {
				processMultiGetRequest(request);
			}
		} catch (Exception e) {
			System.out.println("Exception in ProcessGetRequest of Worker");
			this.errorLogger.log(Level.WARNING, e.getMessage() + "\n");
			e.printStackTrace();
		}
	}

	private void processMultiGetRequest(Request request) {
		try {
			if(this.isSharded  && this.socketChannels.size() > 1) { // sharded on single server is still like single-get request -.-'

				ArrayList<ByteBuffer> partialRequests = utils.getShards(request, this.socketChannels.size());
				
				request.timeStartSendToMC = System.nanoTime();
				for(int i = 0; i < partialRequests.size(); i++) {
					ByteBuffer byteBuffer = partialRequests.get(i);
					byteBuffer.flip();
					SocketChannel socketChannel = this.socketChannels.get(i);
					socketChannel.write(byteBuffer);
				}
				request.timeSentToMC = System.nanoTime();
				
				ArrayList <ByteBuffer> partialResponses = new ArrayList<ByteBuffer>();
				request.timeStartRecvdFromMC = System.nanoTime();
				for(int i = 0; i < partialRequests.size(); i++) {
					SocketChannel socketChannel = this.socketChannels.get(i);
					ByteBuffer byteBuffer = ByteBuffer.allocate(5*1024); // TODO find the right size here
					while(!utils.isCompleteResponse(byteBuffer)) {
						socketChannel.read(byteBuffer); // read until complete response complete response here
					}
					partialResponses.add(byteBuffer);
				}
				request.timeRecvdFromMC = System.nanoTime();
				
				
				for(ByteBuffer buf: partialResponses) {
					String first = new String(Arrays.copyOfRange(buf.array(), 0, 3));
					if(!(first.equals("VAL") || first.equals("END"))) { // Starts with VALUE or END (for get miss)
						first = new String(Arrays.copyOfRange(buf.array(), 0, buf.position()));
						this.errorLogger.log(Level.WARNING, "MultiGet: "+ first);
					}
				}
				
				ByteBuffer response = utils.joinShards(partialResponses);
				response.flip();
				SocketChannel socketChannel = request.socketChannel;
				request.timeStartSentBack = System.nanoTime();
				socketChannel.write(response);
				request.timeSentBack = System.nanoTime();
			}
			else {
				processSingleGetRequest(request);
			}
		}
		catch (Exception e) {
			System.out.println("Exception in ProcessMultiGetRequest of Worker");
			this.errorLogger.log(Level.WARNING, e.getMessage() + "\n");
			e.printStackTrace();
		}
	}

	private void processSingleGetRequest(Request request) {
		try {
			SocketChannel socketChannel = this.socketChannels.get(whosNext);
			ByteBuffer byteBuffer = request.byteBuffer;

			request.timeStartSendToMC = System.nanoTime();
			socketChannel.write(byteBuffer);
			byteBuffer = ByteBuffer.allocate(15*1024);
			request.timeSentToMC = System.nanoTime();
			
			request.timeStartRecvdFromMC = System.nanoTime();
			while(!utils.isCompleteResponse(byteBuffer)) {
				socketChannel.read(byteBuffer); // handle partial response cases
			}
			request.timeRecvdFromMC = System.nanoTime();

			String response = new String(Arrays.copyOfRange(byteBuffer.array(), 0, 3));
			if(!(response.equals("VAL") || response.equals("END"))) { // non-error get responses start with VALUE or END
				this.errorLogger.log(Level.WARNING, "SINGLE GET, MC ID: " + Integer.toString(this.whosNext));
				response = new String(Arrays.copyOfRange(byteBuffer.array(), 0, byteBuffer.position()));
				this.errorLogger.log(Level.WARNING, response);
			}

			byteBuffer.flip();
			request.timeStartSentBack = System.nanoTime();
			request.socketChannel.write(byteBuffer);
			request.timeSentBack = System.nanoTime();
			
			this.whosNext = (this.whosNext+1) % this.socketChannels.size();
		} catch (Exception e) {
			System.out.println("Exception in ProcessSingleGetRequest of Worker");
			this.errorLogger.log(Level.WARNING, e.getMessage() + "\n");
			e.printStackTrace();
		}
	}
}
