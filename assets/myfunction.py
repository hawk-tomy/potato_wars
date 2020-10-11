import logging
import re

import discord
from discord import Embed
import requests
import yaml

from assets import config as cfg
from assets.config import config, data, data_embed, now_session, now_session_cfg

logger = logging.getLogger('bot').getChild('myfunction')

regex_discord_message_url = (
    'https://(ptb.|canary.)?discord(app)?.com/channels/'
    '(?P<guild>[0-9]{18})/(?P<channel>[0-9]{18})/(?P<message>[0-9]{18})'
    )

regex_page_num = r'page:(?P<page>[0-9]+)/[0-9]+'

def is_administrator(ctx):
    return ctx.author.id in config['ID']


def is_header(ctx):
    country_header_list = [c.header for c in now_session.country]
    return ctx.author.id in country_header_list


def is_member(ctx):
    m_dict = now_session.get_member_dict()
    return ctx.message.author.id in m_dict.keys()


def is_mcid_not_set(ctx):
    return not ctx.message.author.id in data['mcid'].keys()


def userName_M(*msg,message):
    return ''.join(msg) + ' - used_by: ' + message.author.name + ' _ ' + str(message.author.id)


def userName_C(*msg,ctx):
    return ''.join(msg) + ' - used_by: ' + ctx.author.name + ' _ ' + str(ctx.author.id)


async def dispand(message,client):
    messages = await extract_messsages(message)
    if not ( messages is None or messages == [] ):
        try:
            for m in messages:
                if message.content:
                    await message.channel.send(embed=compose_embed(m))
                for embed in m.embeds:
                    await message.channel.send(embed=embed)
        except discord.errors.Forbidden as e:
            if message.guild.id == 742290882107277397:
                channel = client.get_channel(742308547110633573)
                error_message = 'Missing Permissions : <#' + str(message.channel.id) +'>'
                await channel.send(error_message)


async def extract_messsages(message):
    messages = []
    for ids in re.finditer(regex_discord_message_url, message.content):
        if message.guild.id != int(ids['guild']):
            return
        fetched_message = await fetch_message_from_id(guild=message.guild, channel_id=int(ids['channel']), message_id=int(ids['message']),)
        messages.append(fetched_message)
    return messages


async def fetch_message_from_id(guild, channel_id, message_id):
    channel = guild.get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    return message


def compose_embed(message):
    embed = Embed(description=message.content, timestamp=message.created_at)
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    embed.set_footer(text=message.channel.name, icon_url=message.guild.icon_url)
    if message.attachments and message.attachments[0].proxy_url:
        embed.set_image(url=message.attachments[0].proxy_url)
    return embed


async def mode_embed(message,bot):
    temp = str(message.guild.id) + '-' + str(message.author.id)
    if temp in data['mode']:
        mode = data['mode'][temp]
        if mode != 'off':
            shortConfig = config['data'][mode]
            pre = await bot.get_prefix(message)
            if isinstance(pre, list):
                pre = str(pre[0])
            tmp = [pre + x for x in config['data'].keys()]+[str(pre+'off')]
            if not message.content in tmp:
                content = ''
                if len(message.mentions) > 0:
                    content += ''.join([str(message.mentions[x].mention) for x in range(len(message.mentions))])
                if len(message.role_mentions) > 0:
                    content += ''.join([str(message.role_mentions[x].mention) for x in range(len(message.role_mentions))])
                files = []
                if len(message.attachments) > 0:
                    for x in range(0,len(message.attachments),1):
                        filename = message.attachments[x].filename
                        download_img(message.attachments[x].url, 'picture/' + filename)
                        files.append(discord.File('picture/' + filename))
                embed = discord.Embed(title= None, description= message.content, color= shortConfig['color'])
                embed.set_author(name = shortConfig['name'] + ' ' + message.author.name ,icon_url = message.author.avatar_url)
                await message.delete()
                if len(files) != 0:
                    await message.channel.send(content= content, embed= embed, files= files)
                else:
                    await message.channel.send(content= content, embed= embed)
    else:
        data['mode'][temp] = 'off'


