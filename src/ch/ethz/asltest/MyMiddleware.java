package ch.ethz.asltest;
import java.io.File;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.util.Iterator;
import java.util.List;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.logging.FileHandler;
import java.util.logging.Level;
import java.util.logging.Logger;

public class MyMiddleware implements Runnable{
	LinkedBlockingQueue<Request> requestQueue = new LinkedBlockingQueue<Request>();
	ServerSocketChannel serverSocketChannel;
	Selector selector;
	Logger errorLogger;
	Logger infoLogger;
	Logger lengthLogger;

	public MyMiddleware(String myIp, int myPort, List<String> mcAddresses, int numThreadsPTP, boolean readSharded) {
		try {
			// for labeling loggers
			String prefix = "logs/" +
							"mc-" + Integer.toString(mcAddresses.size()) + "_" +
							"workers-" + Integer.toString(numThreadsPTP)+ "_" +
							"shard-" + Boolean.toString(readSharded) + "_";

			// Create the logging directory
			File homeLoggingDir = new File("logs");
			if (!homeLoggingDir.exists()) homeLoggingDir.mkdirs();

			// Open the ServerSocketChannel
			InetSocketAddress endpoint = new InetSocketAddress(myIp, myPort);
			this.serverSocketChannel = ServerSocketChannel.open();
			this.serverSocketChannel.socket().bind(endpoint);
			this.serverSocketChannel.configureBlocking(false);

			// Open a selector
			this.selector = Selector.open();

			// Create the worker threads
			for(int i = 0; i < numThreadsPTP; i++){  
				new Thread(new Worker(mcAddresses, this.requestQueue, readSharded, i, prefix)).start();
			}

			// register the serverSocketChannel with the selector
			this.serverSocketChannel.register(this.selector, SelectionKey.OP_ACCEPT);

			// Create loggers
			this.infoLogger = Logger.getLogger(MyMiddleware.class.getName() + "-INFO");
			this.infoLogger.setLevel(Level.INFO);
			FileHandler infoFileHandler = new FileHandler(prefix + "frontend.info");
			infoFileHandler.setFormatter(new LogFormatter());
			this.infoLogger.addHandler(infoFileHandler);

			this.errorLogger = Logger.getLogger(MyMiddleware.class.getName() + "-ERROR");
			this.errorLogger.setLevel(Level.WARNING);
			FileHandler errorFileHandler = new FileHandler(prefix + "frontend.error");
			errorFileHandler.setFormatter(new LogFormatter());
			this.errorLogger.addHandler(errorFileHandler);

			this.lengthLogger = Logger.getLogger(MyMiddleware.class.getName() + "-LENGTH");
			this.lengthLogger.setLevel(Level.INFO);
			FileHandler lengthFileHandler = new FileHandler(prefix + "queue.length");
			lengthFileHandler.setFormatter(new LogFormatter());
			this.lengthLogger.addHandler(lengthFileHandler);			
			
			// Don't log to console as well
			this.infoLogger.setUseParentHandlers(false);
			this.errorLogger.setUseParentHandlers(false);
			this.lengthLogger.setUseParentHandlers(false);
		}
		catch(Exception e){
			System.out.println("Exception during init of MyMiddleware \n");
			e.printStackTrace();
		}
	}

	@Override
	public void run() {
		try {
			while(true){
				selector.select();
				Iterator<SelectionKey> iterator = this.selector.selectedKeys().iterator();
				while(iterator.hasNext()) {
					SelectionKey key = iterator.next();
					if(key.isAcceptable()) addNewConnection(key);
					else if(key.isReadable()) readRequest(key);
					iterator.remove();
				}
			}
		}
		catch(Exception e){
			System.out.println("Exception during run of MyMiddleware");
			this.errorLogger.log(Level.WARNING, e.getMessage() + "\n");
			e.printStackTrace();
			
		}
	}

	private void readRequest(SelectionKey key) {
		try {
			ByteBuffer byteBuffer = null;
			if(key.attachment() != null) byteBuffer = (ByteBuffer)key.attachment();
			else byteBuffer = ByteBuffer.allocate(15*1024); // 14 KB buffer, 10*1024 payload, 256*10 keys, plus some to spare, TODO too much?

			SocketChannel socketChannel = (SocketChannel)key.channel();
			int numRead = socketChannel.read(byteBuffer);

			if(numRead < 0) { // client closed
				key.cancel();
				return;
			}

			if(utils.isCompleteRequest(byteBuffer)) {
				Request request = new Request(socketChannel, byteBuffer);
				request.timeEnqueued = System.nanoTime();
				this.requestQueue.put(request);
				key.attach(null); // remove the attachment
				this.lengthLogger.log(Level.INFO, Integer.toString(this.requestQueue.size()) + "\n");
			}
			else {
				key.attach(byteBuffer);
			}
		}
		catch(Exception e) {
			System.out.println("Exception during readChannel of MyMiddleware");
			this.errorLogger.log(Level.WARNING, e.getMessage() + "\n");
			e.printStackTrace();
		}
	}

	private void addNewConnection(SelectionKey key) {
		try {
			ServerSocketChannel serverSocketChannel = (ServerSocketChannel)key.channel();
			assert serverSocketChannel == this.serverSocketChannel;

			SocketChannel socketChannel = serverSocketChannel.accept();
			socketChannel.configureBlocking(false);
			socketChannel.register(this.selector, SelectionKey.OP_READ);
		}
		catch(Exception e) {
			System.out.println("Exception during addNewConnection of MyMiddleware");
			this.errorLogger.log(Level.WARNING, e.getMessage() + "\n");
			e.printStackTrace();
		}		
	}
}
