import discord
from discord.utils import get

from constants import channels, roles
from init_bot import bot
from utils.states import muted_queue


@bot.event
async def on_member_join(member: discord.Member):
    # todo fix
    # guest_role = get(member.guild.roles, name='Гость')
    # await member.add_roles(guest_role)
    emoji = await member.guild.fetch_emoji(811516186453082133)
    guest_channel: discord.TextChannel = bot.get_channel(channels.GUEST)
    await guest_channel.send(f'{member.mention} {emoji}')

    text = f"""
-Информация о гильдии Tavern of Tales - {bot.get_channel(channels.INFO).mention}
-Заявка для вступления в гильдию (заполняется одним сообщением прямо на канале) - {bot.get_channel(channels.JOIN).mention}
-Выбрать себе классовую роль для доступа к соответствующему каналу - {bot.get_channel(channels.CHOOSE_CLASS).mention}
-Гостевая для общения - {bot.get_channel(channels.GUEST).mention}
-На сервере доступна система приватных комнат - {bot.get_channel(channels.PRIVATE_CHANNELS).mention}
{bot.get_emoji(828026991361261619)}
"""
    embed = discord.Embed(description=f"Добро пожаловать в Таверну Сказаний {member.mention}!")
    embed.set_thumbnail(url=member.avatar_url)

    welcome = bot.get_channel(channels.WELCOME)
    await welcome.send(embed=embed)
    await welcome.send(text)
    if muted_queue[member]:
        await member.add_roles(member.guild.get_role(roles.MUTED))


@bot.event
async def on_member_remove(member: discord.Member):
    guest_channel = bot.get_channel(channels.GUEST)
    guild_channel = bot.get_channel(channels.GUILD)
    channel = guest_channel
    if get(member.guild.roles, name="ToT") in member.roles:
        channel = guild_channel
    await channel.send(f'{member.display_name} :regional_indicator_f:')
