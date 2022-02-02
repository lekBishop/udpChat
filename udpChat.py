#! /usr/bin/python3                                                                                       

import sys                                                                                                
import socket                                                                                             
import threading                                                                                          
import datetime                                                                                           
import time                                                                                               
import os                                                                                                 

# Class stores info for clients that connect to the server                                                
class clientInfo:                                                                                         
    def __init__(self, name, addr, port, status):                                                         
        self.name = name                                                                                  
        self.addr = addr                                                                                  
        self.port = int(port)                                                                             
        self.online = int(status)                                                                         

    def __str__(self):                                                                                    
        return self.name + " " + self.addr + " " + str(self.port) + " " + str(self.online)                

# Check that port is within the allowed range                                                             
def validPort(port):                                                                                      
    return (int(port) <= 65535) and (int(port) >= 1024)                                                   

# Check that new client has a properly formatted IPv4 address and port                                    
def validClient(addr, servport, clientport):                                                              

    #check server IP address                                                                              
    try:                                                                                                  
        socket.inet_pton(socket.AF_INET, addr)                                                            
    except socket.error:                                                                                  
        print("Server IP address error")                                                                  
        return False                                                                                      

    #Check port number                                                                                    
    if not(validPort(servport) and validPort(clientport)):                                                
        print("port numbers should be within the range 1024-65535")                                       
        return False                                                                                      
    return True                                                                                           

# Send the list of clients (active/offline) to all online clients                                         
def broadcastList(socket, clientDict):                                                                    
    clients = clientDict.values();                                                                        
    clientstr = ""                                                                                        

    for data in clients:                                                                                  
        clientstr += str(data) + " "

    clientstr += "*listUpdate*"                                                                           

    for data in clients:                                                                                  
        if data.online:                                                                                   
            socket.sendto(clientstr.encode("utf-8"), (data.addr, data.port))                              

# Reads in clienstr and updates the clients current list of clients                                       
def updateList(clientstr, clientDict):                                                                    
    clients = len(clientstr) // 4                                                                         

    for i in range(clients):                                                                              
        index = i*4                                                                                       
        clientDict.update({clientstr[index]: clientInfo(clientstr[index], clientstr[index+1], clientstr[index+2], clientstr[index+3])})                                                                             

# Method for handling message retrieval                                                                   
def recieveMessage(sock):                                                                                 

    ack = "*ACK*"                                                                                         
    buf = 4096                                                                                            
    global clientDict                                                                                     

    while True:                                                                                           
        sock.setblocking(1)                                                                               
        data, addr = sock.recvfrom(buf)                                                                   
        info = data.decode("utf-8").split()                                                               

        # Check for empty message and ignore it                                                           
        if len(info) < 2:                                                                                 
            time.sleep(.5)                                                                                

        # Check if server sent updated list and update clients list                                       
        elif(info[-1] == "*listUpdate*"):                                                                 
            updateList(info, clientDict)                                                                  
            print("\n>>> [Client table updated.]")                                                        
            print(">>> ",end="")                                                                          
            sys.stdout.flush()                                                                            

        # Message sent by server before offline messages are recieved                                     
        elif data.decode("utf-8") == ">>> You have messages":                                             
            print("\n")                                                                                   
            print(data.decode("utf-8"))                                                                   

        #Retrieve and print offline messages                                                              
        elif info[0] == ">>>" and len(info) > 4:                                                          
            print(data.decode("utf-8"))
            print("")                                                                                                                                                                                                                                                 

        # Retrieve normal message from another client and send ack                                                                                                                                                                                                    
        else:                                                                                                                                                                                                                                                         
            if len(info) > 1:                                                                                                                                                                                                                                         
                msg = data.decode("utf-8")                                                                                                                                                                                                                            
                client = clientDict[info[0][:-1]]                                                                                                                                                                                                                     
                UDP_PORT = client.port                                                                                                                                                                                                                                
                UDP_IP = client.addr                                                                                                                                                                                                                                  
                print("\n>>> " + msg)                                                                                                                                                                                                                                 
                print(">>> ", end="")                                                                                                                                                                                                                                 
                sys.stdout.flush()                                                                                                                                                                                                                                    
                sock.sendto(ack.encode("utf-8"), addr)                                                                                                                                                                                                                

