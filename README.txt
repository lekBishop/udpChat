Liam Bishop
A simple python chat using UDP

Command Line Instructions:
	- No need to compile python script
	- Run chmod so file can be executed
	chmod +x udpChat.py

	Run server: ./udpChat.py -s <port-number>
	Run Client: ./udpChat.py -c <client-name> <server-address> <server-port> <client-port>

Client Commands:
	Send a message: send <reciever-name> <message>
	Deregister client: dereg <client-name>
	Register client: reg <client-name>

The server is able to support many clients all talking to each other. If any client goes offline the 
messages sent to them will be saved in a file called <client-name>_offlineMessages. The server works by constantly checking for incoming client messages and responding appropriately. Whenever a client registers or deregisters the server sends and updated list of users out to all online clients. The list of clients is stored in a python dictionary with the client name acting as the key so they can be easily looked up. The data part of the dictionary is an object that stores information about the client including listening port, address, and online status. Updated lists are sent to clients as a long string and a parsed internally and write over the old list.
