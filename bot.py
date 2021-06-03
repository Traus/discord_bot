import os
import discord

from init_bot import bot

# commands and events
import commands
import events

try:
    from local_settings import TOKEN
except ImportError:
    TOKEN = os.environ.get("TOKEN")


@bot.command(pass_context=True, help='Траус ломает бота')
async def test(ctx, *args):
    msg: discord.Message = ctx.message
    print(msg.channel_mentions)
    print(msg.reference)
    print(msg.guild.emojis)
    m: discord.Message = await ctx.send('123', reference=msg.reference)
    await m.add_reaction(await ctx.guild.fetch_emoji(845429022141186078))
    # await m.add_reaction(await ctx.guild.fetch_emoji(84542902x`2141186078))

bot.run(TOKEN)
