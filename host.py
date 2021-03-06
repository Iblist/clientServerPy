#!/usr/bin/python3.5

####################################################################################
# 'OBLIGATORY COPYRIGHT':
# <https://github.com/Iblist> wrote this. As long as you retain this notice, you can
# Do whatever you want with this stuff.
# If you think it's cool or useful, you can me a drink.
####################################################################################

import socket
import threading
import multiprocessing
import select
import time

'''
This class handles multiple TCP client connections simultaneously through multi-threading.

When a new connection is detected, a new thread is produced to handle that client.

The specification of a HOST, PORT, and the maximum number of allowed clients is possible during
initialization.

A 'input_from_user_queue' exists as a multiprocessing Queue for child threads to send messages recieved
from clients back to the main thread. A 'output_to_user_queue_list' exists as a list of Queues. Each
child thread is given one of these Queues. The parent thread sends messages for clients to each of these
Queues when a message is recieved in the input_from_user_queue.

The 'output_to_user_queue_list' exists as a list of size 1 dictionaries, where the key is either 'in_use'
or 'not_in_use'. This allows created Queues to be reused if a client decides to disconnect.
'''
class TCPMultiThreadServer():
	def __init__(self, HOST, PORT, max_clients=10):
		self.HOST = HOST
		self.PORT = PORT
		self.output_to_user_queue_list = []
		self.input_from_user_queue = multiprocessing.Queue()
		self.max_clients = max_clients
		self.active_clients = 0
		self.thread_list = []

	#Main thread, handles connection requests and spawns child threads.
	def start(self):
		server_is_up = True
		socket_queue_poll = select.poll() #Polls listening Socket for new connections, and input_queue.
		events = select.POLLIN

		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as main_socket:
			main_socket.bind((self.HOST, self.PORT))
			main_socket.listen()
			socket_queue_poll.register(main_socket, events)
			socket_queue_poll.register(self.input_from_user_queue._reader, events)
			#thread_list = []

			while server_is_up:
				result = socket_queue_poll.poll()
				for target in result:
					if target[0] == main_socket.fileno():
						self.handle_new_client(main_socket)
						
					elif target[0] == self.input_from_user_queue._reader.fileno():
						self.handle_queue_input()
								
							
	#Handles active client connections.
	#Input from client is sent to main thread.
	#Messages from main thread are sent to client.
	#Upon exit, output queue is marked 'not_in_use', and the number of clients is deincremented
	def handle(self, sock_tuple=None, output_to_user_queue=None, input_from_user_queue=None):
		connection_is_live = True
		print('Connection Accepted and Started')
		out_queue = output_to_user_queue['in_use']
		in_queue = input_from_user_queue
		client_connection = sock_tuple[0]

		socket_queue_poll = select.poll()
		events = select.POLLIN
		socket_queue_poll.register(client_connection.fileno(), events)
		socket_queue_poll.register(out_queue._reader, events)

		while connection_is_live:
			result = socket_queue_poll.poll()
			#print('result: {} queue: {}'.format(result, out_queue._reader.fileno()))
			for target in result:
				if target[0] == out_queue._reader.fileno():
					message = out_queue.get()
					client_connection.sendall(bytes(message, 'ascii'))
				elif target[0] == client_connection.fileno():
					message = str(client_connection.recv(1024), 'ascii')
					if message == "":
						connection_is_live = False
						break
					in_queue.put(message)
					out_queue.get()
		output_to_user_queue['not_in_use'] = output_to_user_queue.pop('in_use')
		self.active_clients -= 1
		print('Connection to client closed')


	#Creates more output_to_user_queues and adds them to the output_to_user_queue_list
	#Will create 10 queues each time it is called, but will not create more than the max_clients allowed.
	def add_more_clients(self):
		for i in range(10):
			if i == self.max_clients:
				break
			self.output_to_user_queue_list.append({'not_in_use':multiprocessing.Queue()})


	#When a connection is recieved, this function is called.
	#First checks if there is available room for new connection.
	#Next, checks there are enough Queues to handle the new number of clients, creating more as necessary
	#Increments number of active_clients, and creates a new thread passing it an output_to_user_queue marked 'not_in_use'
	#and the input_from_user_queue, as well as the socket the connection will be on.
	#If there is not enough room, the function accepts and immediately closes the socket.
	def handle_new_client(self, main_socket):
		if self.active_clients < self.max_clients:
			if self.active_clients == len(self.output_to_user_queue_list):
				self.add_more_clients()
			new_connection = main_socket.accept()
			self.active_clients += 1		
			for queue in self.output_to_user_queue_list:
				if 'not_in_use' in queue:
					output_to_user_queue = queue
					output_to_user_queue['in_use'] = output_to_user_queue.pop('not_in_use')
					break

			new_thread = threading.Thread(target=self.handle, args=[new_connection, output_to_user_queue, self.input_from_user_queue], daemon=True)
			self.thread_list.append(new_thread)
			new_thread.start()

		else:
			conn = main_socket.accept()
			conn[0].sendall(bytes('R-R-R-R-REJECTED', 'ascii'))
			conn[0].close()
						

	#Sends message in input_from_user_queue to all active threads.
	#Loops through output_to_user_queue_list and passes the message
	#To each queue marked 'in_use'
	def handle_queue_input(self):
		message = self.input_from_user_queue.get()
		for target in self.output_to_user_queue_list:
			if 'in_use' in target:
				queue = target['in_use']
				queue.put(message)


#Just invokes the class above which handles all the actual work.
if __name__ == "__main__":
	server = TCPMultiThreadServer('localhost', 13352, max_clients = 2)
	server.start()			
=======
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

#Code executed by thread.
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
	
	def handle(self):
		connectionActive = True
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

		while connectionActive:
			result = socketQueuePoll.poll()
			#print("Result:{}. Socket FileNo:{}.".format(result[0][0], self.request.fileno())) #temp code
			for thing in result:
				if thing[0] == self.request.fileno():
					response = str(self.request.recv(1024), 'ascii')
					outputToUsers.put(response)
				elif thing[0] == outputToUsers._reader:
					print("Something or other")
			connectionActive = False
			


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

def makeClients(ip, port):
	tempClient(ip, port, "This is a message 1")
	tempClient(ip, port, "This is a message 2")
	tempClient(ip, port, "This is a message 3")

if __name__ == "__main__":
	# Port 0 means to select an arbitrary unused port
	HOST, PORT = "localhost", 0

	server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
	ip, port = server.server_address
	print("Host is: ", server.server_address)

	# Start a thread with the server -- that thread will then start one
	# more thread for each request
	server_thread = threading.Thread(target=server.serve_forever)
	# Exit the server thread when the main thread terminates
	server_thread.daemon = True
	server_thread.start()
	print("Server loop running in thread:", server_thread.name)
	
	clientMaker = threading.Thread(target=makeClients, args=(ip, port))
	clientMaker.start()
	clientMaker.join()
	'''
	tempClient(ip, port, "Message 1")
	tempClient(ip, port, "Message 2")
	tempClient(ip, port, "Message 3")
	'''
	server.shutdown()
	server.server_close()
	
>>>>>>> afad17bb6eee0132d2e225b29421d277bf156eb3