# Method for sending messages and recieving ACKs                                                                                                                                                                                                                      
# Blank data is sent to the server and client to allow this message to retrieve ACK messages instead of recievemessage                                                                                                                                                
def sendMessage(sock, senderName, servaddr, servport):                                                                                                                                                                                                                
    space = " "                                                                                                                                                                                                                                                       
    buf = 4096                                                                                                                                                                                                                                                        
    global clientDict                                                                                                                                                                                                                                                 

    while True:                                                                                                                                                                                                                                                       
        saveMessage = "save-message "                                                                                                                                                                                                                                 
        userInput = input(">>> ")                                                                                                                                                                                                                                     
        msg = userInput.split()                                                                                                                                                                                                                                       

        # Client wants to send a message to another client                                                                                                                                                                                                            
        if  len(msg) > 2 and msg[0] == "send":                                                                                                                                                                                                                        
            reciever = clientDict[msg[1]]                                                                                                                                                                                                                             
            # Remove client dest and "send" from message                                                                                                                                                                                                              
            msg.pop(0)                                                                                                                                                                                                                                                
            msg.pop(0)                                                                                                                                                                                                                                                
            message = senderName + ": "                                                                                                                                                                                                                               
            message += space.join(msg)                                                                                                                                                                                                                                
            # If recieving client is online send it to them                                                                                                                                                                                                           
            if reciever.online:                                                                                                                                                                                                                                       
                recvr = reciever.name                                                                                                                                                                                                                                 
                sock.sendto(space.encode("utf-8"), (servaddr, servport))                                                                                                                                                                                              
                time.sleep(.1)                                                                                                                                                                                                                                        
                sock.sendto(message.encode("utf-8"), (reciever.addr, reciever.port))                                                                                                                                                                                  

            # If client is offline let the user know, format message for offline storage and send to server                                                                                                                                                           
            else:                                                                                                                                                                                                                                                     
                recvr = "server, user offline"                                                                                                                                                                                                                        
                saveMessage = saveMessage + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " " + reciever.name + " " + message                                                                                                                          
                sock.sendto(space.encode("utf-8"), (servaddr, servport))                                                                                                                                                                                              
                time.sleep(.1)                                                                                                                                                                                                                                        
                sock.sendto(saveMessage.encode("utf-8"), (servaddr, servport))                                                                                                                                                                                        

            # When a message is sent, listen for an ACK from the server or client                                                                                                                                                                                     
            sock.settimeout(0.5)                                                                                                                                                                                                                                      
            try:                                                                                                                                                                                                                                                      
                data, addr = sock.recvfrom(buf)                                                                                                                                                                                                                       
                info = data.decode("utf-8")                                                                                                                                                                                                                           
                if info == "*ACK*":                                                                                                                                                                                                                                   
                    print(">>> [Message recieved by " + recvr + ".]")                                                                                                                                                                                                 
            # If the ACK reaches timeout send to the server and wait for another ACK                                                                                                                                                                                  
            # If that fails give up                                                                                                                                                                                                                                   
            except socket.timeout:                                                                                                                                                                                                                                    
                if reciever.online:                                                                                                                                                                                                                                   
                    print(">>> [No ACK from " + reciever.name + ", message sent to server.]")                                                                                                                                                                         
                    sock.sendto(space.encode("utf-8"), (servaddr, servport))                                                                                                                                                                                          
                    time.sleep(.1)                                                                                                                                                                                                                                    
                    sock.sendto(message.encode("utf-8"), (servaddr, servport))                                                                                                                                                                                        
                    sock.settimeout(0.5)                                                                                                                                                                                                                              
                    try:                                                                                                                                                                                                                                              
                        data, addr = sock.recvfrom(buf)                                                                                                                                                                                                               
                        info = data.decode("utf-8")                                                                                                                                                                                                                   
                        if info == "*ACK*":                                                                                                                                                                                                                           
                            print(">>> [Message recieved by " + recvr + ".]")                                                                                                                                                                                         
                    except socket.timeout:                                                                                                                                                                                                                            
                        print(">>> ACK not recieved from server")                                                                                                                                                                                                     
                else:                                                                                                                                                                                                                                                 
                    print(">>> ACK not recieved from server")                                                                                                                                                                                                         

        # If the client wants to deregister let the server know and make sure the client only can dereg itself                                                                                                                                                        
        elif len(msg) == 2 and msg[0] == "dereg" and msg[1] == senderName:                                                                                                                                                                                            
            sock.sendto(space.encode("utf-8"), (servaddr,servport))                                                                                                                                                                                                   
            time.sleep(.1)                                                                                                                                                                                                                                            
            sock.sendto(userInput.encode("utf-8"), (servaddr,servport))                                                                                                                                                                                               

            # The server gets five tries to recieve ACK confirming it was dereg'd                                                                                                                                                                                     
            sock.settimeout(0.5)                                                                                                                                                                                                                                      
            i = 0                                                                                                                                                                                                                                                     
            while i < 5:                                                                                                                                                                                                                                              
                try:                                                                                                                                                                                                                                                  
                    data, addr = sock.recvfrom(buf)                                                                                                                                                                                                                   
                    info = data.decode("utf-8")                                                                                                                                                                                                                       
                    if info == "*ACK*":                                                                                                                                                                                                                               
                        print(">>> [You are offline. Bye.]")                                                                                                                                                                                                          
                        i = 5;                                                                                                                                                                                                                                        
                except socket.timeout:                                                                                                                                                                                                                                
                    if i == 4:                                                                                                                                                                                                                                        
                        print(">>> [Server not responding]")                                                                                                                                                                                                          
                        print(">>> [Exiting]")                                                                                                                                                                                                                        
                        i = 5;                                                                                                                                                                                                                                        
                    if i < 5:                                                                                                                                                                                                                                         
                        sock.sendto(space.encode("utf-8"), (servaddr,servport))                                                                                                                                                                                       
                        time.sleep(.1)                                                                                                                                                                                                                                
                        sock.sendto(userInput.encode("utf-8"), (servaddr,servport))                                                                                                                                                                                   
                    i += 1                                                                                                                                                                                                                                            
        # Ask server to register client again                                                                                                                                                                                                                         
        # Recieve message and server handles if this connection was successful                                                                                                                                                                                        
        elif len(msg) == 2 and msg[0] == "reg":                                                                                                                                                                                                                       
            sock.sendto(userInput.encode("utf-8"), (servaddr, servport))                                                                                                                                                                                              


