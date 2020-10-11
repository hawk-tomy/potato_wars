import pickle
from pprint import pprint

import yaml

from assets.data import Session

with open('config.yml','r',encoding='utf-8')as _f:
    config = yaml.safe_load(_f)
with open('data.yml','r',encoding='utf-8')as _f:
    data = yaml.safe_load(_f)
with open('data_embed.pkl','rb')as _f:
    data_embed = pickle.load(_f)
if data['sessions']:
    pprint(data)
    now_session = Session(**data['sessions'][config['now_session_id']])
    pprint(now_session)
    now_session_cfg = config['sessions'][config['now_session_id']]
socketRequestFunc = {}

def return_dict():
    data['sessions'][config['now_session_id']] = now_session.return_dict()

def file_close():
    return_dict()
    with open('config.yml','w',encoding='utf-8')as _f:
        yaml.dump(config, _f, default_flow_style=False, encoding='utf-8', allow_unicode=True)
    with open('data.yml','w',encoding='utf-8')as _f:
        yaml.dump(data, _f, default_flow_style=False, encoding='utf-8', allow_unicode=True)
    with open('data_embed.pkl','wb')as _f:
        pickle.dump(data_embed, _f, pickle.HIGHEST_PROTOCOL)

def data_close():
    return_dict()
    with open('data.yml','w',encoding='utf-8')as _f:
        yaml.dump(data, _f, default_flow_style=False, encoding='utf-8', allow_unicode=True)

def data_embed_close():
    with open('data_embed.pkl','wb')as _f:
        pickle.dump(data_embed, _f, pickle.HIGHEST_PROTOCOL)

def pkl_clear():
    with open('data_embed.pkl','wb')as _f:
        pickle.dump({}, _f, pickle.HIGHEST_PROTOCOL)
        data_embed = {}
