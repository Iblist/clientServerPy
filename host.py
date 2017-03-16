#!/usr/bin/python3.5

import socketserver
import socket
import threading
import multiprocessing as queue
import select

'''
NOTES FOR SELF
Socket - Read from the socket into a queue. Write to socket from a queue.
QueueIn - Read into this queue from the socket, so select with socket as rlist.
QueueOut - Read from this queue to the socket, so select the queue as wlist.
use poll instead?
The main thread only really needs to keep track of one queue, to which the associated threads
will repeatedly write to.
The issue is, the threads need to listen to both their sockets, and to a queue at the same time.
The obvious answer is to use select() to avoid a spinlock.
The queue class in the multiprocessing module supposedly works with select.
'''

#Code executed by thread.
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
	
	def handle(self):
		temp = True
		message = bytes("Hey there bitch ass nigga", 'ascii')
		#code
		'''
		PSEUDO CODE!
		Use select on two data streams, the input from the socket and a select a buffer containing stuff read from user.
		select blocks, use if else to interpret which has stopped blocking. Need to ensure input is only sent to user
		once.
		'''
		events = select.POLLIN | select.POLLPRI
		socketQueuePoll = select.poll()
		temp = threading.current_thread()
		socketQueuePoll.register(self.request.fileno(), events)
		socketQueuePoll.register(outputToUsers._reader, events)

		'''
		Magic stuff
		Basically select.poll() polls supplied file descriptors and returns a list of which ones are readable.
		By using this, you are able to determine whether the queue or socket has been written to before
		accessing them, and thus avoid spin locks. This depends on how select.poll works, I'm like 90% sure
		it works with interrupts, but I'm too lazy to check. Anyway, it works, so fuck it.
		poll returns a list of tuples.
		The first item in the tuple is the filedescriptor, the second is the event.
		Both are integers.
		Since poll blocks for us, assign the returned list to result, loop through result and
		unpack tuples. Compare tuple against the queue and socket. If the id is the sockets,
		the program should read from that socket and place the read message in the queue.
		If the id is the queues, it should read from the queue and write the value to the
		socket.
		Values read to and from the queue should be in byte form to work with socket transmissions.
		'''
		result = socketQueuePoll.poll()
		print("Result:{}. Socket FileNo:{}.".format(result[0][0], self.request.fileno()))
		if result[0][0] == self.request.fileno():
			self.request.sendall(message)


#Object constructed with this class to indicate use of threading with tcp server.
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

inputFromUsers = queue.Queue()
outputToUsers = queue.Queue()

def tempClient(ip, port, message):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
		sock.connect((ip, port))
		sock.sendall(bytes(message, 'ascii'))
		response = str(sock.recv(1024), 'ascii')
		print("Received: {}".format(response))

if __name__ == "__main__":
	# Port 0 means to select an arbitrary unused port
	HOST, PORT = "localhost", 0

	server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
	ip, port = server.server_address

	# Start a thread with the server -- that thread will then start one
	# more thread for each request
	server_thread = threading.Thread(target=server.serve_forever)
	# Exit the server thread when the main thread terminates
	server_thread.daemon = True
	server_thread.start()
	print("Server loop running in thread:", server_thread.name)

	tempClient(ip, port, "Message 1")
	tempClient(ip, port, "Message 2")
	tempClient(ip, port, "Message 3")
	

	






