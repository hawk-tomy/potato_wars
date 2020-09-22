import logging

import discord
from discord.ext import commands
import yaml

from assets import myfunction as MF
from assets import config as cfg
from assets.config import config, data, now_session, now_session_cfg

root = logging.getLogger('bot')
logger = root.getChild('Administrator_only')

class Administrator_only(commands.Cog):
    """
    管理者専用のコマンド群です。
    discord上での国家作成等を行えます。
    """
    def __init__(self,bot):
        self.bot = bot
        self.off.update(aliases=list(config['data'].keys()))
        logger.debug('load extension success')

    async def cog_check(self,ctx):
        return MF.is_administrator(ctx)

    @commands.command()
    async def off(self,ctx):
        """
        adminモード等を実装してます。
        エイリアス表示されている単語がモードです。
        offは通常モードに切り替えます。
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
        申請されたmcidを追加します。
        `/mcid_add [nummber]`
        (基本的にはBOTが自動送信したメッセージからのコピペで使用します)
        コマンドが間違っていると返った場合、大体はコピペミスです。
        成功した場合、登録しましたと出ます。
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
        申請されたmcidを差し戻します。
        `/mcid ignore [number]`
        (このコマンドはBOTが自動送信した申請メッセージを却下する際に使用します。
        command : となっている部分の最後の部分の数字を[number]に当てはめて使用してください。)
        コマンドが間違っていると返った場合、大体は[number]のコピペミスです。
        成功した場合、却下しましたと出ます。
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

    @commands.group()
    async def op(self,ctx):
        """
        管理用コマンド群です。
        """
        if ctx.invoked_subcommand is None:
            self.bot.help_command.context = ctx
            await self.bot.help_command.send_group_help(ctx.command)

    @op.group()
    async def country(self,ctx):
        """
        国家管理用コマンド群です
        """
        if ctx.invoked_subcommand is None:
            self.bot.help_command.context = ctx
            await self.bot.help_command.send_group_help(ctx.command)

    @country.command()
    async def create(self,ctx,name,head):
        """
        国家の手動作成です。
        ※plugin連携がされていない場合マイクラ鯖内では作成されません。※
        `/op country [name] [header]`
        [name]
        - 国家の名前を入れてください。
        [header]
        - 国家元首に当たるユーザーをメンションしてください。
        """
        header_id = ctx.message.mentions[0].id
        if now_session.get_member_dict().get(header_id) is None:
            await ctx.send('メンバーを指定してください。')
        else:
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
            await ctx.send('作成に成功しました。')
            cfg.data_close()

    @country.command()
    async def delete(self,ctx,id):
        """
        国家を削除します。
        `/op country delete [country id]`
        [country id]
        - `/op show country_list`で得られる数字を指定してください。
        """
        try:
            id = int(id)
        except:
            await ctx.send('コマンドが間違っています。')
        else:
            now_session.country_delete(id)
            cfg.data_close()
            await ctx.send('削除しました。')

    @op.group()
    async def show(self,ctx):
        """
        管理者向け情報表示コマンド群です。
        """
        if ctx.invoked_subcommand is None:
            self.bot.help_command.context = ctx
            await self.bot.help_command.send_group_help(ctx.command)

    @show.command()
    async def more_info(self,ctx,*,arg):
        """
        指定国家の詳細情報を表示します。
        `/op show more_info [id]`
        [id]
        - `/op show country_list`で得られる数字を指定してください。
        ※現在は生データで表示されます。※
        """
        if arg.isdecimal():
            arg = int(arg)
            await ctx.send(f'```{pprint.pformat(now_session.get_country_by_id(arg),compact=True,width=40)}```')

    @show.command()
    async def country_list(self,ctx):
        """
        国家の一覧を表示します。
        詳細情報を得るためのコマンド : 国家名
        が表示されます。
        """
        format_string = '`/country show more_info {id}` : `{name}`'
        data_list = [{'id':c.id,'name':c.name} for c in now_session.country if not c.deleted]
        defalut_embed = discord.Embed(title='country list',description='詳細な情報は`/country show more_info [num]`で取得してください',color=14563384)
        await MF.embed_paginator(ctx,format_string,data_list,defalut_embed,split_num=1)

def setup(bot):
    return bot.add_cog(Administrator_only(bot))
