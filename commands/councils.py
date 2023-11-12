from datetime import datetime

import discord
from discord.ext import commands
from discord.utils import get

from commands._base_command import Command
from commands._mute_control import _add_mute
from constants import Channels, Roles

from utils.format import box, send_by_bot, create_embed
from utils.guild_utils import get_members_by_role, strip_tot, set_permissions, get_afk_users, is_traus, \
    get_role_by_name, get_reputation_income, get_referenced_author, get_channel, voting
from utils.states import immune_until, user_permissions, muted_queue, drunk_status
from utils.tenor_gifs import find_gif


class CouncilsCommands(Command, name='Совет'):
    """Команды, доступные совету гильдии"""

    @commands.command(name='страйк', help='ник [причина]. Даёт +1 уровень страйка')
    @commands.has_role("Совет ги")
    async def strike(self, ctx, member: discord.Member, *reason):
        await ctx.message.delete()

        if is_traus(member):
            return

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
            msg = f"Вопрос об изгнании {member.display_name} уже находится на расмотрении Совета Гильдии."
        else:
            await member.add_roles(strike_1, reason=reason)
            msg = f"{member.display_name} получил {strike_1}. Причина: {reason}."
        await send_by_bot(ctx, box(msg))
        council_channel = get(ctx.guild.channels, id=Channels.COUNCILS)
        if ctx.channel != council_channel:
            await council_channel.send(box(msg))  # совет-гильдии

    @commands.command(name='амнистия', help='Снимает 1 уровень страйка')
    @commands.has_role("Совет ги")
    async def remove_strike(self, ctx, member: discord.Member):
        await ctx.message.delete()

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
        await send_by_bot(ctx, msg)
        council_channel = get(ctx.guild.channels, id=Channels.COUNCILS)
        if ctx.channel != council_channel:
            await council_channel.send(box(msg))  # совет-гильдии

    @commands.command(pass_context=True, name='список', help='Обновить список членов ги')
    @commands.has_role("Совет ги")
    async def guild_list(self, ctx):
        message = ''
        uniq_users = set()
        leader = get_members_by_role(name="Глава ги")
        council = get_members_by_role(name="Совет ги")
        active = get_members_by_role(name="Актив гильдии")
        tot = get_members_by_role(name="ToT")
        recruit = get_members_by_role(name="Рекрут")
        reserve = get_members_by_role(name="Запас")
        channel = get_channel(Channels.LIST)

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
        await channel.send(box(message))

    @commands.command(help='ник [время] [причина]. Время в формате число[smhd]')
    @commands.has_role("Совет ги")
    async def mute(self, ctx, user: discord.Member, time: str = '30s', *reason):
        await ctx.message.delete()

        day = 60 * 60 * 24
        times = {'s': 1, 'm': 60, 'h': 60 * 60, 'd': day}
        time_1, time_2 = int(time[:-1]), time[-1]
        mute_time = time_1 * times[time_2]
        if mute_time > day:
            mute_time = day
        reason = ' '.join(reason) or "заслужил"

        await ctx.send(box(f'{user.display_name} получил мут на {"24 часа" if mute_time == day else time} по причине: {reason}'))
        await _add_mute(user, mute_time)

    @commands.command(help='Снять мут')
    @commands.has_permissions(manage_roles=True, ban_members=True, kick_members=True)
    async def unmute(self, ctx, user: discord.Member):
        await ctx.message.delete()
        role = user.guild.get_role(Roles.MUTED)  # айди роли которую будет получать юзер
        await ctx.send(box(f'Мут снят с {user.display_name}'))
        await user.remove_roles(role)
        muted_queue.clear()

        channels_with_perms = [Channels.SEKTA, Channels.KEFIR]
        try:
            for channel_id in channels_with_perms:
                await set_permissions(channel_id, user, read_messages=user_permissions[user][channel_id][0],
                                      send_messages=user_permissions[user][channel_id][1])
        except KeyError:
            # unmute before first mute happens
            pass

    @commands.command(pass_context=True, name='принять', help='Принять в гильдию')
    @commands.has_role("Совет ги")
    async def accept(self, ctx, member: discord.Member):
        await ctx.message.delete()
        guest = get(ctx.guild.roles, name='Гость')
        recruit = get(ctx.guild.roles, name='Рекрут')
        alliance = get(ctx.guild.roles, name='Орден')
        await member.add_roles(recruit)
        await member.add_roles(alliance)
        await member.edit(reason='Добро пожаловать', nick=f'[ToT] {member.display_name}')
        await member.remove_roles(guest)
        msg = f'{member.mention}, добро пожаловать в таверну! {self.bot.get_emoji(828026991361261619)}\n' \
              f'Для удобства гильдии и бота, прошу поправить ник по формату: [ToT] Ник-в-игре (Ник дискорд или имя, по желанию).\n' \
              f'А также выбрать себе роли классов, которыми вы играете в {get_channel(Channels.CHOOSE_CLASS).mention}.\n ' \
              f'Обязательно ознакомься с {get_channel(Channels.OTHER_GUILDS).mention}.'
        await get_channel(Channels.GUILD).send(msg)

    @commands.command(pass_context=True, help='Кикнуть с сервера')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member):
        await ctx.guild.kick(member)

    @commands.command(pass_context=True, help='Забанить засранца')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member):
        await ctx.send(find_gif('kick from tavern', limit=1))
        await ctx.guild.ban(member, delete_message_days=0)

    @commands.command(pass_context=True, name='исключить', help='Исключить из гильдии')
    @commands.has_role("Совет ги")
    async def kick_from_guild(self, ctx, member: discord.Member, *reason):
        if is_traus(member):
            return
        reason = ' '.join(reason) or "не сложилось"
        await ctx.message.delete()
        kick = False
        guest = get(ctx.guild.roles, name='Гость')
        for role in member.roles:
            if role.name in [
                'Совет ги',
                'ToT',
                'Наставник',
                'Малый совет',
                'Актив гильдии',
                'Рекрут',
                'Запас',
                'Хай лвл'
                'Орден',
                'Разговор',
                'Страйк 1-уровень',
                'Страйк 2-уровень',
                'Страйк 3-уровень',
            ]:
                kick = True
                await member.remove_roles(role)
                await member.add_roles(guest)
        if kick:
            await member.edit(nick=strip_tot(name=member.display_name))
            msg = box(f'{ctx.author.display_name} исключил {member.display_name} из гильдии. Причина: {reason}')
            await ctx.send(msg)
            await member.send(msg)  # в лс
            await get(ctx.guild.channels, id=Channels.COUNCILS).send(msg)  # совет-гильдии

    @commands.command(name='домик', help='Временный иммунитет от шапалаха')
    @commands.has_any_role("Совет ги")
    async def home(self, ctx, members: commands.Greedy[discord.Member], immune: str = '10'):
        minutes = 10
        if not members:
            author = await get_referenced_author(ctx)
            if author is not None:
                members = [author]
            else:
                members = [ctx.author]

        if is_traus(ctx.author):
            minutes = int(immune)

        for member in set(members):
            stamp = datetime.timestamp(datetime.now()) + minutes*60
            immune_until[member] = stamp
            await ctx.send(box(f'{member.display_name} получает иммунитет на {minutes} минут.'))

    @commands.command(name='бафф', help='Бафф гильдии от шапалаха')
    @commands.has_any_role("Глава ги")
    async def buff(self, ctx):
        tot = get_members_by_role(name="ToT")
        recruit = get_members_by_role(name="Рекрут")

        for member in set(tot.members + recruit.members):
            stamp = datetime.timestamp(datetime.now()) + 60*60
            immune_until[member] = stamp
        await ctx.send(box(f'Таверна получает иммунитет на 60 минут. Перерыв на пиво!'))

    @commands.command(name='наковер', help='вызвать человека на ковер для разговора')
    @commands.has_any_role("Совет ги")
    async def on_carpet(self, ctx, member: discord.Member):
        carpet = get(ctx.guild.roles, name='Разговор')
        await member.add_roles(carpet)
        await get_channel(Channels.CARPET).send(member.mention)

    @commands.command(pass_context=True, help='Совет чистит каналы')
    @commands.has_role("Совет ги")
    async def clean(self, ctx, limit=10):
        await ctx.channel.purge(limit=limit)

    @commands.command(pass_context=True, name='отпуск', help='Уйти/вернуться с отпуска')
    @commands.has_role("Совет ги")
    async def vacation(self, ctx):
        await ctx.message.delete()

        member: discord.Member = ctx.author
        role = get_role_by_name('Отпуск')
        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send(box(f'{member.display_name} вернулся с отпуска'))
        else:
            await member.add_roles(role)
            await ctx.send(box(f'{member.display_name} ушёл в отпуск'))

    @commands.command(pass_context=True, name='пинг', help='Проверка активности гильдии')
    @commands.has_role("Совет ги")
    async def ping(self, ctx, start=None):
        await ctx.message.delete()

        channel: discord.TextChannel = await self.bot.fetch_channel(Channels.PING)
        all_roles = ctx.guild.roles
        councils = get(all_roles, id=Roles.COUNCILS)
        tot = get(all_roles, id=Roles.TOT)
        recruit = get(all_roles, id=Roles.RECRUIT)
        guild_ping = f'{councils.mention} {tot.mention} {recruit.mention}'

        embed_first = create_embed(
            description="Проверка активности гильдии.\n"
                        "Статья Устава 4.3.5 предусматривает выдачу страйка за отсутствие более 7 дней без уважительной причины.\n"
                        "Обязательно поставьте реакцию на данное сообщение - ✅"
        )

        if start is not None and start == 'all':
            await channel.purge()
            msg = await channel.send(guild_ping, embed=embed_first)
            await msg.add_reaction('✅')
        else:
            history = channel.history(oldest_first=True)
            msg: discord.Message = await history.next()
            to_delete = []
            async for m in history:
                to_delete.append(m)
            await channel.delete_messages(to_delete)
            afk_users = await get_afk_users(msg)
            embed_repeat = create_embed(
                description=f"{' '.join([user.mention for user in afk_users])}\n"
                            f"Обязательно отреагируйте на первое сообщение на этом канале!"
            )
            await channel.send(embed=embed_repeat)

    @commands.command(pass_context=True, name='афк', help='Список тех, кто не отметился в пинге')
    @commands.has_role("Совет ги")
    async def check_afk(self, ctx):
        await ctx.message.delete()

        channel: discord.TextChannel = await self.bot.fetch_channel(Channels.PING)
        history = channel.history(oldest_first=True)
        msg: discord.Message = await history.next()
        afk_users = await get_afk_users(msg)

        await ctx.channel.send(box('\n'.join([user.display_name for user in afk_users])))

    @commands.command(pass_context=True, name='пьянь', help='Ушел в запой? Посиди в муте')
    @commands.has_role("Совет ги")
    async def drunk(self, ctx, member: discord.Member = None):
        await ctx.message.delete()

        if member is None:
            member = ctx.author

        role = get_role_by_name('Совет ги')
        drunk = get_role_by_name('В зюзю')

        if drunk_status[member][0] or drunk in member.roles:
            await member.remove_roles(drunk)
            if drunk_status[member][1]:
                await member.add_roles(role)
            await ctx.send(f'{member.mention} с возвращением из запоя! <:pepe_beer:828026991361261619>')
            del drunk_status[member]
        else:
            council = role in member.roles and not is_traus(member)
            if council:
                await member.remove_roles(role)
            await member.add_roles(drunk)
            await send_by_bot(ctx, member.mention+':', find_gif('drunk', 10))
            drunk_status[member] = (True, council)

    @commands.command(pass_context=True, name='вклад', help='Узнать активность членов гильдии')
    @commands.has_role("Глава ги")
    async def income(self, ctx, tax: str = '0'):
        all_income = get_reputation_income(int(tax))
        msg = 'Вклад в гильдию за последнее время:\n'
        for name in sorted(all_income, key=all_income.get, reverse=True):
            msg += f'\n{name} {all_income[name]}'
        await ctx.send(box(msg))


def setup(bot):
    bot.add_cog(CouncilsCommands(bot))
