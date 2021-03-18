from discord.ext import commands

from init_bot import bot


@bot.command(pass_context=True, help='Траус чистит каналы')
@commands.has_role("Глава ги")
async def clean(ctx, limit=10):
    await ctx.channel.purge(limit=limit)
