import random
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Union, Optional

import discord
import imageio
import requests
from PIL import Image, ImageOps
from discord.utils import get
from collections import namedtuple

from constants import GUILD_ID, beer_emoji
from database.participants_table import participants
from database.stat import add_value
from init_bot import bot
from utils.format import send_by_bot
from utils.states import immune_until

Members = namedtuple('Members', ['role', 'members'])


def get_role_by_name(name: str) -> discord.Role:
    all_roles = bot.get_guild(GUILD_ID).roles
    return get(all_roles, name=name)


async def mention_member_by_id(member_id: int) -> str:
    guild: discord.Guild = bot.get_guild(GUILD_ID)
    member = await guild.fetch_member(member_id)
    return member.mention


def get_leader() -> discord.Member:
    members = get_members_by_role('Глава ги')
    if len(members.members) != 1:
        return bot.get_guild(GUILD_ID).owner
    return members.members[0]


def get_members_by_role(name: str = None) -> namedtuple:
    name = name.replace(' ', '').lower()
    all_members = bot.get_all_members()
    all_roles = bot.get_guild(GUILD_ID).roles
    class_roles = dict(
        алхимик='💉',
        маг='🔮',
        охотник='🏹',
        страж='🛡️',
        тень='🗡️',
    )
    if name in class_roles:
        name = class_roles[name]
    for role in all_roles:
        if role.name.replace(' ', '').lower() == name:
            return Members(role.name, [member for member in all_members if role in member.roles])


def get_class_roles(guild: discord.Guild) -> dict:
    roles_dict = {'💉': get(guild.roles, name='💉'),
                  '🧙': get(guild.roles, name='🔮'),
                  '🏹': get(guild.roles, name='🏹'),
                  '🛡️': get(guild.roles, name='🛡️'),
                  '🗡️': get(guild.roles, name='🗡️')}
    return roles_dict


def get_guild_members(name: str) -> str:
    group_tot = get_members_by_role(name='ToT')
    group = get_members_by_role(name=name)
    members = set(group.members) & set(group_tot.members)
    message = ''
    for count, member in enumerate(members, 1):
        message += f'{count}. {strip_tot(name=member.display_name)}\n'
    return message


def get_bot_avatar():
    manager = get_members_by_role(name="Смотритель Таверны").members
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


async def set_permissions(channel_id: int, target: Union[discord.Member, discord.Role], **permissions):
    channel = get_channel(channel_id)
    await channel.set_permissions(target, **permissions)


async def create_and_send_slap(ctx, avatar_from, avatar_to, gif=False, from_bot=False):
    clean_list = []
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
    tmp_file_path.write_bytes(b.read())
    clean_list.append(tmp_file_path)

    if gif:
        reversed = ImageOps.mirror(Image.open(tmp_file_path))
        tmp_file_path_2 = Path('files/media/temp_slap_reverse.png')
        reversed.save('files/media/temp_slap_reverse.png', quality=95)
        clean_list.append(tmp_file_path_2)

        images = []
        for filename in sorted(clean_list*2):
            images.append(imageio.imread(filename))
        tmp_gif_path = Path('files/media/temp_gif_slap.gif')
        imageio.mimsave(tmp_gif_path, images)
        clean_list.append(tmp_gif_path)

    file_path = tmp_gif_path if gif else tmp_file_path
    message = await quote_referenced_message(ctx, limit=50)

    try:
        if from_bot:
            await ctx.send(file=discord.File(file_path), reference=ctx.message.reference)
        else:
            await send_by_bot(ctx, message, file=discord.File(file_path))
    finally:
        for file in clean_list:
            file.unlink()


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


def check_for_beer(content: Union[discord.Message, discord.Emoji]):
    for name, smile in beer_emoji.items():
        if smile in str(content):
            count_smiles = len(re.findall(smile, str(content)))
            add_value(name, count_smiles)


def find_animated_emoji(word: str) -> Optional[str]:
    for emoji in bot.get_guild(GUILD_ID).emojis:
        if word.lower() == emoji.name.lower() and emoji.animated:
            return f"<a:{emoji.name}:{emoji.id}>"


def get_emoji_by_id(emoji_id: Union[str, int]) -> Optional[discord.Emoji]:
    for emoji in bot.get_guild(GUILD_ID).emojis:
        if emoji.id == int(emoji_id):
            return emoji


async def get_referenced_message(ctx) -> Optional[discord.Message]:
    if ctx.message.reference is not None:
        message_id = ctx.message.reference.message_id
        return await ctx.fetch_message(message_id)


async def get_referenced_author(ctx) -> Optional[discord.Member]:
    if ctx.message.reference is not None:
        message = await get_referenced_message(ctx)
        return message.author


async def quote_referenced_message(ctx, limit: int = 100) -> str:
    if ctx.message.reference is not None:
        message = await get_referenced_message(ctx)
        content = message.content
        if len(content) > limit:
            content = content[:limit] + '**...**'
        if content.count('\n') > 4:
            content = '\n'.join(content.split('\n', maxsplit=3)[:3]) + '**...**'
        return f'{message.author.mention}\n{">>> " if content else ""}{content.replace(">>> ", "")}\n'
    return ''


def is_traus(member: discord.Member) -> bool:
    all_roles = bot.get_guild(GUILD_ID).roles
    traus = get(all_roles, name='Глава ги')
    if traus in member.roles:
        return True
    return False


def random_emoji(animated=True) -> discord.Emoji:
    emojis = bot.get_guild(GUILD_ID).emojis
    if animated:
        emojis = list(filter(lambda x: x.animated, emojis))
    return random.choice(emojis)


def get_reputation_income(tax: int = 0) -> dict:
    def start_time_with_tax(num) -> int:
        return num - num//100*tax
    return {player.name: player.finish - start_time_with_tax(player.start) for player in participants}


def chance(percentage: int) -> bool:
    return random.randint(0, 100) <= percentage


def get_channel(channel_id: int) -> discord.TextChannel:
    return bot.get_channel(channel_id)


async def has_voice_permissions(user: discord.Member) -> bool:
    return get_role_by_name('Совет ги') in user.roles \
           or get_role_by_name('Глава ги') in user.roles
