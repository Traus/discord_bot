import random
import re

import discord
from discord.ext import commands
from discord.utils import get

from constants import channels
from init_bot import bot
from utils.guild_utils import get_member_by_role


def _get_paragraph(par, text):
    pattern = f'(?<![.\d<]){par}.*'
    res = re.findall(pattern, text)
    return '\n\t'.join(res)


def _get_principle(text):
    pattern = r'Основные принципы гильдии.*'
    res = re.findall(pattern, text)
    return res[0]


@bot.command(pass_context=True, help='вывод глав устава')
async def устав(ctx, par):
    channel: discord.TextChannel = get(ctx.channel.guild.channels, id=channels.CHARTER)
    messages = await channel.history().flatten()
    text = '\n'.join(message.content for message in messages)
    await ctx.send(_get_paragraph(par, text))


@bot.command(pass_context=True, help='вывод правил')
async def rule(ctx, par):
    channel: discord.TextChannel = get(ctx.channel.guild.channels, id=channels.RULES)
    messages = await channel.history(limit=1, oldest_first=True).flatten()
    text = '\n'.join(message.content for message in messages)
    if par == '34':
        await ctx.send(_get_paragraph(2, text))
        await ctx.send(file=discord.File('files/media/34.jpg'))
    else:
        await ctx.send(_get_paragraph(par, text))


@bot.command(pass_context=True, help='основные принципы')
async def main(ctx):
    channel: discord.TextChannel = get(ctx.channel.guild.channels, id=channels.INFO)
    messages = await channel.history(limit=1, oldest_first=True).flatten()
    text = '\n'.join(message.content for message in messages)
    await ctx.send(_get_principle(text))


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


@bot.command(pass_context=True, help='Обновить список членов ги')
@commands.has_role("Совет ги")
async def список(ctx):
    message = ''
    uniq_users = set()
    leader = get_member_by_role(ctx, name="Глава ги")
    council = get_member_by_role(ctx, name="Совет ги")
    tot = get_member_by_role(ctx, name="ToT")
    recruit = get_member_by_role(ctx, name="Рекрут")
    channel = bot.get_channel(channels.LIST)

    count = 0
    for group in (leader, council, tot, recruit):
        message += f"-----------{group.role}-----------\n"
        for i in range(len(group.members)):
            if group.members[i] not in uniq_users:
                count += 1
                message += f'{count}. {group.members[i].display_name}\n'
                uniq_users.add(group.members[i])
    await ctx.message.delete()
    await channel.purge(limit=1, oldest_first=True)
    await channel.send(message)


@bot.command(pass_context=True, help='для решения споров')
async def roll(ctx, num=100):
    await ctx.message.delete()
    await ctx.send(f"{ctx.author.display_name} rolled {random.randint(1, num)} from {num}")


@bot.command(help='описание команд')
async def info(ctx):
    msg = 'Основные команды:\n'
    msg += '**!устав [глава устава]** - для вывода главы устава\n'
    msg += '**!rule [номер правила]** - для вывода правила из канала правил\n'
    msg += '**!roll [макс - опционально]** - для вывода целого числа от 1 до 100 (или макс)\n'
    msg += '**!страйк [Ник] [причина - опционально]** - даёт +1 уровень страйка\n'
    msg += '**!амнистия [Ник]** - снимает 1 уровень страйка\n'
    msg += '**!mute [Ник] [время] [причина]** - мут. Время в формате [цифра][smhd]\n'
    msg += '**!unmute [Ник]** - снять мут\n'
    await ctx.send(msg)
