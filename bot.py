import os
import discord
from datetime import date
from constants import *

# commands
from commands import *

try:
    from loccal_settings import TOKEN
except ImportError:
    TOKEN = os.environ.get("TOKEN")


@bot.command(pass_context=True)
async def test(ctx, *args):
    print(args)
    print(ctx.message.id)
    print(ctx.message.author.id)
    print(ctx.guild.roles)
    print(ctx.channel.id)
    emoji = await ctx.guild.fetch_emoji(811516186453082133)
    await ctx.channel.send(f'{ctx.message.author.mention} {emoji}')


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.message_id == messages.ROOMS:
        emoji = payload.emoji
        if emoji.name == '🇩':
            user = await bot.fetch_user(payload.user_id)
            domino_channel = bot.get_channel(channels.DOMINO)
            perms_flag = False
            for role in payload.member.roles:
                if role.name in ['Совет ги', 'ToT', 'Крот с ЕС', 'Первосвященник секты', 'Просвящённый культист', 'Верный адепт']:
                    perms_flag = True
            await domino_channel.set_permissions(user, read_messages=True, send_messages=perms_flag)
        else:
            channel = bot.get_channel(channels.PRIVATE_CHANNELS)
            message = await channel.fetch_message(payload.message_id)
            await message.clear_reaction(emoji)

    if payload.message_id == messages.RULES:
        emoji = payload.emoji
        if emoji.name == '✅':
            guild = bot.get_guild(payload.guild_id)
            member: discord.Member = await guild.fetch_member(payload.user_id)
            guest = get(guild.roles, name='Гость')
            await member.add_roles(guest)
            channel = bot.get_channel(channels.GUEST)
            emoji = await member.guild.fetch_emoji(811516186453082133)
            await channel.send(f'{member.mention} {emoji}')


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    if payload.message_id == messages.ROOMS:
        emoji = payload.emoji
        if emoji.name == '🇩':
            user = await bot.fetch_user(payload.user_id)
            domino_channel = bot.get_channel(channels.DOMINO)
            await domino_channel.set_permissions(user, read_messages=False)

    if payload.message_id == messages.RULES:
        emoji = payload.emoji
        if emoji.name == '✅':
            guild = bot.get_guild(payload.guild_id)
            member = await guild.fetch_member(payload.user_id)
            guest = get(guild.roles, name='Гость')
            await member.remove_roles(guest)


@bot.event
async def on_message(message: discord.Message):
    no_moderation = (channels.REQUEST, channels.JOIN, channels.MEMES)
    if message.channel.id not in no_moderation:
        await automoderation(message)

    if message.channel.id == channels.MEMES:
        if message.content:
            await message.delete()

    if message.channel.id == channels.JOIN:  # вступление-в-гильдию
        inv_gi_channel: discord.TextChannel = get(message.channel.guild.channels, id=channels.REQUEST)  # заявки-в-ги
        message.content = f"{'-' * 30}\n<@{message.author.id}> - {date.today()}\n{message.content}\n{'-' * 30}"
        await inv_gi_channel.send(f'{message.content}')
        await message.delete()
    await bot.process_commands(message)


@bot.event
async def on_member_remove(member: discord.Member):
    channel = bot.get_channel(channels.GUEST)
    await channel.send(f'{member.display_name} :regional_indicator_f:')


bot.run(TOKEN)
