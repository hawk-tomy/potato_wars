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
    通常ユーザーが使用可能になる予定のコマンド群です。
    現在プラグインとの連携機能が未実装のため
    BOTからアクセス可能な情報は少ないです。
    """
    def __init__(self,bot):
        self.bot = bot
        logger.debug('load extension success')

    async def cog_check(self,ctx):
        return MF.is_member(ctx)

    @commands.group()
    async def country(self,ctx):
        """
        国家関連コマンド群 詳細は`/help country`
        `/country`でヘルプが表示されます。
        """
        if ctx.invoked_subcommand is None:
            self.bot.help_command.context = ctx
            await self.bot.help_command.send_group_help(ctx.command)

    @country.command()
    async def show(self,ctx):
        """
        自分の所属する国家の情報の表示
        ※現在は生データで表示されます。※
        """
        c_id = now_session.get_member_by_id(ctx.message.author.id).country['id']
        await ctx.send(str(now_session.get_country_by_id(c_id)))

    @country.command()
    @commands.check(MF.is_headder)
    async def add(self,ctx, *, arg):
        """
        メンションで指定ユーザーを国家に追加する
        `/country add [メンション]`
        [メンション]
        - サブアカウントは指定できません
        - 複数人をメンションすることで同時に指定できます
        """
        if now_session.get_member_by_id(ctx.author.id).is_sub:
            await ctx.send('サブコマンドは指定できません')
        else:
            country_id = now_session.get_member_by_id(ctx.author.id).country['id']
            now_session.country_add_members(country_id,*[m.id for m in ctx.message.mentions])
            cfg.data_close()
            await ctx.send('追加しました。')

def setup(bot):
    return bot.add_cog(User_command(bot))
