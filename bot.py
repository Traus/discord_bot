import asyncio
import os
import random
import re
from pathlib import Path
from re import split

import discord
from discord.ext import commands
from discord.utils import get

from constants import *
from files import charter, rules

try:
    from loccal_settings import TOKEN
except ImportError:
    TOKEN = os.environ.get("TOKEN")

BAD_WORDS = Path('files/bad_words.txt').read_text(encoding='utf8').split('\n')

bot = commands.Bot(command_prefix='!')


def get_charter(par):
    text = charter.text
    res = re.findall(f'(?<![.]){par}.*', text)
    return '\n\t'.join(res)


def get_rule(par):
    text = rules.text
    res = re.findall(f'(?<![.]){par}.*', text)
    return '\n\t'.join(res)


@bot.command(pass_context=True, help='вывод глав устава')
async def устав(ctx, par):
    await ctx.send(get_charter(par))


@bot.command(pass_context=True, help='вывод правил')
async def rule(ctx, par):
    if par == '34':
        await ctx.send(file=discord.File('files/34.jpg'))
    else:
        await ctx.send(get_rule(par))


@bot.command(pass_context=True)
async def test(ctx, member: discord.Member):
    await ctx.send(f"hello {member.display_name} {member.id}")


@bot.command(pass_context=True, help='для решения споров')
async def roll(ctx, num=100):
    await ctx.message.delete()
    await ctx.send(f"{ctx.author.display_name} rolled {random.randint(1, num)} from {num}")


@bot.command(help='+1 к наказанию')
@commands.has_role("Совет ги")
async def страйк(ctx, member: discord.Member, *reason):
    reason = ' '.join(reason) or "заслужил"
    all_roles = ctx.guild.roles
    strike_1 = get(all_roles, name='Страйк 1-уровень')
    strike_2 = get(all_roles, name='Страйк 2-уровень')
    strike_3 = get(all_roles, name='Страйк 3-уровень')
    msg = None
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
    if msg is not None:
        await ctx.send(msg)
        await get(ctx.guild.channels, id=channels.COUNCILS).send(msg)  # совет-гильдии


@bot.command(help='-1 к наказанию')
@commands.has_role("Глава ги")
async def амнистия(ctx, member: discord.Member):
    all_roles = ctx.guild.roles
    strike_1 = get(all_roles, name='Страйк 1-уровень')
    strike_2 = get(all_roles, name='Страйк 2-уровень')
    strike_3 = get(all_roles, name='Страйк 3-уровень')
    msg = None
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
    if msg is not None:
        await ctx.send(msg)
        await get(ctx.guild.channels, id=channels.COUNCILS).send(msg)  # совет-гильдии


async def add_mute(user: discord.Member, time: str = '30s'):
    times = {'s': 1, 'm': 60, 'h': 60*60, 'd': 60*60*24}
    time_1, time_2 = int(time[:-1]), time[-1]
    role = user.guild.get_role(roles.MUTED)  # айди роли которую будет получать юзер
    await user.add_roles(role)
    await asyncio.sleep(time_1 * times[time_2])
    await user.remove_roles(role)


@bot.command(help='мут, время, причина')
@commands.has_permissions(manage_roles=True, ban_members=True, kick_members=True)
async def mute(ctx, user: discord.Member, time: str = '30s', reason='заслужил'):
    await ctx.send(f'{user.display_name} получил мут на {time} минут по причине: {reason}')
    await add_mute(user, time)


@bot.command(help='анмут')
@commands.has_permissions(manage_roles=True, ban_members=True, kick_members=True)
async def unmute(ctx, user: discord.Member):
    role = user.guild.get_role(roles.MUTED)  # айди роли которую будет получать юзер
    await ctx.send(f'Мут снят с {user.display_name}')
    await user.remove_roles(role)


async def automoderation(message: discord.Message):
    mute = False
    pattern = r'[ !.,?]+'
    for word in split(pattern, message.content):
        if word.lower() in BAD_WORDS:
            mute = True
            break
    if mute:
        try:
            await message.delete()
        except discord.errors.NotFound:
            pass
        await message.channel.send(f'{message.author.display_name} получил мут на 30 секунд')
        await add_mute(message.author)


@bot.command(help='fanatik')
async def fanatik(ctx):
    await ctx.send(f':regional_indicator_f: :regional_indicator_a: :regional_indicator_n: :regional_indicator_a: :regional_indicator_t: :regional_indicator_i: :regional_indicator_k:')


@bot.command(help='rofl')
async def rofl(ctx):
    await ctx.send(f'{ctx.author.display_name} <@{members.ROFL}>`ит')


@bot.command(help='описание команд')
async def info(ctx):
    msg = '**!устав [глава устава]** - для вывода главы устава\n'
    msg += '**!rule [номер правила]** - для вывода правила из канала правил\n'
    msg += '**!roll [макс - опционально]** - для вывода целого числа от 1 до 100 (или макс)\n'
    msg += '**!страйк [Ник] [причина - опционально]** - даёт +1 уровень страйка\n'
    msg += '**!амнистия [Ник]** - отнимает 1 уровень страйка\n'
    msg += '**!mute [Ник] [время] [причина]** - мут. Время в формате [цифра][smhd]\n'
    msg += '**!unmute [Ник]** - снять мут\n'
    await ctx.send(msg)


@bot.event
async def on_message(message: discord.Message):
    if message.channel.id not in (channels.REQUEST, channels.JOIN):
        await automoderation(message)

    if message.channel.id == channels.JOIN:  # вступление-в-гильдию
        inv_gi_channel: discord.TextChannel = get(message.channel.guild.channels, id=channels.REQUEST)  # заявки-в-ги
        message.content = f"{'-' * 30}\n<@{message.author.id}>\n{message.content}\n{'-' * 30}"
        await inv_gi_channel.send(f'{message.content}')
        await message.delete()
    await bot.process_commands(message)


bot.run(TOKEN)
