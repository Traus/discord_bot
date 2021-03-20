from datetime import datetime

import discord
from discord.utils import get
from collections import namedtuple, defaultdict

from init_bot import bot

Members = namedtuple('Members', ['role', 'members'])

when_all_called = defaultdict(lambda: datetime.timestamp(datetime.now()))
when_slap_called = defaultdict(lambda: datetime.timestamp(datetime.now()))


def get_member_by_role(ctx=None, user: discord.Member = None, name: str = None) -> namedtuple:
    obj = ctx or user
    all_roles = getattr(obj, 'guild').roles
    role = get(all_roles, name=name)
    all_members = bot.get_all_members()
    return Members(name, [member for member in all_members if role in member.roles])


def get_bot_avatar(ctx=None):
    manager = get_member_by_role(ctx, name="Смотритель Таверны").members
    return manager[0].avatar_url


async def set_permissions(channel_name: str, user_id: int, **permissions):
    channel = bot.get_channel(channel_name)
    user = await bot.fetch_user(user_id)
    await channel.set_permissions(user, **permissions)


def is_spam(author, memory, sec):
    stamp = datetime.timestamp(datetime.now())
    if 1 < stamp - memory[author] < sec:
        return True
    return False
