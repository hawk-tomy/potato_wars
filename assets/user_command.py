import pprint
import logging

import yaml
import discord
from discord.ext import commands

from assets import myfunction as MF
from assets import config as cfg
from assets.config import config, data, now_session

root = logging.getLogger('bot')
logger = root.getChild('User_command')

class User_command(commands.Cog):
    """
    user command
    """
    def __init__(self,bot):
        self.bot = bot
        logger.debug('loading success')

    @commands.group()
    async def country(self,ctx):
        """
        country command group
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('spam')

    @country.command()
    @commands.check(MF.is_administrator)
    async def create(self,ctx, name, head):
        """
        country create commad
        """
        header_id = ctx.message.mentions[0].id
        header = now_session.get_member_by_id(header_id)
        id_ = now_session.country_create(
            name=name,
            header=header_id,
            roles={'header':header_id},
            members=[
                {**header.return_dict(),**{'roles':'header'}},
            ],
            deleted=False,
        )
        now_session.get_member_by_id(header_id).set_country(id_,'header')
        await ctx.send('create success')
        cfg.data_close()

    @country.command()
    @commands.is_owner()
    async def delete(self,ctx,id):
        """
        country delete command
        """
#        data['wait_delete_country_y/n'] += [ctx.author.id]
#       await ctx.send('本当に削除しますか？削除する場合はyをやめるならnを打ち込んでください。(この操作は1分以内に反応がなければ、無効になります)',after_delete= 60)
        if isinstance(id,int):
            now_session.country_delete(id)
        cfg.data_close()
        await ctx.send('delete success')

    @country.command()
    @commands.check(MF.is_headder)
    async def add(self,ctx, *, arg):
        """
        country add command
        """
        if now_session.get_member_by_id(ctx.author.id).is_sub:
            await ctx.send('this user is sub account')
            return
        country_id = now_session.get_member_by_id(ctx.author.id).country['id']
        now_session.country_add_members(country_id,*[ctx.message.mentions[0].id])
        cfg.data_close()
        await ctx.send('add member is succes')

    @country.group()
    @commands.check(MF.is_administrator)
    async def show(self,ctx):
        """
        country show command group
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('Error missing sub command')

    @show.command()
    @commands.check(MF.is_administrator)
    async def more_info(self,ctx,*,arg):
        """
        send more info
        """
        if arg.isdecimal():
            arg = int(arg)
            await ctx.send(f'```{pprint.pformat(now_session.get_country_by_id(arg),compact=True,width=40)}```')

    @show.command()
    @commands.check(MF.is_administrator)
    async def country_list(self,ctx):
        """
        contry show country list command
        """
        format_string = '`/country show more_info {id}` : `{name}`'
        data_list = [{'id':c.id,'name':c.name} for c in now_session.country]
        defalut_embed = discord.Embed(title='country list',description='詳細な情報は`/country show more_info [num]`で取得してください',color=14563384)
        await MF.embed_paginator(ctx,format_string,data_list,defalut_embed,split_num=1)

def setup(bot):
    return bot.add_cog(User_command(bot))
