from contextlib import asynccontextmanager
from typing import Union

import discord
from discord.ext import commands

from init_bot import bot
from utils.format import box
from utils.guild_utils import set_permissions
from utils.statuses import voice_owners

docs = dict(
    lock="!nv lock - Закрыть канал.",
    unlock="!nv unlock - Открыть канал.",
    invite="!nv invite @роль или @имя - Выдать право присоединяться к каналу.",
    remove="!nv remove @роль или @имя - Кикнуть и отобрать право присоединяться к каналу.",
    rename="!nv rename новое имя - Переименовать канал.",
    limit="!nv limit число - Ограничить число участников.",
    help="!nv help или !nv - Вызов справки.",
)

_pattern = '{:<30}-{}'
doc_text = """Для использования команд необоходимо подключиться к приватному голосовому каналу.

Список доступных команд:
{}

Обратите внимание, что имя каналу можно менять не чаще 2х раз за 10 минут (ограничения дискорда)
""".format('\n'.join(_pattern.format(*value.split(' - ')) for value in docs.values()))


@asynccontextmanager
async def check_owner(ctx):
    if voice_owners[ctx.author.voice.channel] != ctx.author:
        await ctx.send(box(f'Владелец канала - {voice_owners[ctx.author.voice.channel].display_name}'))
        return
    yield


async def join_channel(ctx):
    await ctx.channel.send(box("Сначала необходимо подключиться к приватному голосовому каналу!"))


class NewVocCommands(commands.Cog, name='Голос', description="Управление приватными голосовыми каналами"):
    # todo ограничение по вызовыу команд
    @commands.group(pass_context=True, help="Возможные команды после !nv - lock, unlock, invite @user/@role, remove @user/@role, rename [name], limit [number]")
    async def nv(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(box(doc_text))
            return
        if ctx.author.voice is None:
            return await join_channel(ctx)

    @nv.command(help=docs['lock'])
    async def lock(self, ctx):
        member: discord.Member = ctx.author

        async with check_owner(ctx):
            await ctx.send(box(f'{member.voice.channel.name} закрыт'))
            for role in member.guild.roles:
                await set_permissions(member.voice.channel.id, role, connect=False)

    @nv.command(help=docs['unlock'])
    async def unlock(self, ctx):
        member: discord.Member = ctx.author

        async with check_owner(ctx):
            await ctx.send(box(f'{member.voice.channel.name} открыт'))
            for role in member.guild.roles:
                await set_permissions(member.voice.channel.id, role, connect=True)

    @nv.command(help=docs['invite'])
    async def invite(self, ctx, target: Union[discord.Member, discord.Role]):
        member: discord.Member = ctx.author
        channel: discord.VoiceChannel = member.voice.channel

        if isinstance(target, discord.Member):
            name = 'display_name'
        elif isinstance(target, discord.Role):
            name = 'name'
        else:
            await ctx.send(box(docs['invite']))
            return
        await set_permissions(channel.id, target, connect=True)
        await ctx.send(box(f"{getattr(target, name)} пригалашен на {channel.name}"))

    @nv.command(help=docs['remove'])
    async def remove(self, ctx, target: Union[discord.Member, discord.Role]):
        member: discord.Member = ctx.author
        channel: discord.VoiceChannel = member.voice.channel

        if isinstance(target, discord.Member):
            name = 'display_name'
            await target.move_to(None)
        elif isinstance(target, discord.Role):
            name = 'name'
            users = channel.members
            for user in users:
                if target in user.roles:
                    await user.move_to(None)
        else:
            await ctx.send(box(docs['remove']))
            return
        await set_permissions(channel.id, target, connect=False)
        await ctx.send(box(f"{getattr(target, name)} удален с {channel.name}"))

    @nv.command(help=docs['rename'])
    async def rename(self, ctx, *name):
        async with check_owner(ctx):
            await ctx.author.voice.channel.edit(name=' '.join(name))

    @nv.command(help=docs['limit'])
    async def limit(self, ctx, new_limit: int):
        async with check_owner(ctx):
            await ctx.author.voice.channel.edit(user_limit=int(new_limit))


bot.add_cog(NewVocCommands())
