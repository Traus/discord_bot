from discord.ext import commands

from commands._base_command import Command
from database.connector import connection
from database.stat import select_all, add_value


class DBCommands(Command, name='База данных'):
    """Команды для работы с базой данных"""
    @commands.command(pass_context=True, help='Проверить доступность базы')
    async def ping_db(self, ctx, *args):
        await ping_db(ctx, *args)

    @commands.command(pass_context=True, help='Переконектиться к базе данных')
    @commands.has_role("Глава ги")
    async def reconnect(self, ctx, *args):
        connection.reconnect()
        await ctx.send('База данных перезагружена')

    @commands.command(pass_context=True, help='Отключить базу данных')
    @commands.has_role("Глава ги")
    async def close_db(self, ctx, *args):
        connection.close()
        await ctx.send('База данных отключена')

    @commands.command(pass_context=True, help='Чекнуть таблицу стат')
    async def select(self, ctx, *args):
        await ctx.send(select_all())

    @commands.command(pass_context=True, help='Добавить значение в таблицу стат')
    @commands.has_role("Глава ги")
    async def add(self, ctx, name: str, number: int):
        await ctx.send(add_value(name, number))


async def ping_db(ctx, *args):
    closed = connection.closed
    await ctx.send(f"База данных {'не ' if closed else ''}подключена")


def setup(bot):
    bot.add_cog(DBCommands(bot))
