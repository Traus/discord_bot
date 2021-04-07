from discord.ext import commands

from init_bot import bot
from utils.tenor_gifs import find_gif


@bot.command(pass_context=True, name='мегашапалах', help='Ульта Трауса')
@commands.has_role("Глава ги")
async def mega_slap(ctx):
    await ctx.send(find_gif('batman slap', 1))
