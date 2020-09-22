import logging

import discord
from discord.ext import commands
import requests
import yaml

from assets import myfunction as MF
from assets import config as cfg
from assets.config import config, data, now_session, now_session_cfg

root = logging.getLogger('bot')
logger = root.getChild('test_session_only')

class Test_session_only(commands.Cog):
    """
    公開テスト向けに使用可能なコマンド群です。この鯖でのみ使用可能です。
    """
    def __init__(self,bot):
        self.bot = bot
        logger.debug('load extension success')

    async def cog_check(self,ctx):
        return ctx.guild.id == config['test_guild']

    @commands.group()
    @commands.check(MF.is_member)
    async def test(self,ctx):
        """
        公開テスト向けに使用可能なコマンド群です。詳細は`/help test`
        """
        if ctx.invoked_subcommand is None:
            self.bot.help_command.context = ctx
            await self.bot.help_command.send_group_help(ctx.command)

    @test.command()
    async def country_create(self,ctx,name):
        """
        国家を作成するコマンドです。
        `/test country create [name]`
        [name]
        - 国家の名前です。
        なおこの場合の国家元首は建国した本人です。
        """
        header_id = ctx.message.author.id
        id_ = now_session.country_create(
            name=name,
            header=header_id,
            roles={'header':header_id},
            members= {
                header_id:{'roles':'header'},
            },
            deleted=False,
        )
        now_session.get_member_by_id(header_id).set_country(id_,'header')
        await ctx.send('作成に成功しました。')
        cfg.data_close()

    @commands.command()
    @commands.check(MF.is_mcid_not_set)
    async def mcid_set(self,ctx,mcid):
        """
        公開テストに参加するために必要なコマンドです。
        mcidを設定するコマンドです。
        `/mcid_set [mcid]`
        [mcid]
        - 正しいmcidを指定してください。
        - エラーが返った場合再度実行してください。
        - 登録ができた場合には公開テストに参加できます。
        """
        McidData = None
        if mcid.replace('_','').encode('utf-8').isalnum():
            url = 'https://api.mojang.com/users/profiles/minecraft/' + mcid
            r = requests.get(url)
            if r.status_code == 200:
                r_json = r.json()
                McidData = {'mcid':r_json['name'],'uuid':r_json['id']}
            elif r.status_code == 204:
                await ctx.send("Not Found")
            elif r.status_code == 404:
                await ctx.send("Mojang server is down now.Please wait for minute.")
            else:
                print(r.status_code)
                await ctx.send("Bad request. Please retry.")
        else:
            await ctx.send("You can use A-Za-z0-9_ only.")
        if McidData is None:
            await ctx.send('再度入力してください')
        else:
            data['mcid'][ctx.message.author.id] = McidData
            now_session.member_add(**{
                    'id':ctx.message.author.id,
                    'has_sub':False,
                    'sub_id':None,
                    'is_sub':False,
                    'country':None
                })
            await ctx.send('登録しました。\n実行可能なコマンドが増えました。`/help`を実行してください。')

def setup(bot):
    return bot.add_cog(Test_session_only(bot))