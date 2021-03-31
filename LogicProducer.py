import os
import sys
import shutil
import time
from queue import Queue


def pack(packet_id, message):
    return chr(packet_id) + message

#method to separate the message
def unpack(data):
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
        return "Qcreada"
    else:
        q = Queue(maxsize = 0)
        QueuesP[port].append(q)
        print("se añadio una nueva cola en "+str(port))
        return "Qcreada"

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
        return "Qeliminada"
    except:
        return "QE"

def queueMessage(QueuesP, port, message, indice):
    try:
        indiceI = int(indice)
        QueuesP[port][indiceI].put(message)
        print("se añadió el mensaje a la cola "+str(port)+" "+indice)
        print("mensaje",message)
        return "Menviado"
    except:
        return "ME"