def download_img(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(r.content)


def getLogger(name, saveName= 'mainnoname.log'):
    def_logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(saveName, encoding='utf-8')
    fh.setFormatter(formatter)
    fh.setLevel(logging.NOTSET)
    def_logger.addHandler(fh)
    return def_logger

#getLogger('bot.myfunction','myfunction.log')

async def embed_paginator(ctx,format_string,data_list=None,defalut_embed=Embed.Empty,split_num=10):
    if data_list is None or defalut_embed is Embed.Empty or type(split_num) is not int:
        raise ValueError
        return None
    embed_dict = {}
    if len(data_list) > split_num:
        all_page_num = len(data_list) // split_num
        for num in range(all_page_num):
            embed_dict[num] = defalut_embed.copy()
            embed_dict[num].set_footer(text=f'page:{num+1}/{all_page_num}')
            temp = data_list[num*split_num:(num+1)*split_num]
            temp = [format_string.format(**i) for i in temp]
            embed_dict[num].add_field(name='––––––––––––––––––––––––––––––',value='\n'.join(temp),inline=True)
        temp = await ctx.send(embed=embed_dict[0])
        data_embed[temp.id] = embed_dict
        cfg.data_embed_close()
        await temp.add_reaction('\U000023ee')
        await temp.add_reaction('\U000025c0')
        await temp.add_reaction('\U000025b6')
        await temp.add_reaction('\U000023ed')
        return embed_dict
    elif len(data_list) != 0:
        embed_dict[0] = defalut_embed.copy()
        temp = data_list[0:10]
        temp = [format_string.format(**i) for i in temp]
        embed_dict[0].add_field(name='––––––––––––––––––––––––––––––',value='\n'.join(temp),inline=True)
        await ctx.send(embed=embed_dict[0])
        return embed_dict
    else:
        embed_dict[0] = defalut_embed.copy()
        embed_dict[0].add_field(name='––––––––––––––––––––––––––––––',value='表示できる情報がありません',inline=True)
        await ctx.send(embed=embed_dict[0])
        return embed_dict


async def reaction_add_or_remove(payload,bot):
        if payload.message_id in data_embed:
            if payload.user_id == bot.user.id:
                return
            channel = bot.get_channel(payload.channel_id)
            temp = await channel.fetch_message(payload.message_id)
            match_ob = re.fullmatch(regex_page_num,temp.embeds[0].footer.text)
            num = int(match_ob['page'])-1
            if payload.emoji.name == '\U000023ee':
                if num == 0:
                    return None
                await temp.edit(embed=data_embed[payload.message_id][0])
            elif payload.emoji.name == '\U000025c0':
                if num == 0:
                    return None
                num_temp = num-1
                await temp.edit(embed=data_embed[payload.message_id][num_temp])
            elif payload.emoji.name == '\U000025b6':
                if num == len(data_embed[payload.message_id])-1:
                    return None
                num_temp = num+1
                await temp.edit(embed=data_embed[payload.message_id][num_temp])
            elif payload.emoji.name == '\U000023ed':
                if num == len(data_embed[payload.message_id])-1:
                    return None
                await temp.edit(embed=data_embed[payload.message_id][len(data_embed[payload.message_id])-1])


async def McidSet(bot,message,data):
    McidData = await McidGet(message)
    if McidData is None:
        await message.channel.send('再度入力してください。')
    else:
        data['Mcid_wait_member'].remove(message.author.id)
        await message.channel.send(f'https://ja.namemc.com/profile/{McidData["mcid"]}\n仮登録しました。運営側担当者の確認が得られ次第サーバーに参加できます。次のBOTからのDMをお待ちください。')
        channel = bot.get_channel(now_session_cfg['OPchannel'])
        prefix = await bot.get_prefix(message)
        send_message = await channel.send(f'discord user : {message.author.mention}\nMCID : {McidData["name"]}\ncommand : {prefix}mcid_add ')
        data['mcid_temp'][send_message.id] = {'mcid':McidData, 'discord_id':message.author.id}
        await send_message.edit(content= send_message.content + ' ' + str(send_message.id))
        cfg.data_close()


async def McidGet(message):
    tmp = message.content
    data = {'namejs': None, 'error': None}
    if tmp.replace('_','').encode('utf-8').isalnum():
        url = 'https://api.mojang.com/users/profiles/minecraft/' + message.content
        r = requests.get(url)
        if r.status_code == 200:
            r_json = r.json()
            return {'mcid':r_json['name'],'uuid':r_json['id']}
        elif r.status_code == 204:
            await message.channel.send("Not Found")
            return None
        elif r.status_code == 404:
            await message.channel.send("Mojang server is down now.Please wait for minute.")
            return None
        else:
            print(r.status_code)
            await message.channel.send("Bad request. Please retry.")
            return None
    else:
        print(tmp)
        await message.channel.send("You can use A-Za-z0-9_ only.")
        return None


def mcid_to_member_list():
    return list(data['mcid'].keys())


def return_uuid_dcit():
    return {v['uuid']:{'discord_id':k,'mcid':v['mcid']} for k,v in data['mcid'].items()}

async def country_create(receive,bot):
    country_dict = now_session.get_country_by_id(receive[2]['country_id']).return_dict()
    embed = (
        discord.Embed(title='建国', description=f'**<@{country_dict["header"]}>が建国しました**', color=14563384)
        .add_field(name='国家の名前', value=country_dict['name'])
        .add_field(name='短い名前', value=country_dict['nick_name'])
    )
    channel = bot.get_channel(now_session_cfg['sendWebsocketEventChannelId'])
    await channel.send(embed=embed)

async def country_delete(receive,bot):
    country_dict = now_session.get_all_country_by_id(receive[2]['country_id']).return_dict()
    embed = discord.Embed(title='国家解体', description=f'**<@{country_dict["header"]}>が国家:{country_dict["name"]}を解体しました**', color=14563384)
    channel = bot.get_channel(now_session_cfg['sendWebsocketEventChannelId'])
    await channel.send(embed=embed)

async def country_member_add(receive,bot):
    country_dict = now_session.get_all_country_by_id(receive[2]['country_id']).return_dict()
    members = '<@'+'>\n<@'.join(receive[2]['members'])+'>'
    embed = (
        discord.Embed(title='国家所属', description=f'**{country_dict["name"]}に所属したユーザー一覧です**', color=14563384)
        .add_field(name='参加したユーザー一覧', value=members)
    )
    channel = bot.get_channel(now_session_cfg['sendWebsocketEventChannelId'])
    await channel.send(embed=embed)

async def country_member_remove(receive,bot):
    country_dict = now_session.get_all_country_by_id(receive[2]['country_id']).return_dict()
    members = '<@'+'>\n<@'.join(receive[2]['members'])+'>'
    embed = (
        discord.Embed(title='国家脱退', description=f'**{country_dict["name"]}から脱退したユーザー一覧です**', color=14563384)
        .add_field(name='脱退したユーザー一覧', value=members)
    )
    channel = bot.get_channel(now_session_cfg['sendWebsocketEventChannelId'])
    await channel.send(embed=embed)

async def country_change_name(receive,bot):
    country_dict = now_session.get_country_by_id(receive[2]['country_id']).return_dict()
    embed = (
        discord.Embed(title='国名変更', description=f'**<@{country_dict["header"]}>が国名を変更しました**', color=14563384)
        .add_field(
            name='国家の名前',
            value=f'`{country_dict["before"]["name"]}` -> `{country_dict["after"]["name"]}`'
            )
        .add_field(
            name='短い名前',
            value=f'`{country_dict["before"]["nick_name"]}` -> `{country_dict["after"]["nick_name"]}`'
            )
    )
    channel = bot.get_channel(now_session_cfg['sendWebsocketEventChannelId'])
    await channel.send(embed=embed)

socketEventFunction = {
    'create':country_create,
    'deleteCountry':country_delete,
    'addmember':country_member_add,
    'removemember':country_member_remove,
    'cangename':country_change_name,
}
