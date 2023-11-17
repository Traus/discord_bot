import os
from pathlib import Path

import discord

from commands.db_commands import ping_db
from init_bot import bot

# commands and events
import commands
import music
import events
from utils.format import create_embed
from utils.guild_utils import get_role_by_name

try:
    from local_settings import TOKEN
except ImportError:
    TOKEN = os.environ.get("TOKEN")

os.environ['PATH'] += str(Path(__file__).parent.joinpath('ff_source').absolute())


@bot.command(pass_context=True, help='Траус ломает бота')
async def test(ctx, *args):
    msg: discord.Message = ctx.message
    print(msg.channel_mentions)
    print(msg.reference)
    print(msg.guild.emojis)
    m: discord.Message = await ctx.send('123', reference=msg.reference)
    await m.add_reaction(await ctx.guild.fetch_emoji(845429022141186078))
    await ctx.send(embed=create_embed(title='test', description='12321321'))
    # await m.add_reaction(await ctx.guild.fetch_emoji(84542902x`2141186078))


@bot.command(pass_context=True, help='ping')
async def ping(ctx, *args):
    msg: discord.Message = ctx.message
    await msg.channel.send(f"Бот жив цел орёл. Ping={bot.latency}")
    await ping_db(ctx)


if __name__ == '__main__':
    # Load extension
    for filename in os.listdir('./commands'):
        if filename.endswith('.py') and not filename.startswith('_'):
            print(filename)
            bot.load_extension(f'commands.{filename[: -3]}')

    bot.run(TOKEN, reconnect=True)
