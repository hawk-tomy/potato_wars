import asyncio
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
        ※現在は生データで表示されます※
        """
        c_id = now_session.get_member_by_id(ctx.message.author.id).country['id']
        await ctx.send(str(now_session.get_country_by_id(c_id)))

#    @country.command()
#    @commands.check(MF.is_header)
    async def add(self,ctx, *, arg):
        """
        メンションで指定ユーザーを国家に追加する
        `/country add [mention]`
        [mention]
        - サブアカウントは指定できません
        - 複数人をメンションすることで同時に指定できます
        """
        if now_session.get_member_by_id(ctx.author.id).is_sub:
            await ctx.send('サブアカウントは指定できません')
        else:
            country_id = now_session.get_member_by_id(ctx.author.id).country['id']
            now_session.country_add_members(country_id,*[m.id for m in ctx.message.mentions])
            cfg.data_close()
            await ctx.send('追加しました。')

#    @country.command()
    @commands.check(MF.is_header)
    async def rename(self,ctx,*,arg):
        """
        国名の変更コマンド。
        `/country rename [name]`
        [name]
        - 変更後の国家の名前を指定してください。
        """
        country_id = now_session.get_member_by_id(ctx.author.id).country['id']
        now_session.get_country_by_id(country_id).rename(arg)
        cfg.data_close()
        await ctx.send('名前の変更に成功しました。')

#    @country.command()
    @commands.check(MF.is_header)
    async def remove(self,ctx,*arg):
        """
        国家解体用コマンド。
        `/country remove`
        現在確認コマンドの実行で消去がなされます。
        誤操作等での復帰は現状不可能です。
        """
        if arg:
            return None
        await ctx.send('この操作は取り消せません。本当に削除を行いたい場合は`/coutnry remove confilm`を実行してください。')
        def remove_confirm(msg):
            if msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id:
                return msg.content == '/country remove confilm'
            else:
                return False
        try:
            await self.bot.wait_for('message',check=remove_confirm,timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.send('削除をキャンセルしました。')
        else:
            country_id = now_session.get_member_by_id(ctx.author.id).country['id']
            now_session.country_delete(country_id)
            await ctx.send('削除しました。')
            cfg.data_close()

def setup(bot):
    return bot.add_cog(User_command(bot))
