# clientServerPy
Simple implementation of an IRC like client server communication...thing written for Python3.5

¯\_(ツ)_/¯

#Purpose
This program is more or less me practicing/learning sockets, multi-threading, and inter-thread communication methods.
It is a simplistic implementation of a client server chat room. Multiple clients connect to the server, send messages,
and the server echoes those messages back to each connected client. There isn't anything like usernames, passwords, or
any kind of security implemented.

In future, I may attempt to implement the entire IRC protocol, just for the hell of it.

#Usage
Run program using Python3.5
Not supported for Windows machines, will probably only work on \*nix machines. Whether that includes mac or not, I'm not sure.
Can also be run as an executable with chmod +x

During program execution, if a client connects to the server a message will appear indicating a new connection was successfully
started. This alert will only appear if the connection was accepted, and a new thread was spawned for the new client.
If a connected client disconnects from the server, a message will appear indicating a client has disconnected, and the thread has
shut down.

To exit the program, use either CTRL+Z or CTRL+C. Eventually, the ability to close the client from the command line more gracefully
should be implemented, as well as input of commands.

#Planned features
This of course assumes I feel like tinkering with this later >.>

Use of server side commands, such as closing program and listing connected clients.
Usernames. Allow users to connect with a username (and maybe password), and have that displayed with messages to clients.
Full implement of IRC protocol.

