import asyncio
from pathlib import Path
from random import randint
from re import split

import discord

from constants import roles, channels
from utils.format import box
from utils.guild_utils import set_permissions
from utils.states import muted_queue, user_permissions

BAD_WORDS = Path('files/bad_words.txt').read_text(encoding='utf8').split('\n')


async def _add_mute(member: discord.Member, time: int):
    mute_role = member.guild.get_role(roles.MUTED)  # айди роли которую будет получать юзер

    if muted_queue[member]:
        muted_queue[member].append(time)
        if mute_role not in member.roles:
            await member.add_roles(mute_role)
        return

    channels_with_perms = [channels.SEKTA, channels.KEFIR]
    user_permissions[member]['manage_roles'] = member.guild_permissions.manage_roles
    member.guild_permissions.manage_roles = False
    for channel_id in channels_with_perms:
        user_permissions[member][channel_id] = (
            member.permissions_in(member.guild.get_channel(channel_id)).read_messages,
            member.permissions_in(member.guild.get_channel(channel_id)).send_messages
        )
    await member.add_roles(mute_role)
    for channel_id in channels_with_perms:
        await set_permissions(channel_id, member, send_messages=False)

    muted_queue[member].append(time)
    while True:
        if muted_queue[member]:
            await asyncio.sleep(muted_queue[member][0])
            try:
                muted_queue[member].pop(0)
            except IndexError:
                # unmute before mute ends
                pass
        else:
            break

    await member.remove_roles(mute_role)
    member.guild_permissions.manage_roles = user_permissions[member]['manage_roles']
    for channel_id in channels_with_perms:
        await set_permissions(channel_id, member, read_messages=user_permissions[member][channel_id][0], send_messages=user_permissions[member][channel_id][1])


async def automoderation(message: discord.Message):
    mute = False
    pattern = r'[ !.,?;:_@#&$-]+'
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
        await _add_mute(message.author, time=mute_time)