args = len(sys.argv)                                                                                                                                                                                                                                                  
clientDict = {}                                                                                                                                                                                                                                                       
recvr = ""                                                                                                                                                                                                                                                            

#Server mode                                                                                                                                                                                                                                                          
if args == 3 :                                                                                                                                                                                                                                                        

    UDP_PORT = int(sys.argv[2])                                                                                                                                                                                                                                       
    buf = 1024                                                                                                                                                                                                                                                        
    ack = "*ACK*"                                                                                                                                                                                                                                                     

    servsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                                                                                                                                                                                                       
    servsock.bind(('', UDP_PORT))                                                                                                                                                                                                                                     

    while True:                                                                                                                                                                                                                                                       
        data, addr = servsock.recvfrom(buf)                                                                                                                                                                                                                           
        info = data.decode("utf-8").split()                                                                                                                                                                                                                           

        # If blank message, send back to sender to clean recv buffer                                                                                                                                                                                                  
        if len(info) < 2:                                                                                                                                                                                                                                             
            servsock.sendto(recvr.encode("utf-8"), addr)                                                                                                                                                                                                              

        # Check if client wants to register and is giving valid info                                                                                                                                                                                                  
        elif (info[0] == "reg") and (len(info) == 5) and validClient(addr[0], addr[1], addr[1]) or (info[0] == "reg" and len(info) == 2):                                                                                                                             

            # Make sure the client doesn't already exist or does and was offline
            if (info[1] in clientDict and (not clientDict[info[1]].online)) or info[1] not in clientDict:                                                                                                                                                             
                clientDict.update({info[1]: clientInfo(info[1], addr[0], addr[1], 1)})                                                                                                                                                                                
                broadcastList(servsock, clientDict)                                                                                                                                                                                                                   

                # Check if the client has offline messages and send them                                                                                                                                                                                              
                # Messages are stored per client in a text file                                                                                                                                                                                                       
                fname = info[1] + "_offlineMessages"                                                                                                                                                                                                                  
                try:                                                                                                                                                                                                                                                  
                    with open(fname, "r") as offlineFile:                                                                                                                                                                                                             
                        message = ">>> You have messages"                                                                                                                                                                                                             
                        servsock.sendto(message.encode("utf-8"), addr)                                                                                                                                                                                                
                        message = offlineFile.readline().strip()                                                                                                                                                                                                      
                        while message !='':                                                                                                                                                                                                                           
                            message = ">>> " + message                                                                                                                                                                                                                
                            servsock.sendto(message.encode("utf-8"), addr)                                                                                                                                                                                            
                            message = offlineFile.readline().strip()                                                                                                                                                                                                  
                        offlineFile.close()                                                                                                                                                                                                                           
                        os.remove(fname)                                                                                                                                                                                                                              
                # If the new client has no saved messages we're done                                                                                                                                                                                                  
                except IOError:                                                                                                                                                                                                                                       
                    pass                                                                                                                                                                                                                                              
            # If the client is currenly online, don't allow another client with the same name                                                                                                                                                                         
            else:                                                                                                                                                                                                                                                     
                servsock.sendto(bytes("Client name in use, not registered","utf-8"), (info[2], int(info[3])))                                                                                                                                                         
        # If server recieves a dereg request, set the client to offline and broadcast the new list                                                                                                                                                                    
        elif info[0] == "dereg" and len(info) == 2 and info[1] in clientDict and clientDict[info[1]].online:                                                                                                                                                          
            clientDict[info[1]].online = 0                                                                                                                                                                                                                            
            servsock.sendto(ack.encode("utf-8"), addr)                                                                                                                                                                                                                
            broadcastList(servsock, clientDict)                                                                                                                                                                                                                       

        # If the server recieves a save-message request                                                                                                                                                                                                               
        elif info[0] == "save-message" and len(info) > 4:                                                                                                                                                                                                             

            # If the client is online, let the user know and rebroadcast the list                                                                                                                                                                                     
            if clientDict[info[3]].online:                                                                                                                                                                                                                            
                broadcastList(servsock, clientDict)                                                                                                                                                                                                                   
                message = ">>>  [Client <nick-name> exists!!]"                                                                                                                                                                                                        

            # Otherwise append the message in a file with the offline clients name in it                                                                                                                                                                              
            else:                                                                                                                                                                                                                                                     
                servsock.sendto(ack.encode("utf-8"), addr)                                                                                                                                                                                                            
                fname = info[3]+"_offlineMessages"                                                                                                                                                                                                                    
                data = data.decode("utf-8").split()                                                                                                                                                                                                                   
                data = str(data[1]) + " " + str(data[2]) + " " + " ".join(data[4:])                                                                                                                                                                                   
                data += "\n"                                                                                                                                                                                                                                          
                offlineFile = open(fname,"a")                                                                                                                                                                                                                         
                offlineFile.write(data)                                                                                                                                                                                                                               
                offlineFile.close()                                                                                                                                                                                                                                   

