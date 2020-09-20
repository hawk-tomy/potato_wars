import asyncio
import logging
import logging.config
import os
import sys

import discord
from discord.ext import tasks
from discord.ext import commands
import requests
import yaml

from assets import myfunction as MF
from assets import Help
from assets import config as cfg
from assets.config import config, data, now_session, now_session_cfg

with open('token','r',encoding='utf-8')as f:
    TOKEN = f.read()
with open('logging_config.yml','r',encoding='utf-8')as f:
    logging.config.dictConfig(yaml.safe_load(f))

logger = logging.getLogger('bot')
bot = commands.Bot(command_prefix= '/',help_command=Help())

bot.mode_flag = False
bot.load_extension('assets.administrator_only')
bot.load_extension('assets.user_command')

@bot.event
async def on_ready():
    logger.debug('login success')
    await bot.get_user(612641323631247370).send('起動しました。')

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
async def pkl_clear(ctx):
    cfg.pkl_clear()
    await ctx.send('done')

@bot.command()
async def ping(ctx):
    '''
    ping -> pong
    '''
    await ctx.send('pong')

@bot.command()
@commands.is_owner()
async def kill(ctx):
    '''
    kill this bot
    '''
    logger.info('killing now...')
    cfg.file_close()
    await bot.get_user(612641323631247370).send('killing now...')
    await sys.exit()

@bot.command()
@commands.is_owner()
async def restart(ctx):
    '''
    restart this bot
    '''
    logger.info('restart now...')
    cfg.file_close()
    await bot.get_user(612641323631247370).send('resatrting now...')
    os.execl(sys.executable, os.path.abspath(__file__), os.path.abspath(__file__))

@bot.command()
@commands.is_owner()
async def reload(ctx):
    '''
    reload extension
    '''
    await bot.get_user(612641323631247370).send('reloading now...')
    bot.reload_extension('assets.administrator_only')
    bot.reload_extension('assets.user_command')
    await bot.get_user(612641323631247370).send('reloading success')
    logger.info('reload succes')

bot.run(TOKEN)
