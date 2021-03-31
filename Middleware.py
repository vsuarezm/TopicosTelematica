import socket 
import LogicProducer as lp
import LogicConsumer as lc

# import thread module 
from _thread import *
import threading
import sys
import os
import json

print_lock = threading.Lock() # thread function 

def threaded(c, port, QueuesP, QueuesC):
    
    while True:
        login = c.recv(1024)
        data = str(login.decode("utf-8"))
        info = data.split(' ')
        user = info[0]
        password = info[1]
        #user, password = lp.unpack(str(login.decode("utf-8")))

        try:
            f = open("auth.json")
            auth = json.load(f)
            auth = auth[0]
            #autenticación
            if auth[user] == password:
                print(user, ' has logged in' )
                response = user
                c.send(response.encode("utf-8"))

                # identify user type: consumer or producer
                data = c.recv(1024)
                Id = str(data.decode("utf-8"))

                if Id == "1":
                    producer(c, user, QueuesP)
                    break
                if Id == "2":
                    consumer(c, user, QueuesP, QueuesC)
                    break
            else:
                response = "Failed login"
                c.send(response.encode("utf-8"))
        except:
            response = "ERROR! Cannot find, try again"
            print(response, sys.exc_info())
            c.send(response.encode("utf-8"))


def producer(c, port, QueuesP):

    while True: 
        data = c.recv(1024)  # command received from client
        if not data: 
            print('Bye')
            #print_lock.release() # lock released on exit 
            break
        else:
            Id, command, message, indice = lp.unpack(str(data.decode("utf-8")))
            if Id == 'q':
                if command == "create":
                    response = lp.queueCreate(QueuesP, port)
                
                elif command == "list":
                    response = lp.queueList(QueuesP)
                
                elif command == "delete":
                    response = lp.queueDelete(QueuesP, port, indice)
                
                elif command == "message":
                    response = lp.queueMessage(QueuesP, port, message, indice)
                
                c.sendall(response.encode("utf-8"))
                
    # connection closed 
    c.close() 

def consumer(c, port, QueuesP, QueuesC):

    while True: 
        data = c.recv(1024) # command received from client
        if not data: 
            print('Disconected') 
            break

        else:
            command, mode, idq, idp = lc.unpack(str(data.decode("utf-8")))
            if command == 'connect':
                if mode == 'queue':
                    response = lc.c_queue(QueuesP, QueuesC, idq, idp, port)
                else:
                    response = 'Invalid command: Choose queue or channel to connect'
                c.sendall(response.encode("utf-8"))

            elif command == 'pull':
                if mode == 'queue':
                    response = lc.p_queue(QueuesC, port)
                else:
                    response = 'Invalid command: Choose queue or channel to pull'

                c.sendall(response.encode("utf-8"))

            elif command == 'list':
                if mode == 'queue':
                    response = lp.queueList(QueuesP)
                else:
                    response = 'Invalid command: Choose queue or channel to list'
                
                c.sendall(response.encode("utf-8"))
            else:
                response = 'Invalid Command: Command no recognize'
                c.sendall(response.encode("utf-8"))
            
    # connection closed 
    c.close() 


def Main(): 
    #host = "0.0.0.0" 
    host = "localhost" 
    #server port
    #port = 8080
    port = 8000
    #socket created
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    #socket into listening mode
    s.bind((host, port)) 
    print("socket binded to port", port)
    
    s.listen(5) 
    print("socket is listening") 
    QueuesP = {}
    QueuesC = {}

    while True: 

        c, addr = s.accept() # establish connection with client 
        #print_lock.acquire() # lock acquired by client
        print('Connected to :', addr[0], ':', addr[1])
        identification = str(addr[0])+":"+str(addr[1])
        # Start a new thread
        try:
            #hilo para que el servidor siempre permanezca escuchando las conexiones 
            start_new_thread(threaded, (c, identification, QueuesP, QueuesC))
        except:
            continue
    s.close() 


if __name__ == '__main__':
    Main() 
