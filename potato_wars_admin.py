import asyncio
import logging
import logging.config
import os
import sys

import discord
from discord.ext import commands, tasks
import requests
import yaml

from assets import myfunction as MF
from assets import Help
from assets import config as cfg
from assets.config import config, data, now_session, now_session_cfg, socketRequestFunc
from assets import mysocket
from assets.mysocket import receive_queue, debug_queue

with open('token','r',encoding='utf-8')as f:
    TOKEN = f.read()
with open('logging_config.yml','r',encoding='utf-8')as f:
    logging.config.dictConfig(yaml.safe_load(f))

logger = logging.getLogger('bot')
bot = commands.Bot(command_prefix= '/',help_command=Help())
bot_is_start = False

bot.load_extension('assets.owner_only')
bot.load_extension('assets.administrator_only')
bot.load_extension('assets.user_command')
if config['test']:
    bot.load_extension('assets.test_session_only')

@bot.event
async def on_ready():
    global bot_is_start
    logger.debug('login success')
    appinfo = await bot.application_info()
    bot.owner_id = appinfo.owner.id
    bot_is_start = True
    await bot.get_user(bot.owner_id).send('起動しました。')

@bot.event
async def on_member_join(member):
    if member.guild.id == now_session_cfg['guild'] and not member.bot:
        await member.add_roles(member.guild.get_role(now_session_cfg['role']))
        await member.send('本サーバーではmcidをBOTに登録することで参加することができます。\nmcidを入力してください。')
        data['Mcid_wait_member'].append(member.id)

@bot.event
async def on_message(message):
    global config, data
    if isinstance(message.channel,discord.DMChannel):
        if message.author.id in data['Mcid_wait_member']:
            await MF.McidSet(bot,message,data)
    else:
        if message.author == bot.user:
            return
        if MF.is_administrator(message):
            await MF.mode_embed(message,bot)
        await MF.dispand(message,bot)
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    await MF.reaction_add_or_remove(payload,bot)

@bot.event
async def on_raw_reaction_remove(payload):
    await MF.reaction_add_or_remove(payload,bot)

@bot.command()
@commands.is_owner()
async def kill(ctx):
    '''
    kill
    '''
    logger.info('killing now...')
    mysocket.send_queue.put({'server':'server','data':'close'})
    mysocket.t2.join()
    cfg.file_close()
    await bot.get_user(bot.owner_id).send('killing now...')
    await sys.exit()

@bot.command()
@commands.is_owner()
async def restart(ctx):
    '''
    restart
    '''
    logger.info('restart now...')
    mysocket.send_queue.put({'server':'server','data':'close'})
    mysocket.t2.join()
    cfg.file_close()
    await bot.get_user(bot.owner_id).send('resatrting now...')
    os.execl(sys.executable, os.path.abspath(__file__), os.path.abspath(__file__))

@bot.command()
@commands.is_owner()
async def reload(ctx):
    '''
    reload extension
    '''
    await bot.get_user(bot.owner_id).send('reloading now...')
    bot.reload_extension('assets.owner_only')
    bot.reload_extension('assets.administrator_only')
    bot.reload_extension('assets.user_command')
    if config['test']:
        bot.reload_extension('assets.test_session_only')
    await bot.get_user(bot.owner_id).send('reloading success')
    logger.info('reload succes')

@tasks.loop(seconds=1.0)
async def receive_function():
    if bot_is_start:
        if not receive_queue.empty():
            receive = receive_queue.get()
            if receive[0]:
                function_dict =  socketRequestFunc.get(receive[0],None)
                if function_dict is not None:
                    await function_dict['func'](receive,socketRequestFunc[receive[0]],bot)
                else:
                    logger.warning('Function Is Not Found\n'+receive)
            else:
                await MF.socketEventFunction[receive[1]](receive,bot)

@tasks.loop(seconds=1)
async def loop():
    if bot_is_start:
        if not debug_queue.empty():
            receive = debug_queue.get()
            if receive and not receive in ('server&connection','server&close'):
                channel = bot.get_channel(656070887178502148)
                await channel.send(f'```{receive}```')

@tasks.loop(hours=1.0)
async def re_conection():
    if bot_is_start:
        mysocket.re_conect()

receive_function.start()
re_conection.start()
loop.start()
bot.run(TOKEN)
