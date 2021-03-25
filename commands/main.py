import random
import re
import time
from datetime import datetime

import discord
from discord.ext import commands
from discord.utils import get

from commands.mute_control import _add_mute
from constants import channels, roles
from init_bot import bot
from utils.format import box
from utils.guild_utils import get_member_by_role, is_spam, strip_tot
from utils.statuses import when_all_called


class MainCommands(commands.Cog, name='Основные команды'):
    """Основные команды, доступные каждому"""

    @commands.command(pass_context=True, name='устав', help='Глава устава. Вывод глав устава')
    async def charter(self, ctx, par):
        channel: discord.TextChannel = get(ctx.channel.guild.channels, id=channels.CHARTER)
        messages = await channel.history().flatten()
        text = '\n'.join(message.content for message in messages)
        await ctx.send(box(_get_paragraph(par, text)))

    @commands.command(pass_context=True, help='Номер правила. Вывод правил')
    async def rule(self, ctx, par):
        channel: discord.TextChannel = get(ctx.channel.guild.channels, id=channels.RULES)
        messages = await channel.history(limit=1, oldest_first=True).flatten()
        text = '\n'.join(message.content for message in messages)
        if par == '34':
            await ctx.send(_get_paragraph(2, text))
            await ctx.send(file=discord.File('files/media/34.jpg'))
        else:
            await ctx.send(box(_get_paragraph(par, text)))

    @commands.command(pass_context=True, help='Основные принципы гильдии')
    async def main(self, ctx):
        channel: discord.TextChannel = get(ctx.channel.guild.channels, id=channels.INFO)
        messages = await channel.history(limit=1, oldest_first=True).flatten()
        text = '\n'.join(message.content for message in messages)
        await ctx.send(box(_get_principle(text)))

    @commands.command(pass_context=True, help='Для решения споров. Случайное число от 1 до 100')
    async def roll(self, ctx, num=100):
        await ctx.message.delete()
        await ctx.send(box(f"{ctx.author.display_name} rolled {random.randint(1, num)} from {num}"))

    @commands.command(pass_context=True, name='дейл', help='Узнать, когда обновятся дейлы')
    async def daily(self, ctx):
        start_time = "10/03/2021 00:00"
        first = second = 7 * 60 * 60
        third = 9 * 60 * 60
        stamp = time.mktime(datetime.strptime(start_time, "%d/%m/%Y %H:%M").timetuple())
        now = datetime.timestamp(datetime.utcnow())
        delta = now - stamp
        starts_first = ("Дейлы 7 и 13 уровня начнутся в {} по мск", now + (first - delta % first))
        starts_next = ("Дейл 16 уровня начнётся в {} по мск", now + (third - delta % third))
        if starts_first[1] > starts_next[1]:
            starts_first, starts_next = starts_next, starts_first
        before_dail = starts_first[1] - now

        msg = 'Следующий дейл начнётся через {next_dail}.\n{first}.\n{second}.'.format(
            next_dail=f'{int(before_dail // 3600)} часов {int(before_dail / 60 % 60)} минут {int(before_dail % 60)} секунд',
            first=starts_first[0].format(datetime.fromtimestamp(starts_first[1] + 3600*3)),
            second=starts_next[0].format(datetime.fromtimestamp(starts_next[1] + 3600*3))
        )
        await ctx.channel.send(box(msg))


