import os
import sys
import shutil
import time
from queue import Queue

def pack(packet_id, message):
    return chr(packet_id) + message


def unpack(data):
    info = data.split(' ')
    if info[0] == 'connect':
        return info[0], info[1], info[2], info[3]

    elif info[0] == 'pull' or 'list':
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
