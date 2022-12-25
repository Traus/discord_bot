from discord.ext import commands

from database.connector import connection
from database.stat import select_all, add_value
from init_bot import bot


@bot.command(pass_context=True, help='Проверить доступность базы')
async def ping_db(ctx, *args):
    closed = connection.closed
    await ctx.send(f"База {'не ' if closed else ''}подключена")


@commands.has_role("Глава ги")
@bot.command(pass_context=True, help='Переконектиться к базе данных')
async def reconnect(ctx, *args):
    connection.reconnect()
    await ctx.send('База перезагружена')


@commands.has_role("Глава ги")
@bot.command(pass_context=True, help='Отключить базу данных')
async def close_db(ctx, *args):
    connection.close()
    await ctx.send('База отключена')


@bot.command(pass_context=True, help='Чекнуть таблицу стат')
async def select(ctx, *args):
    await ctx.send(select_all())


@commands.has_role("Глава ги")
@bot.command(pass_context=True, help='Добавить значение в таблицу стат')
async def add(ctx, name: str, number: int):
    await ctx.send(add_value(name, number))
