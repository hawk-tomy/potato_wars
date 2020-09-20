import logging

import discord
from discord.ext import commands
import yaml

from assets import myfunction as MF
from assets import config as cfg
from assets.config import config, data, now_session, now_session_cfg
from assets.data import Session

root = logging.getLogger('bot')
logger = root.getChild('Administrator_only')

class Administrator_only(commands.Cog):
    """
    administrator only
    """
    def __init__(self,bot):
        self.bot = bot
        self.off.update(aliases=list(config['data'].keys()))
        logger.debug('loading success')

    async def cog_check(self,ctx):
        return MF.is_administrator(ctx)

    @commands.command()
    async def off(self,ctx):
        """
        change mode
        """
        tmp = ctx.message.content[len(ctx.prefix):]
        flag = True
        if tmp == 'off':
            embed = discord.Embed(title= '通常モードに変更しました。' ,color=14563384)
        elif tmp in [x for x in config['data'].keys()]:
            embed = discord.Embed(title= config['data'][tmp]['name'] + 'モードに変更しました。' ,color=14563384)
        else:
            flag = False
        if flag:
            await ctx.send(embed=embed,delete_after=5.0)
            temp = str(ctx.guild.id)+'-'+str(ctx.author.id)
            data['mode'][temp] = tmp
            await ctx.message.delete()
            cfg.data_close()
            logger.info(MF.userName_C('mode change', str(temp), ':', ctx.prefix, tmp, ctx=ctx))

    @commands.command()
    async def mcid_add(self,ctx,arg):
        """
        add mcid for database
        <send> : /mcid_add [nummber]
        <return> : success or bad requests
        """
        try:
            arg = int(arg)
        except:
            await ctx.send('コマンドが間違っています。')
            logger.warning(MF.userName_C('add mcid failed',ctx=ctx))
        else:
            if arg in data['mcid_temp']:
                discord_id = data['mcid_temp'][arg]['discord_id']
                data['mcid'][discord_id] = data['mcid_temp'][arg]['mcid']
                data['mcid_temp'].pop(arg)
                now_session.member_add(**{
                    'id':discord_id,
                    'has_sub':False,
                    'sub_id':None,
                    'is_sub':False,
                    'country':None
                })
                await ctx.send('登録しました。',delete_after=10)
                me = await ctx.channel.fetch_message(arg)
                await ctx.message.delete()
                await me.delete()
                await self.bot.get_user(discord_id).send('運営により登録されました。サーバーに参加できます。')
                members = self.bot.get_guild(now_session_cfg['guild']).get_role(now_session_cfg['role']).members
                for i in members:
                    if i.id == discord_id:
                        member = i
                        break
                await member.remove_roles(member.guild.get_role(now_session_cfg['role']))
                channel = self.bot.get_channel(config['sendChannelId'])
                embed = discord.Embed(title=None,description='mcid記入待ちロールを外しました。こちらで発言できます。当サーバーへのご参加ありがとうございます！')
                await channel.send(content=member.mention,embed=embed)
                cfg.data_close()
                logger.info(MF.userName_C('add mcid success', data['mcid'][discord_id], ctx=ctx))
            else:
                await ctx.send('コマンドが間違っています。')
                logger.warning(MF.userName_C('add mcid failed',ctx=ctx))

    @commands.command()
    async def mcid_ignore(self,ctx,arg):
        """
        ignore mcid
        <send> : /mcid_ignore [nummber]
        <return> : success or bad requests
        """
        try:
            arg = int(arg)
        except:
            await ctx.send('コマンドが間違っています')
            logger.warning(MF.userName_C('ignore mcid failed',ctx=ctx))
        else:
            if arg in data['mcid_temp']:
                await ctx.send('却下しました。')
                temp = data['mcid_temp'][arg]['discord_id']
                await self.bot.get_user(temp).send('却下されました。再入力してください。')
                data['mcid_temp'].pop(arg)
                data['wait_mcid'] = temp
                logger.info(MF.userName_C('ignore mcid success',ctx=ctx))
            else:
                await ctx.send('コマンドが間違っています')
                logger.warning(MF.userName_C('ignore mcid failed',ctx=ctx))

    @commands.command()
    @commands.is_owner()
    async def create_session(self,ctx):
        id = len(data['sessions'])
        discord_id_list = MF.mcid_to_member_list()
        guild = bot.get_guild(config['guild'])
        member_list = [member.id for member in guild.members]
        members = []
        for discord_id in discord_id_list:
            if discord_id in member_list:
                members.append({'id':discord_id,'has_sub':False,'sub_id':None,'is_sub':False,'country':None})
        country = []
        data['sessions'].append(Session(**{'id':id,'country':country,'members':members}))

def setup(bot):
    return bot.add_cog(Administrator_only(bot))
