from datetime import datetime
from io import BytesIO
from pathlib import Path

import discord
import requests
from PIL import Image
from discord.utils import get
from collections import namedtuple

from constants import GUILD_ID
from init_bot import bot
from utils.statuses import immune_until

Members = namedtuple('Members', ['role', 'members'])


def get_member_by_role(ctx=None, user: discord.Member = None, name: str = None) -> namedtuple:
    obj = ctx or user
    all_roles = getattr(obj, 'guild').roles
    role = get(all_roles, name=name)
    all_members = bot.get_all_members()
    return Members(name, [member for member in all_members if role in member.roles])


def get_class_roles(guild: discord.Guild) -> dict:
    roles_dict = {'💉': get(guild.roles, name='💉'),
                  '🧙': get(guild.roles, name='🔮'),
                  '🏹': get(guild.roles, name='🏹'),
                  '🛡️': get(guild.roles, name='🛡️'),
                  '🗡️': get(guild.roles, name='🗡️')}
    return roles_dict


def get_guild_members(ctx, name: str) -> str:
    group_tot = get_member_by_role(ctx, name='ToT')
    group = get_member_by_role(ctx, name=name)
    members = set(group.members) & set(group_tot.members)
    message = ''
    for count, member in enumerate(members, 1):
        message += f'{count}. {strip_tot(name=member.display_name)}\n'
    return message


def get_bot_avatar(ctx=None):
    manager = get_member_by_role(ctx, name="Смотритель Таверны").members
    return manager[0].avatar_url


def strip_tot(name: str) -> str:
    if '[tot]' in name.lower() or '[тот]' in name.lower():
        return name[5:].strip()
    return name.strip()


async def get_afk_users(msg: discord.Message) -> set:
    all_roles = bot.get_guild(GUILD_ID).roles
    all_members = bot.get_all_members()
    tot = get(all_roles, name='ToT')
    recruit = get(all_roles, name='Рекрут')
    all_guild_users = {member for member in all_members if tot in member.roles or recruit in member.roles}

    for reaction in msg.reactions:
        async for user in reaction.users():
            all_guild_users.discard(user)
    return all_guild_users


async def set_permissions(channel_name: str, user_id: int, **permissions):
    channel = bot.get_channel(channel_name)
    user = await bot.fetch_user(user_id)
    await channel.set_permissions(user, **permissions)


async def create_and_send_slap(ctx, avatar_from, avatar_to):
    base = Image.open(Path('files/media/batslap.png')).resize((1000, 500)).convert('RGBA')

    image_bytes = BytesIO(requests.get(avatar_to).content)
    avatar = Image.open(image_bytes).resize((220, 220)).convert('RGBA')
    image_bytes = BytesIO(requests.get(avatar_from).content)
    avatar2 = Image.open(image_bytes).resize((200, 200)).convert('RGBA')

    base.paste(avatar, (610, 210), avatar)
    base.paste(avatar2, (380, 70), avatar2)
    base = base.convert('RGB')

    b = BytesIO()
    base.save(b, format='png')
    b.seek(0)

    tmp_file_path = Path('files/media/temp_slap.png')
    try:
        tmp_file_path.write_bytes(b.read())
        await ctx.send(file=discord.File(tmp_file_path))
    finally:
        tmp_file_path.unlink()


def has_immune(member: discord.Member) -> bool:
    if immune_until[member] >= datetime.timestamp(datetime.now()):
        return True
    return False


def is_spam(author, memory, sec):
    stamp = datetime.timestamp(datetime.now())
    if 1 < stamp - memory[author] < sec:
        return True
    memory[author] = stamp
    return False
