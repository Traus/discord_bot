import random
import re
import time
from datetime import datetime

import discord
from discord.ext import commands
from discord.utils import get

from constants import channels, vote_reactions
from init_bot import bot
from utils.format import box


class MainCommands(commands.Cog, name='Основное'):
    """Основные команды, доступные каждому"""

    @commands.command(pass_context=True, name='устав', help='Глава устава. Вывод глав устава')
    async def charter(self, ctx, par):
        channel: discord.TextChannel = get(ctx.channel.guild.channels, id=channels.CHARTER)
        messages = await channel.history().flatten()
        text = '\n'.join(message.content for message in messages)
        await ctx.send(box(_get_paragraph(par, text)))

    @commands.command(pass_context=True, help='Номер правила. Вывод правил')
    async def rule(self, ctx, par):
        channel: discord.TextChannel = get(ctx.channel.guild.channels, id=channels.RULES)
        messages = await channel.history(limit=1, oldest_first=True).flatten()
        text = '\n'.join(message.content for message in messages)
        if par == '34':
            await ctx.send(_get_paragraph(2, text))
            await ctx.send(file=discord.File('files/media/34.jpg'))
        else:
            await ctx.send(box(_get_paragraph(par, text)))

    @commands.command(pass_context=True, help='Основные принципы гильдии')
    async def main(self, ctx):
        channel: discord.TextChannel = get(ctx.channel.guild.channels, id=channels.INFO)
        messages = await channel.history(limit=1, oldest_first=True).flatten()
        text = '\n'.join(message.content for message in messages)
        await ctx.send(box(_get_principle(text)))

    @commands.command(pass_context=True, help='Для решения споров. Случайное число от 1 до 100')
    async def roll(self, ctx, num=100):
        await ctx.message.delete()
        await ctx.send(box(f"{ctx.author.display_name} rolled {random.randint(1, num)} from {num}"))

    @commands.command(pass_context=True, name='дейл', help='Узнать, когда обновятся дейлы')
    async def daily(self, ctx):
        start_time = "10/03/2021 00:00"
        first = second = 7 * 60 * 60
        third = 9 * 60 * 60
        stamp = time.mktime(datetime.strptime(start_time, "%d/%m/%Y %H:%M").timetuple())
        now = datetime.timestamp(datetime.utcnow())
        delta = now - stamp
        starts_first = ("Дейлы 7 и 13 уровня начнутся в {} по мск", now + (first - delta % first))
        starts_next = ("Дейл 16 уровня начнётся в {} по мск", now + (third - delta % third))
        if starts_first[1] > starts_next[1]:
            starts_first, starts_next = starts_next, starts_first
        before_dail = starts_first[1] - now

        msg = 'Следующий дейл начнётся через {next_dail}.\n{first}.\n{second}.'.format(
            next_dail=f'{int(before_dail // 3600)} часов {int(before_dail / 60 % 60)} минут {int(before_dail % 60)} секунд',
            first=starts_first[0].format(datetime.fromtimestamp(starts_first[1] + 3600*3)),
            second=starts_next[0].format(datetime.fromtimestamp(starts_next[1] + 3600*3))
        )
        await ctx.channel.send(box(msg))

    @commands.command(pass_context=True, help='Начать опрос')
    async def vote(self, ctx, *text):
        await ctx.message.delete()
        embed = discord.Embed(description=f"{ctx.author.mention}:\n{' '.join(text)}")
        embed.set_thumbnail(url=ctx.author.avatar_url)
        now = datetime.timestamp(datetime.utcnow())
        embed.set_footer(text=f"Опрос от {datetime.fromtimestamp(now + 3*60*60).strftime('%d.%m.%Y - %H:%M')}")
        msg: discord.Message = await ctx.send(embed=embed)

        for reaction in vote_reactions:
            await msg.add_reaction(reaction)


def _get_paragraph(par, text):
    pattern = f'(?<![.\d<]){par}.*'
    res = re.findall(pattern, text)
    return '\n\t'.join(res)


def _get_principle(text):
    pattern = r'Основные принципы гильдии.*'
    res = re.findall(pattern, text)
    return res[0]


bot.add_cog(MainCommands())
