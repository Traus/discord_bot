import asyncio
from pathlib import Path
from re import split

import discord
from discord.ext import commands

from constants import roles
from init_bot import bot

BAD_WORDS = Path('files/bad_words.txt').read_text(encoding='utf8').split('\n')


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
    await ctx.send(f'{user.display_name} получил мут на {time} по причине: {reason}')
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
