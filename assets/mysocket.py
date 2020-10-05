import json
import queue
import socket
import threading

from assets.config import config
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

receive_queue = queue.Queue()
send_queue = queue.Queue()
read_line = ''

# 接続先
host = config['host']
port = config['port']
sock.connect((host, port))

def Receive_Handler(sock):
    global read_line
    while True:
        try:
            read = sock.recv(4096)
            if not read:
                continue
            print('receive :'+read.decode())
            read_line += read.decode()
        except ConnectionError:
            continue
        except Exception:
            raise
        read_line_split = read_line.split('@')
        if not len(read_line_split)<=1:
            read_line = '@'.join(read_line_split[1:])
            receive_queue = read_line_split[0]

def Send_Handler(sock):
    while True:
        your_input = send_queue.get()
        sock.send(your_input.encode(encoding='utf-8'))

t1 = threading.Thread(target = Receive_Handler, args= (sock,))
t2 = threading.Thread(target = Send_Handler, args= (sock,))
t1.start()
t2.start()
