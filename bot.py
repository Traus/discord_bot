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
    print(ctx.guild.roles)
    print(ctx.channel.id)


@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id != PRIVATE_CHANNELS_MSG_ID:
        return
    emoji = payload.emoji
    if emoji.name == '🇩':
        user = await bot.fetch_user(payload.user_id)
        domino_channel = bot.get_channel(channels.DOMINO)
        perms_flag = False
        for role in payload.member.roles:
            if role.name in ['Совет ги', 'ToT', 'Крот с ЕС', 'Клуб любителей домино']:
                perms_flag = True
        await domino_channel.set_permissions(user, read_messages=True, send_messages=perms_flag)
    else:
        channel = bot.get_channel(channels.PRIVATE_CHANNELS)
        message = await channel.fetch_message(payload.message_id)
        await message.clear_reaction(emoji)


@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id != PRIVATE_CHANNELS_MSG_ID:
        return
    emoji = payload.emoji
    if emoji.name == '🇩':
        user = await bot.fetch_user(payload.user_id)
        domino_channel = bot.get_channel(channels.DOMINO)
        await domino_channel.set_permissions(user, read_messages=False)


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


bot.run(TOKEN)