#Client mode                                                                                                                                                                                                                                                          
elif args == 6:                                                                                                                                                                                                                                                       
    #Check for -c                                                                                                                                                                                                                                                     
    if sys.argv[1] != "-c":                                                                                                                                                                                                                                           
        print("-c for client mode")                                                                                                                                                                                                                                   
        sys.exit()                                                                                                                                                                                                                                                    

    #Check valid ip and port                                                                                                                                                                                                                                          
    if not validClient(sys.argv[3], sys.argv[4], sys.argv[5]):                                                                                                                                                                                                        
        print("invalid client info")                                                                                                                                                                                                                                  
        sys.exit()                                                                                                                                                                                                                                                    

    UDP_IP = sys.argv[3]                                                                                                                                                                                                                                              
    UDP_PORT = int(sys.argv[4])                                                                                                                                                                                                                                       
    buf = 1024                                                                                                                                                                                                                                                        

    client = clientInfo(sys.argv[2], socket.gethostbyname(socket.gethostname()), sys.argv[5], 1)                                                                                                                                                                      
    bdata = ("reg " + str(client)).encode()                            

    #Register client over udp                                                                                                                                                                                                                                         
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                                                                                                                                                                                                           
    sock.bind(('', int(sys.argv[5])))                                                                                                                                                                                                                                 
    sock.settimeout(1)                                                                                                                                                                                                                                                
    sock.sendto(bdata, (UDP_IP, UDP_PORT))                                                                                                                                                                                                                            

    # Try to connect to the server                                                                                                                                                                                                                                    
    try:                                                                                                                                                                                                                                                              
        data, addr = sock.recvfrom(buf)                                                                                                                                                                                                                               
        info = data.decode("utf-8").split()                                                                                                                                                                                                                           
        if len(info) == 6:                                                                                                                                                                                                                                            
            print(data.decode())                                                                                                                                                                                                                                      
            sys.exit()                                                                                                                                                                                                                                                
        else:                                                                                                                                                                                                                                                         
            print(">>> [Welcome, You are registered.]")                                                                                                                                                                                                               
            updateList(info, clientDict)                                                                                                                                                                                                                              
            print(">>> [Client table updated.]")                                                                                                                                                                                                                      
    except socket.timeout:                                                                                                                                                                                                                                            
        print("Request Timeout, no response from server")                                                                                                                                                                                                             
        sys.exit()                                                                                                                                                                                                                                                    

    #Threads for sending and recieving data at the same time                                                                                                                                                                                                          
    sending = threading.Thread(target=sendMessage, args=(sock, sys.argv[2], UDP_IP, UDP_PORT,))                                                                                                                                                                       
    recieving = threading.Thread(target=recieveMessage, args=(sock,))                                                                                                                                                                                                 
    sending.start()                                                                                                                                                                                                                                                   
    recieving.start()                                                                                                                                                                                                                                                 

        #Incorrect number of arguments                                                                                                                                                                                                                                
else:                                                                                                                                                                                                                                                                 
    print("Incorrect number of arguments")                                                                                                                                                                                                                            
    print("server: udpChat -s <port>")                                                                                                                                                                                                                                
    print("client: udpChat -c <nick-name> <server-ip> <server-port> <client-port>")
