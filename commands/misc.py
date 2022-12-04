from discord.ext import commands

from database import reconnect, conn
from database.stat import select_all, add_value
from init_bot import bot


@bot.command(pass_context=True, help='Чекнуть таблицу стат')
async def select(ctx, *args):
    await ctx.send(select_all())


@commands.has_role("Глава ги")
@bot.command(pass_context=True, help='Добавить значение в таблицу стат')
async def add(ctx, name: str, number: int):
    await ctx.send(add_value(name, number))


@commands.has_role("Глава ги")
@bot.command(pass_context=True, help='Переконектиться к базе данных')
async def connect(ctx, *args):
    global conn

    conn = reconnect()
    await ctx.send('База перезагружена')

