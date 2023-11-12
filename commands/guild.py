import re

import discord
from discord.ext import commands
from discord.utils import get

from commands._base_command import Command
from commands._mute_control import _add_mute
from constants import Roles, Channels

from utils.format import box, send_by_bot, create_embed, edit_new_strings
from utils.guild_utils import is_spam, get_members_by_role, strip_tot, is_traus
from utils.states import when_all_called


class GuildCommands(Command, name='Гильдия'):
    """Команды, доступные участникам гильдии с ролью ToT"""

    @commands.command(pass_context=True, name='all',  help='Вызвать всю гильдию ТоТ. '
                                                           'Доступ к команде - Совет, Актив, Наставник. '
                                                           'Злоупотребление наказуемо!')
    @commands.has_any_role("Совет ги", "Актив гильдии", "Наставник")
    async def _all(self, ctx, *, text: str = ''):
        if is_spam(ctx.author, when_all_called, 60) and not is_traus(ctx.author):
            await ctx.send(box(f'{ctx.author.display_name} получил мут на 5 минут по причине: не злоупотреблять!'))
            await _add_mute(ctx.author, 5*60)
        else:
            all_roles = ctx.guild.roles
            councils = get(all_roles, id=Roles.COUNCILS)
            tot = get(all_roles, id=Roles.TOT)
            recruit = get(all_roles, id=Roles.RECRUIT)
            msg = f'{councils.mention} {tot.mention} {recruit.mention}\n'

            if text:
                msg += edit_new_strings(text)
            else:
                msg += box("Общий сбор!")

            await send_by_bot(ctx, msg, delete=True)

    @commands.command(pass_context=True, name='тлевра',  help='Тлевра и всё, что с ней связано.')
    @commands.has_any_role("Совет ги", "Актив гильдии", "Наставник")
    async def decayra(self, ctx, *time):
        channel: discord.TextChannel = ctx.channel
        decayra_chat = get(ctx.guild.channels, id=Channels.DECAYRA)
        decayra_announce = get(ctx.guild.channels, id=Channels.ANNOUNCE)

        pings = f'@everyone'
        pattern = f"Кто идёт, ставим ✅ под сообщением!\n" \
                  f"Группы собираем в пещерах, но не перед входом в 3.1. Бежим тихо."
        msg = f"Тлевра в {' '.join(time)}. {pattern}\n" \
              f"Тактику всем знать наизусть: <#{Channels.GUIDES}>. Или сообщения выше."

        async def search_for_decayra_message():
            for message in await decayra_announce.history().flatten():
                if pattern in message.content:
                    return message

        if time:
            if channel != decayra_announce:
                return

            message = await search_for_decayra_message()
            if message:
                await message.delete()

            new_message: discord.Message = await send_by_bot(ctx, f"{pings}\n{msg}", delete=True)
            await new_message.add_reaction('✅')

        else:
            if channel != decayra_chat:
                return
            await ctx.message.delete()
            found = ''

            message = await search_for_decayra_message()
            if message:
                found = ''.join(re.findall('Тлевра в .*(?=\.)', message.content))
            await ctx.send(box(found))

    @commands.command(pass_context=True, name='роль', help="Список членов ги с определенной ролью")
    @commands.has_any_role("Совет ги", "ToT")
    async def roles(self, ctx, *role_name):
        tot = get_members_by_role(name="ToT")
        role = get_members_by_role(name=' '.join(role_name))
        group = set(role.members)
        templates = ('рекрут', 'запас', 'tavern', 'состав', 'завсегдатай', 'легенды')
        if not re.compile('|'.join(templates), re.IGNORECASE).search(role.role.lower()):
            group = group & set(tot.members)

        message = ''
        for count, member in enumerate(group, 1):
            message += f'{count}. {strip_tot(name=member.display_name)}\n'

        embed = create_embed(fields=[(f'**{role.role}**:', message)])

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GuildCommands(bot))
