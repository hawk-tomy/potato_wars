import discord
from discord.ext import commands

class Help(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.no_category = "カテゴリ未設定"
        self.command_attrs["short_doc"] = "このメッセージを表示します。"
        self.command_attrs["help"] = "このBOTのヘルプコマンドです。"
        self.color = 0x54c3f1
        self.description = 'This is POTATO WARS BOT'

    async def create_category_tree(self,category):
        content_line, lv = [], []
        command_list = category.walk_commands()
        for cmd in await self.filter_commands(command_list,sort=False):
            if cmd.root_parent:
                root = ' '.join([i.name for i in cmd.parents[::-1]])
                indent = '-' * cmd.parents.index(cmd.root_parent)
                content_line.append(f"{indent}`{self.context.prefix}{root} {cmd.name}` : {cmd.short_doc}\n")
                lv.append(len(indent))
            else:
                content_line.append(f"`{self.context.prefix}{cmd.name}` : {cmd.short_doc}\n")
                lv.append(0)
        if min(lv):
            for index, line in enumerate(content_line):
                content_line[index] = ''.join(line.split('-'*min(lv))[1:])
        return ''.join(content_line)

    async def send_bot_help(self,mapping):
        embed = discord.Embed(title='helpコマンド', color=self.color)
        if self.description:
            embed.description = self.description
        for cog in mapping:
            if cog:
                cog_name = cog.qualified_name
            else:
                cog_name = self.no_category
            command_list = await self.filter_commands(mapping[cog],sort=True)
            content = ''
            for cmd in command_list:
                    content += f'`{self.context.prefix}{cmd.name}` - {cmd.short_doc}\n'
            if content == '':
                continue
            embed.add_field(name=cog_name,value=content,inline=False)
        embed.set_footer(text= self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self,cog):
        embed = discord.Embed(title=cog.qualified_name,description=cog.description,color=self.color)
        embed.add_field(name="コマンドリスト",value=await self.create_category_tree(cog))
        embed.set_footer(text= self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_group_help(self,group):
        embed = discord.Embed(title=f"{self.context.prefix}{group.qualified_name}",
            description=group.description,color=self.color)
        if group.aliases:
            embed.add_field(name="有効なエイリアス",value="`" + "`, `".join(group.aliases) + "`",inline=False)
        if group.help:
            embed.add_field(name="ヘルプテキスト",value=group.help,inline=False)
        embed.add_field(name="サブコマンドリスト",value=await self.create_category_tree(group),inline=False)
        embed.set_footer(text= self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_command_help(self,command):
        params = " ".join(command.clean_params.keys())
        embed = discord.Embed(title=f"{self.context.prefix}{command.qualified_name} {params}",
            description=command.description,color=self.color)
        if command.aliases:
            embed.add_field(name="有効なエイリアス：",value="`" + "`, `".join(command.aliases) + "`",inline=False)
        if command.help:
            embed.add_field(name="ヘルプテキスト：",value=command.help,inline=False)
        embed.set_footer(text= self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error):
        embed = discord.Embed(title="ヘルプ表示のエラー",description=error,color=self.color)
        embed.set_footer(text= self.get_ending_note())
        await self.get_destination().send(embed=embed)

    def get_ending_note(self):
        command_name = self.invoked_with
        return "{0}{1} [command_name] とすることでコマンドについてのヘルプを閲覧できます。\n" \
               "{0}{1} [category_name] とすることでカテゴリーの詳細情報を閲覧できます。".format(self.clean_prefix, command_name)

    def command_not_found(self,string):
        return f"{string} というコマンドは存在しません。"

    def subcommand_not_found(self,command,string):
        if isinstance(command, commands.Group) and len(command.all_commands) > 0:
            return f"{command.qualified_name} に {string} というサブコマンドは登録されていません。"
        return f"{command.qualified_name} にサブコマンドは登録されていません。"
