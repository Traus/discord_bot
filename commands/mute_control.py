import asyncio
from pathlib import Path
from random import randint
from re import split

import discord

from constants import roles, channels
from utils.format import box
from utils.guild_utils import set_permissions

BAD_WORDS = Path('files/bad_words.txt').read_text(encoding='utf8').split('\n')


async def _add_mute(user: discord.Member, time: str = '30s'):
    times = {'s': 1, 'm': 60, 'h': 60*60, 'd': 60*60*24}
    time_1, time_2 = int(time[:-1]), time[-1]
    role = user.guild.get_role(roles.MUTED)  # айди роли которую будет получать юзер
    permissions = dict()
    channels_with_perms = [channels.MERY, channels.KEFIR]
    for channel_id in channels_with_perms:
        permissions[channel_id] = (user.permissions_in(user.guild.get_channel(channel_id)).read_messages,
                                   user.permissions_in(user.guild.get_channel(channel_id)).send_messages)
    await user.add_roles(role)
    for channel_id in channels_with_perms:
        await set_permissions(channel_id, user.id, send_messages=False)
        await set_permissions(channels.PRIVATE_CHANNELS, user.id, read_messages=False)

    await asyncio.sleep(time_1 * times[time_2])
    await user.remove_roles(role)
    for channel_id in channels_with_perms:
        await set_permissions(channel_id, user.id, read_messages=permissions[channel_id][0], send_messages=permissions[channel_id][1])
        await set_permissions(channels.PRIVATE_CHANNELS, user.id, read_messages=True)


async def automoderation(message: discord.Message):
    mute = False
    pattern = r'[ !.,?;:-_@]+'
    for word in split(pattern, message.content):
        if word.lower() in BAD_WORDS:
            mute = True
            break
    if mute:
        try:
            await message.delete()
        except discord.errors.NotFound:
            pass
        mute_time = randint(1, 60)
        suffix = 'у' if str(mute_time).endswith('1') and mute_time != 11 \
            else 'ы' if str(mute_time)[-1] in ('2', '3', '4') and mute_time not in [12, 13, 14] \
            else ''
        await message.channel.send(box(f'{message.author.display_name} получил мут на {mute_time} секунд{suffix}'))
        await _add_mute(message.author, time=f"{mute_time}s")
