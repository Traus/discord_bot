import re

import discord
from discord.ext import commands
from discord.utils import get

from constants import channels
from files import charter, rules
from init_bot import bot


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