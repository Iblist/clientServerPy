#!/usr/bin/python3.5

####################################################################################
# 'OBLIGATORY COPYRIGHT':
# <https://github.com/Iblist> wrote this. As long as you retain this notice, you can
# Do whatever you want with this stuff.
# If you think it's cool or useful, you can me a drink.
####################################################################################

import socket
import threading
import select
import multiprocessing as queue
import time

inputFromUser = queue.Queue()

def manager(address, port):
	connectionIsAlive = True
	queueSocketPoll = select.poll()
	events = select.POLLIN | select.POLLPRI

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
		try:
			sock.connect((address, port))
			queueSocketPoll.register(inputFromUser._reader, events)
			queueSocketPoll.register(sock, events)

			while connectionIsAlive:
				results = queueSocketPoll.poll()
				for item in results:
					if item[0] == inputFromUser._reader.fileno():
						messageToSend = inputFromUser.get()
						if messageToSend.lower() == '/quit':
							connectionIsAlive = False
						else:
							sock.sendall(bytes(messageToSend, 'ascii'))
					elif item[0] == sock.fileno():
						messageFromServer = str(sock.recv(1024), 'ascii')
						if messageFromServer == "":
							connectionIsAlive = False
						else:
							print("Server: {}".format(messageFromServer))
		except Exception as e:
			print("Connection to {} (port {}) refused, error: {}".format(address, port, e))
		finally:
			print("Connection closed, bye bye")

if __name__ == "__main__":
	address, port = '127.0.0.1', 13352

	connection = threading.Thread(target = manager, args=(address, port))
	#connection = threading.Thread(target = temp)
	connection.start()
	while connection.is_alive():
		connection.join(0)
		userInput = input()
		inputFromUser.put(userInput)



