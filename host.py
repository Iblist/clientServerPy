#!/usr/bin/python

import SocketServer
import threading

#Code executed by thread.
class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
	
	def handle(self, ):
		#code
		'''
		PSEUDO CODE!
		Use select on two data streams, the input from the socket and a select a buffer containing stuff read from user.
		select blocks, use if else to interpret which has stopped blocking. Need to ensure input is only sent to user
		once.
		'''
		

#Object constructed with this class to indicate use of threading with tcp server.
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	pass

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
    print "Server loop running in thread:", server_thread.name
