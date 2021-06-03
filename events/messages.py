from datetime import date

import discord
from discord.utils import get

from commands import automoderation, send_by_bot
from constants import channels
from init_bot import bot
from utils.guild_utils import check_for_beer, find_animated_emoji


@bot.event
async def on_message(message: discord.Message):
    no_moderation = (channels.REQUEST, channels.JOIN, channels.MEMES)

    check_for_beer(message.content)

    animated_emoji_flag = False
    content = message.content
    words = set(content.split(':'))
    for word in words:
        emoji = find_animated_emoji(word)
        if emoji and f':{word}:' in content:  # only 1 word without :
            animated_emoji_flag = True
            content = content.replace(f':{word}:', emoji)
    message._handle_content(content)

    if message.channel.id not in no_moderation:
        await automoderation(message)

    if message.channel.id == channels.MEMES:
        if message.content:
            await message.delete()

    if message.channel.id == channels.JOIN:  # вступление-в-гильдию
        inv_gi_channel: discord.TextChannel = get(message.channel.guild.channels, id=channels.REQUEST)  # заявки-в-ги

        embed = discord.Embed(description=f"{date.today()}\n{message.content}")
        embed.set_thumbnail(url=message.author.avatar_url)

        await inv_gi_channel.send(f"<@{message.author.id}>", embed=embed)
        await message.delete()

    if animated_emoji_flag:
        # todo немного костыльно. Подумать на свежую голову
        if message.author.bot:
            return
        ctx = await bot.get_context(message)
        await send_by_bot(ctx, content, delete=True)
    await bot.process_commands(message)