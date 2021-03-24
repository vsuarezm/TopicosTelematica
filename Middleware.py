import socket 
from _thread import *
import threading
import sys
import os

import json

print_lock = threading.Lock() # thread function 

def threaded(c, port, QueuesP, QueuesC):
    
    while True:
        login = c.recv(1024) # 
        data = str(login.decode("utf-8"))
        info = data.split(' ')
        user = info[0]
        password = info[1]
        #user, password = unpackProducer(str(login.decode("utf-8")))

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
                    producer(c, user, QueuesP, ChannelsP, ChannelsC)
                    break
                if Id == "2":
                    consumer(c, user, QueuesP, QueuesC, ChannelsP, ChannelsC)
                    break
            else:
                response = "Failed login"
                c.send(response.encode("utf-8"))
        except:
            response = "ERROR! Cannot find, try again"
            print(response, sys.exc_info())
            c.send(response.encode("utf-8"))

def packConsumer(packet_id, message):
    return chr(packet_id) + message


def unpackConsumer(data):
    info = data.split(' ')
    if info[0] == 'CONNECT':
        return info[0], info[1], info[2], info[3]

    elif info[0] == 'PULL' or 'LIST':
        return info[0], info[1], None, None

    else:
        return 'Error', None, None, None


def c_queue(QueuesP, QueuesC, idq, idp, port):
    try:
        q = QueuesP.get(idq)
        QueuesC[port] = q[int(idp)]
        return 'Conected with queue'
    except:
        return 'Invalid id queue or queue does no exist'

def p_queue(QueuesC, port):
    try:
        q = QueuesC[port]
        m = q.get(True, 3)
        return m
    except:
        return 'Empty queue or you are not connect to a queue'

def unpackProducer(data):
    info = data.split(' ')
    if len(info)==2:    
        return info[0], info[1], 0, 0
    elif "message" in data:
        index = data.index("message")
        return info[0], info[1], data[index+8:-1].strip(), info[-1]
    return info[0], info[1], 0, info[2]

def send(socket, output_data):
    try:
        socket.send(output_data)
    except TypeError:
        socket.send(bytes(output_data, "utf-8"))

def queueCreate(QueuesP, port):
    if port not in QueuesP:
        q = Queue(maxsize = 0)
        QueuesP[port] = [q]
        print("se creo la cola en "+str(port))
        return "QC"
    else:
        q = Queue(maxsize = 0)
        QueuesP[port].append(q)
        print("se añadio una nueva cola en "+str(port))
        return "QC"

def queueList(QueuesP):
    listQ = ""
    for i in QueuesP:
        cont = 0
        for j in QueuesP[i]:
            if not j == False:
                listQ += " -"+i+" "+str(cont)+"\n"
            cont+=1
    return listQ

def queueDelete(QueuesP, port, indice):
    try:
        indiceI = int(indice)
        QueuesP[port][indiceI] = False
        print("se eliminó la cola "+str(port)+" "+indice)
        return "QD"
    except:
        return "QE"

def queueMessage(QueuesP, port, message, indice):
    try:
        indiceI = int(indice)
        QueuesP[port][indiceI].put(message)
        print("se añadió el mensaje a la cola "+str(port)+" "+indice)
        print("mensaje",message)
        return "MA"
    except:
        return "ME"

#method for different producers
def producer(c, port, QueuesP, ChannelsP, ChannelsC):

    while True: 

        data = c.recv(1024)  # command received from client
        if not data: 
            print('Bye')
            #print_lock.release() # lock released on exit 
            break
        else:
            Id, command, message, indice = unpackProducer(str(data.decode("utf-8")))
            if Id == 'q':

                if command == "create":
                    response = queueCreate(QueuesP, port)
                
                elif command == "list":
                    response = queueList(QueuesP)
                
                elif command == "delete":
                    response = queueDelete(QueuesP, port, indice)
                
                elif command == "message":
                    response = queueMessage(QueuesP, port, message, indice)
                
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
            command, mode, idq, idp = unpackConsumer(str(data.decode("utf-8")))
            if command == 'CONNECT':
                if mode == 'QUEUE':
                    response = c_queue(QueuesP, QueuesC, idq, idp, port)
                else:
                    response = 'Invalid command'
                c.sendall(response.encode("utf-8"))
            elif command == 'PULL':
                if mode == 'QUEUE':
                    response = p_queue(QueuesC, port)
                else:
                    response = 'Invalid command'
                c.sendall(response.encode("utf-8"))
            elif command == 'LIST':
                if mode == 'QUEUE':
                    response = queueList(QueuesP)
                else:
                    response = 'Invalid command'
                c.sendall(response.encode("utf-8"))
            else:
                response = 'Invalid Command'
                c.sendall(response.encode("utf-8"))
    # connection closed 
    c.close() 


def Main(): 
    #host = "0.0.0.0" 
    host = "localhost" 
    #port = 8080
    port = 8000
    #socket created
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    #socket into listening mode
    s.bind((host, port)) 
    print("socket binded to port", port)
    
    s.listen(5) 
    print("socket is listening") 
    #diccionario para identificar las colas de cada productor
    #la clave es la direccion ip del productor el valor es una cola(objeto cola)
    QueuesP = {}

    #diccionario para que cada consumidor sepa a que cola esta suscrita
    #la clave es la direccion ip del consumidor el valor es una cola(objeto cola)
    QueuesC = {}

    while True: 
        c, addr = s.accept() # establish connection with client 
        #print_lock.acquire() # lock acquired by client
        print('Connected to :', addr[0], ':', addr[1])
        identification = str(addr[0])+":"+str(addr[1])
        # Start a new thread
        try:
            #hilo para que el servidor siempre permanezca escuchando las conexiones 
            start_new_thread(threaded, (c, identification, QueuesP, QueuesC, ChannelsP, ChannelsC))
        except:
            continue
    s.close() 


if __name__ == '__main__':
    Main() 
