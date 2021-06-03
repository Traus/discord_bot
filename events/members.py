import discord

from constants import channels, roles
from init_bot import bot
from utils.states import muted_queue


@bot.event
async def on_member_join(member: discord.Member):
    welcome = bot.get_channel(channels.WELCOME)
    text = f"""
Для доступа к каналам ознакомься с {bot.get_channel(channels.RULES).mention} и поставь под ними ✅.

-Информация о гильдии Tavern of Tales - {bot.get_channel(channels.INFO).mention}
-Заявка для вступления в гильдию (заполняется одним сообщением прямо на канале) - {bot.get_channel(channels.JOIN).mention}
-Выбрать себе классовую роль для доступа к соответствующему каналу - {bot.get_channel(channels.CHOOSE_CLASS).mention}
-Гостевая для общения - {bot.get_channel(channels.GUEST).mention}
-На сервере доступна система приватных комнат - {bot.get_channel(channels.PRIVATE_CHANNELS).mention}
{bot.get_emoji(828026991361261619)}
"""
    embed = discord.Embed(description=f"Добро пожаловать в Таверну Сказаний {member.mention}!")
    embed.set_thumbnail(url=member.avatar_url)

    await welcome.send(embed=embed)
    await welcome.send(text)
    if muted_queue[member]:
        await member.add_roles(member.guild.get_role(roles.MUTED))


@bot.event
async def on_member_remove(member: discord.Member):
    channel = bot.get_channel(channels.GUEST)
    await channel.send(f'{member.display_name} :regional_indicator_f:')
