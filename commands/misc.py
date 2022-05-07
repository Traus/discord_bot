from discord.ext import commands

from database import reconnect
from database.stat import select_all
from init_bot import bot


@bot.command(pass_context=True, help='Чекнуть таблицу стат')
async def test_select(ctx, *args):
    await ctx.send(select_all())


@commands.has_role("Глава ги")
@bot.command(pass_context=True, help='Переконектиться к базе данных')
async def connect(ctx, *args):
    reconnect()
    await ctx.send('База перезагружена')

