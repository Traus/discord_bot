from datetime import datetime

import discord
from discord.ext import commands
from discord.utils import get

from commands.mute_control import _add_mute
from constants import channels, roles
from init_bot import bot
from utils.format import box
from utils.guild_utils import get_member_by_role, strip_tot
from utils.statuses import immune_until


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

    @commands.command(name='домик', help='временный иммунитет от шапалаха')
    @commands.has_any_role("Совет ги")
    async def home(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        stamp = datetime.timestamp(datetime.now()) + 10*60
        immune_until[member] = stamp
        await ctx.send(box(f'{member.display_name} получает иммунитет на 10 минут.'))

    @commands.command(pass_context=True, help='Совет чистит каналы')
    @commands.has_role("Совет ги")
    async def clean(self, ctx, limit=10):
        await ctx.channel.purge(limit=limit)


bot.add_cog(CouncilsCommands())
