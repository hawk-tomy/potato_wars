import logging

import discord
from discord.ext import commands
import yaml

from assets import myfunction as MF
from assets import config as cfg
from assets.config import config, data, now_session, now_session_cfg
from assets.data import Session

root = logging.getLogger('bot')
logger = root.getChild('owner_only')

class Owner_only(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        logger.debug('load extension success')

    async def cog_check(self,ctx):
        return await self.bot.is_owner(ctx.message.author)

    @commands.command()
    async def pkl_clear(self,ctx):
        """
        picklデータの初期化。ページめくり機能用データがなくなる。
        """
        cfg.pkl_clear()
        await ctx.send('done')

    @commands.command()
    async def create_session(self,ctx):
        """
        セッションの作成。引数無し。
        """
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
    return bot.add_cog(Owner_only(bot))