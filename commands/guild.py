import re
from random import randint

import discord
from discord.ext import commands
from discord.utils import get

from commands.mute_control import _add_mute
from constants import roles, channels
from init_bot import bot
from utils.format import box, send_by_bot
from utils.guild_utils import is_spam, get_members_by_role, strip_tot, is_traus
from utils.states import when_all_called


class GuildCommands(commands.Cog, name='Гильдия'):
    """Команды, доступные участникам гильдии с ролью ToT"""

    @commands.command(pass_context=True, name='all',  help='Вызвать всю гильдию ТоТ. '
                                                           'Доступ к команде - Совет, Актив, Наставник. '
                                                           'Злоупотребление наказуемо!')
    @commands.has_any_role("Совет ги", "Актив гильдии", "Наставник")
    async def _all(self, ctx, *message):
        if is_spam(ctx.author, when_all_called, 60) and not is_traus(ctx, ctx.author):
            await ctx.send(box(f'{ctx.author.display_name} получил мут на 5 минут по причине: не злоупотреблять!'))
            await _add_mute(ctx.author, 5*60)
        else:
            all_roles = ctx.guild.roles
            councils = get(all_roles, id=roles.COUNCILS)
            tot = get(all_roles, id=roles.TOT)
            recruit = get(all_roles, id=roles.RECRUIT)
            msg = f'{councils.mention} {tot.mention} {recruit.mention}\n'

            if message:
                msg += ' '.join(message).replace('\\n', '\n')
            else:
                msg += box("Общий сбор!")

            await send_by_bot(ctx, msg, delete=True)

    @commands.command(pass_context=True, name='тлевра',  help='Тлевра и всё, что с ней связано.')
    @commands.has_any_role("Совет ги", "Актив гильдии", "Наставник")
    async def decayra(self, ctx, *time):
        channel: discord.TextChannel = ctx.channel
        decayra_channel = get(ctx.guild.channels, id=channels.DECAYRA)
        if channel != decayra_channel:
            return

        all_roles = ctx.guild.roles
        councils = get(all_roles, id=roles.COUNCILS)
        tot = get(all_roles, id=roles.TOT)
        recruit = get(all_roles, id=roles.RECRUIT)
        pings = f'{councils.mention} {tot.mention} {recruit.mention}'
        pattern = f"Кто идёт, ставим ✅ под сообщением!\n" \
                  f"Группы собираем в пещерах, но не перед входом в 3.1. Бежим тихо."
        msg = f"Тлевра в {' '.join(time)}. {pattern}\n" \
              f"Тактику всем знать наизусть: <#{channels.GUIDES}>"

        if time:
            new_message: discord.Message = await send_by_bot(ctx, f"{pings}\n{msg}", delete=True)
            await new_message.add_reaction('✅')
            for message in await channel.pins():
                if pattern in message.content:
                    await message.unpin()
            await new_message.pin()
        else:
            await ctx.message.delete()
            found = ''
            for message in await channel.pins():
                if pattern in message.content:
                    found = ''.join(re.findall('Тлевра в .*(?=\.)', message.content))
                    break
            await ctx.send(box(found))

    @commands.command(pass_context=True, name='роль', help="Список членов ги с определенной ролью")
    @commands.has_any_role("Совет ги", "ToT")
    async def roles(self, ctx, *role_name):
        tot = get_members_by_role(ctx, name="ToT")
        role = get_members_by_role(ctx, name=' '.join(role_name))
        group = set(role.members)
        if role.role.lower() != "рекрут" and "tavern" not in role.role.lower():
            group = group & set(tot.members)

        message = ''
        for count, member in enumerate(group, 1):
            message += f'{count}. {strip_tot(name=member.display_name)}\n'

        embed = discord.Embed(colour=discord.Color.from_rgb(randint(0, 255), randint(0, 255), randint(0, 255)))
        embed.add_field(name=f'**{role.role}**:', value=message)

        await ctx.send(embed=embed)


bot.add_cog(GuildCommands())
