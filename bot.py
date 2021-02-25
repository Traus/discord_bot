import os
import random

# commands
from commands import *

try:
    from loccal_settings import TOKEN
except ImportError:
    TOKEN = os.environ.get("TOKEN")


@bot.command(pass_context=True)
async def test(ctx, *args):
    print(args)


@bot.command(pass_context=True, help='для решения споров')
async def roll(ctx, num=100):
    await ctx.message.delete()
    await ctx.send(f"{ctx.author.display_name} rolled {random.randint(1, num)} from {num}")


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
        message.content = f"{'-' * 30}\n<@{message.author.id}>\n{message.content}\n{'-' * 30}"
        await inv_gi_channel.send(f'{message.content}')
        await message.delete()
    await bot.process_commands(message)


bot.run(TOKEN)
