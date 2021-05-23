from datetime import datetime

import discord
from discord.ext import commands
from discord.utils import get

from commands.mute_control import _add_mute
from constants import channels, roles
from init_bot import bot
from utils.format import box, send_by_bot
from utils.guild_utils import get_member_by_role, strip_tot, set_permissions, get_afk_users
from utils.states import immune_until, user_permissions, muted_queue
from utils.tenor_gifs import find_gif


class CouncilsCommands(commands.Cog, name='Совет'):
    """Команды, доступные совету гильдии"""

    @commands.command(name='страйк', help='ник [причина]. Даёт +1 уровень страйка')
    @commands.has_role("Совет ги")
    async def strike(self, ctx, member: discord.Member, *reason):
        await ctx.message.delete()

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
        council_channel = get(ctx.guild.channels, id=channels.COUNCILS)
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
        council_channel = get(ctx.guild.channels, id=channels.COUNCILS)
        if ctx.channel != council_channel:
            await council_channel.send(box(msg))  # совет-гильдии

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
        await channel.send(box(message))

    @commands.command(help='ник [время] [причина]. Время в формате число[smhd]')
    @commands.has_permissions(manage_roles=True, ban_members=True, kick_members=True)
    async def mute(self, ctx, user: discord.Member, time: str = '30s', *reason):
        await ctx.message.delete()
        reason = ' '.join(reason) or "заслужил"
        await ctx.send(box(f'{user.display_name} получил мут на {time} по причине: {reason}'))
        await _add_mute(user, time)

    @commands.command(help='Снять мут')
    @commands.has_permissions(manage_roles=True, ban_members=True, kick_members=True)
    async def unmute(self, ctx, user: discord.Member):
        await ctx.message.delete()
        role = user.guild.get_role(roles.MUTED)  # айди роли которую будет получать юзер
        await ctx.send(box(f'Мут снят с {user.display_name}'))
        await user.remove_roles(role)
        muted_queue.clear()

        channels_with_perms = [channels.MERY, channels.KEFIR]
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
        await member.add_roles(recruit)
        await member.remove_roles(guest)
        msg = f'{member.mention}, добро пожаловать в таверну! {bot.get_emoji(828026991361261619)}\n' \
              f'Для удобства гильдии и бота, прошу поправить ник по формату: [ToT] Ник-в-игре (Ник дискорд или имя, по желанию).\n' \
              f'А также выбрать себе роли классов, которыми вы играете в {bot.get_channel(channels.CHOOSE_CLASS).mention}' \
              f'\n\n' \
              f'**Очень важно**: зайди, пожалуйста, на {bot.get_channel(channels.PING).mention} и поставь ✅ под первым сообщением.'
        await bot.get_channel(channels.GUILD).send(msg)

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
        reason = ' '.join(reason) or "не сложилось"
        await ctx.message.delete()
        kick = False
        guest = get(ctx.guild.roles, name='Гость')
        for role in member.roles:
            if role.name in [
                'Совет ги',
                'ToT',
                'Наставник',
                'Зазывала',
                'Актив гильдии',
                'Рекрут',
                'Запас',
                'Хай лвл'
                'Разговор'
                'Страйк 1-уровень'
                'Страйк 2-уровень'
                'Страйк 3-уровень'
            ]:
                kick = True
                await member.remove_roles(role)
                await member.add_roles(guest)
        if kick:
            msg = box(f'{ctx.author.display_name} исключил {member.display_name} из гильдии. Причина: {reason}')
            await ctx.send(msg)
            await member.send(msg)  # в лс
            await get(ctx.guild.channels, id=channels.COUNCILS).send(msg)  # совет-гильдии

    @commands.command(name='домик', help='временный иммунитет от шапалаха')
    @commands.has_any_role("Совет ги")
    async def home(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        stamp = datetime.timestamp(datetime.now()) + 10*60
        immune_until[member] = stamp
        await ctx.send(box(f'{member.display_name} получает иммунитет на 10 минут.'))

    @commands.command(name='наковер', help='вызвать человека на ковер для разговора')
    @commands.has_any_role("Совет ги")
    async def on_carpet(self, ctx, member: discord.Member):
        carpet = get(ctx.guild.roles, name='Разговор')
        await member.add_roles(carpet)
        await bot.get_channel(channels.CARPET).send(member.mention)

    @commands.command(pass_context=True, help='Совет чистит каналы')
    @commands.has_role("Совет ги")
    async def clean(self, ctx, limit=10):
        await ctx.channel.purge(limit=limit)

    @commands.command(pass_context=True, name='пинг', help='Проверка активности гильдии')
    @commands.has_role("Совет ги")
    async def ping(self, ctx, start=None):
        await ctx.message.delete()

        channel: discord.TextChannel = await bot.fetch_channel(channels.PING)
        all_roles = ctx.guild.roles
        councils = get(all_roles, id=roles.COUNCILS)
        tot = get(all_roles, id=roles.TOT)
        recruit = get(all_roles, id=roles.RECRUIT)
        guild_ping = f'{councils.mention} {tot.mention} {recruit.mention}'

        embed_first = discord.Embed(
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
            embed_repeat = discord.Embed(
                description=f"{' '.join([user.mention for user in afk_users])}\n"
                            f"Обязательно отреагируйте на первое сообщение на этом канале!"
            )
            await channel.send(embed=embed_repeat)

    @commands.command(pass_context=True, name='афк', help='Список тех, кто не отметился в пинге')
    @commands.has_role("Совет ги")
    async def check_afk(self, ctx):
        await ctx.message.delete()

        channel: discord.TextChannel = await bot.fetch_channel(channels.PING)
        history = channel.history(oldest_first=True)
        msg: discord.Message = await history.next()
        afk_users = await get_afk_users(msg)

        await ctx.channel.send(box('\n'.join([user.display_name for user in afk_users])))


bot.add_cog(CouncilsCommands())
