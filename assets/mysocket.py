import json
import queue
import socket
import threading
import traceback

from assets.config import config
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

logging.getLogger('bot').getChild('socket')
receive_queue = queue.Queue()
send_queue = queue.Queue()
read_line = ''

# 接続先
host = config['host']
port = config['port']
sock.connect((host, port))
waiting_id = []

def switcher(receive_str):
    receive_str_list = receive_str.split('&')
    server = receive_str_list[0]
    data = '&'.join(receive_str_list[1:])
    receive_queue.put()

def Receive_Handler(sock):
    read_line = ''
    while True:
        if not t1.is_alive() and not waiting_id:
            break
        try:
            read = sock.recv(4096)
            if not read:
                continue
            logger.debug('receive :'+read.decode())
            read_line += read.decode()
        except ConnectionError as e:
            logger.error(''.join(traceback.TracebackException.from_exception(e).format()))
            continue
        except Exception as e:
            raise
        read_line_split = read_line.split('@')
        if not len(read_line_split)<1:
            read_line = '@'.join(read_line_split[1:])
            switcher(read_line_split[0])

def Send_Handler(sock, send_queue):
    while True:
        Send_data = send_queue.get()
        if Send_data['server'] != 'server':
            waiting_id.append(Send_data['data']['id'])
        Send_data_str = f"{Send_data['server']}&{json.dumps(Send_data['data'])}@"
        logger.debug('send :'+Send_data_str)
        sock.send(Send_data_str.encode(encoding='utf-8'))
        if Send_data_str == 'server&close@':
            break

t1 = threading.Thread(target = Send_Handler, args= (sock, send_queue))
t2 = threading.Thread(target = Receive_Handler, args= sock)
t1.start()
t2.start()