class CouncilsCommands(commands.Cog, name='Команды совета'):
    """Команды, доступные совету гильдии"""

    @commands.command(name='страйк', help='ник [причина]. Даёт +1 уровень страйка')
    @commands.has_role("Совет ги")
    async def strike(self, ctx, member: discord.Member, *reason):
        reason = ' '.join(reason) or "заслужил"
        all_roles = ctx.guild.roles
        strike_1 = get(all_roles, name='Страйк 1-уровень')
        strike_2 = get(all_roles, name='Страйк 2-уровень')
        strike_3 = get(all_roles, name='Страйк 3-уровень')
        if strike_1 in member.roles:
            await member.remove_roles(strike_1)
            await member.add_roles(strike_2, reason=reason)
            msg = f"{member.display_name} получил {strike_2}. Причина: {reason}.\nСледующий страйк будет причиной вылета из гильдии!"
        elif strike_2 in member.roles:
            await member.remove_roles(strike_2)
            await member.add_roles(strike_3, reason=reason)
            msg = f"{member.display_name} получил {strike_3}. Причина: {reason}.\nСоветом Гильдии будет рассмотрен вопрос об изгнании {member}"
        elif strike_3 in member.roles:
            msg = f"Вопрос об изннании {member.display_name} уже находится на расмотрении Совета Гильдии."
        else:
            await member.add_roles(strike_1, reason=reason)
            msg = f"{member.display_name} получил {strike_1}. Причина: {reason}."
        await ctx.send(box(msg))
        await get(ctx.guild.channels, id=channels.COUNCILS).send(box(msg))  # совет-гильдии

    @commands.command(name='амнистия', help='Снимает 1 уровень страйка')
    @commands.has_role("Совет ги")
    async def remove_strike(self, ctx, member: discord.Member):
        all_roles = ctx.guild.roles
        strike_1 = get(all_roles, name='Страйк 1-уровень')
        strike_2 = get(all_roles, name='Страйк 2-уровень')
        strike_3 = get(all_roles, name='Страйк 3-уровень')
        if strike_1 in member.roles:
            await member.remove_roles(strike_1)
            msg = f"{member.display_name} прощен за хорошее поведение."
        elif strike_2 in member.roles:
            await member.remove_roles(strike_2)
            await member.add_roles(strike_1)
            msg = f"{member.display_name} частично прощен за хорошее поведение."
        elif strike_3 in member.roles:
            await member.remove_roles(strike_3)
            await member.add_roles(strike_2)
            msg = f"{member.display_name} частично прощен за хорошее поведение."
        else:
            msg = f"{member.display_name} и так молодец!"
        await ctx.send(box(msg))
        await get(ctx.guild.channels, id=channels.COUNCILS).send(box(msg))  # совет-гильдии

    @commands.command(pass_context=True, name='список', help='Обновить список членов ги')
    @commands.has_role("Совет ги")
    async def guild_list(self, ctx):
        message = ''
        uniq_users = set()
        leader = get_member_by_role(ctx, name="Глава ги")
        council = get_member_by_role(ctx, name="Совет ги")
        active = get_member_by_role(ctx, name="Актив гильдии")
        tot = get_member_by_role(ctx, name="ToT")
        recruit = get_member_by_role(ctx, name="Рекрут")
        reserve = get_member_by_role(ctx, name="Запас")
        channel = bot.get_channel(channels.LIST)

        count = 0
        for group in (leader, council, active, tot, recruit, reserve):
            message += f"-----------{group.role}-----------\n"
            for i in range(len(group.members)):
                if group.members[i] not in uniq_users:
                    count += 1
                    name = group.members[i].display_name
                    message += f'{count}. {strip_tot(name)}\n'
                    uniq_users.add(group.members[i])
        await ctx.message.delete()
        await channel.purge(limit=1, oldest_first=True)
        await channel.send(message)

    @commands.command(help='ник [время] [причина]. Время в формате число[smhd]')
    @commands.has_permissions(manage_roles=True, ban_members=True, kick_members=True)
    async def mute(self, ctx, user: discord.Member, time: str = '30s', *reason):
        reason = ' '.join(reason) or "заслужил"
        await ctx.send(box(f'{user.display_name} получил мут на {time} по причине: {reason}'))
        await _add_mute(user, time)

    @commands.command(help='Снять мут')
    @commands.has_permissions(manage_roles=True, ban_members=True, kick_members=True)
    async def unmute(self, ctx, user: discord.Member):
        role = user.guild.get_role(roles.MUTED)  # айди роли которую будет получать юзер
        await ctx.send(box(f'Мут снят с {user.display_name}'))
        await user.remove_roles(role)

    @commands.command(pass_context=True, help='Кикнуть с сервера')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member):
        await ctx.guild.kick(member)

    @commands.command(pass_context=True, name='исключить', help='Исключить из гильдии')
    @commands.has_role("Совет ги")
    async def kick_from_guild(self, ctx, member: discord.Member, *reason):
        reason = ' '.join(reason) or "не сложилось"
        await ctx.message.delete()
        kick = False
        guest = get(ctx.guild.roles, name='Гость')
        for role in member.roles:
            if role.name in ['Совет ги', 'ToT', 'Наставник', 'Актив гильдии', 'Рекрут', 'Запас']:
                kick = True
                await member.remove_roles(role)
                await member.add_roles(guest)
        if kick:
            msg = box(f'{ctx.author.display_name} исключил {member.display_name} из гильдии. Причина: {reason}')
            await ctx.send(msg)
            await get(ctx.guild.channels, id=channels.COUNCILS).send(msg)  # совет-гильдии


class GuildCommands(commands.Cog, name='Команды гильдии'):
    """Команды, доступные участникам гильдии с ролью ToT"""

    @commands.command(pass_context=True, help='Вызвать всю гильдию ТоТ. '
                                              'Доступ к команде - Совет, Актив, Наставник. '
                                              'Злоупотребление наказуемо!')
    @commands.has_any_role("Совет ги", "Актив гильдии", "Наставник")
    async def all(self, ctx, *message):
        await ctx.message.delete()
        if is_spam(ctx.author, when_all_called, 60):
            await ctx.send(box(f'{ctx.author.display_name} получил мут на 5 минут по причине: предупреждал же!'))
            await _add_mute(ctx.author, '5m')
        else:
            all_roles = ctx.guild.roles
            councils = get(all_roles, id=roles.COUNCILS)
            tot = get(all_roles, id=roles.TOT)
            recruit = get(all_roles, id=roles.RECRUIT)
            msg = f'{councils.mention} {tot.mention} {recruit.mention}'
            if message:
                msg += box(f'\n{ctx.author.display_name}:\n{" ".join(message)}')
            else:
                msg += box(f'\n{ctx.author.display_name} объявлет общий сбор')
            await ctx.send(msg)

    @commands.command(pass_context=True, name='хай', help="Список хай лвл гильдии")
    @commands.has_any_role("Совет ги", "ToT")
    async def high_lvl(self, ctx):
        group = get_member_by_role(ctx, name="Хай лвл")
        message = ''
        for count, member in enumerate(group.members, 1):
            message += f'{count}. {strip_tot(name=member.display_name)}\n'
        await ctx.send(box(message))

    # @commands.command(pass_context=True, name='алхимик', help="Список алхимиков ToT")
    # @commands.has_any_role("Совет ги", "ToT")
    # async def alchemist(self, ctx):
    #     group = get_member_by_role(ctx, name='💉')
    #     message = ''
    #     for count, member in enumerate(group.members, 1):
    #         message += f'{count}. {strip_tot(name=member.display_name)}\n'
    #     await ctx.send(box(message))


def _get_paragraph(par, text):
    pattern = f'(?<![.\d<]){par}.*'
    res = re.findall(pattern, text)
    return '\n\t'.join(res)


def _get_principle(text):
    pattern = r'Основные принципы гильдии.*'
    res = re.findall(pattern, text)
    return res[0]


bot.add_cog(MainCommands())
bot.add_cog(CouncilsCommands())
bot.add_cog(GuildCommands())
