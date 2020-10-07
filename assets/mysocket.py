import json
import queue
import socket
import threading
import traceback

from assets import myfunction as MF
from assets.config import config, now_session
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

def country_create(receive_data):
    receive_data['data']['country'] = json.loads(receive_data['data']['country'])
    head = MF.return_uuid_dict()['data']['country']['head']
    member = [MF.return_uuid_dict()[m] for m in receive_data['data']['country']['member']]
    country_id = int(receive_data['data']['country']['taag'][3:])
    country_dict ={
        'name':receive_data['data']['country']['name'],
        'nick_name':receive_data['data']['country']['nickname'],
        'members':member,
        'id':country_id,
    }
    now_session.country_create(**country_data)
    return receive_data,country_id

def country_delete(receive_data):
    receive_data['data']['country'] = json.loads(receive_data['data']['country'])
    country_id = receive_data['data']['country']['tag'][3:]
    now_session.country_delete(coutnry_id)
    return receive_data,country_id

def country_change_name(receive_data):
    receive_data['data']['country'] = json.loads(receive_data['data']['country'])
    country_id = receive_data['data']['country']['tag'][3:]
    name = receive_data['data']['country']['name']
    nick_name = receive_data['data']['country']['nickname']
    now_session.get_country_by_id(country_id).rename(name.nick_name)
    return receive_data,country_id

def country_member_add(receive_data):
    receive_data['data']['country'] = json.loads(receive_data['data']['country'])
    country_id = receive_data['data']['country']['tag'][3:]
    b_m = now_session.get_country_by_id(country_id).members.keys()
    add_member = [p_m  for p_m in receive_data['data']['country']['member'] if p_m not in b_m]
    now_session.country_add_members(country_id,**addmember)
    return receive_data,country_id

def country_member_remove(receive_data):
    receive_data['data']['country'] = json.loads(receive_data['data']['country'])
    country_id = receive_data['data']['country']['tag'][3:]
    p_m = receive_data['data']['country']['member']
    remove_member = [ b_m for b_m in now_session.get_country_by_id(country_id).members.keys() if b_m not in p_m]
    now_session.country_remove_members(country_id,**remove_member)
    return receive_data,country_id

function_dict = {'create':country_create,'deleteCountry':country_delete,'addmember':country_member_add,'removemember':country_member_remove,'cangename':country_change_name}

def switcher(receive_str):
    receive_str_list = receive_str.split('&')
    server = receive_str_list[0]
    raw_data = '&'.join(receive_str_list[1:])
    receive_data =json.loads(raw_data)
    if receive_data['id']:
        return_receive = False
    else:
        return_receive = function_dict[receive_data['type']](receive_data)
    receive_queue.put(return_receive)

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
