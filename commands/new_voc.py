import re

import discord
from discord.ext import commands

from constants import categories, roles
from init_bot import bot
from utils.format import box
from utils.guild_utils import set_permissions

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


async def join_channel(text_channel):
    await text_channel.send(box("Сначала необходимо подключиться к приватному голосовому каналу!"))


class NewVocCommands(commands.Cog, name='Управление приватными голосовыми каналами', description=doc_text):

    @commands.command(help=doc_text)
    async def nv(self, ctx, command: str = 'help', *args):
        member: discord.Member = ctx.author
        text_channel: discord.TextChannel = ctx.channel
        if member.voice is None:
            await join_channel(ctx)
            return
        channel: discord.VoiceChannel = member.voice.channel

        async def lock(*args):
            for role in member.guild.roles:
                await set_permissions(channel.id, role, connect=False)

        async def unlock(*args):
            for role in member.guild.roles:
                await set_permissions(channel.id, role, connect=True)

        async def invite(*args):
            if not args:
                await text_channel.send(box(docs['invite']))
            else:
                obj = args[0]
                if '!' in obj:
                    obj_type = 'get_member'
                else:
                    obj_type = 'get_role'
                obj_id = int(re.findall(r'\d+', obj)[0])
                tg = getattr(ctx.guild, obj_type)(obj_id)
                await set_permissions(channel.id, tg, connect=True)
                await text_channel.send(box(f"{tg.display_name if obj_type == 'get_member' else tg.name} "
                                            f"пригалашен на {channel.name}"))

        async def remove(*args):
            if not member:
                await text_channel.send(box(docs['remove']))
            else:
                obj = args[0]
                if '!' in obj:
                    obj_type = 'get_member'
                else:
                    obj_type = 'get_role'
                obj_id = int(re.findall(r'\d+', obj)[0])
                tg = getattr(ctx.guild, obj_type)(obj_id)
                await set_permissions(channel.id, tg, connect=False)
                if obj_type == 'get_member':
                    await tg.move_to(None)
                    await text_channel.send(box(f"{tg.display_name} удален с {channel.name}"))
                else:
                    await text_channel.send(box(f"{tg.name} удален с {channel.name}"))
                    users = channel.members
                    for user in users:
                        if tg in user.roles:
                            await user.move_to(None)

        async def rename(*name):
            if not name:
                await text_channel.send(box(docs['rename']))
            else:
                await channel.edit(name=' '.join(name))

        async def limit(new_limit: int, *args):
            if not new_limit:
                await text_channel.send(box(docs['limit']))
            else:
                await channel.edit(user_limit=int(new_limit))

        async def _help(*args):
            await text_channel.send(box(doc_text))

        commands_dict = dict(
            lock=lock,
            unlock=unlock,
            invite=invite,
            remove=remove,
            rename=rename,
            limit=limit,
            help=_help,
        )

        if channel.category_id != categories.PRIVATE:
            await join_channel(ctx)
        else:
            await commands_dict.get(command, _help)(*args)


bot.add_cog(NewVocCommands())
