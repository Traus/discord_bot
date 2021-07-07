import random
import re
import time
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from discord.utils import get

from constants import channels, vote_reactions, number_emoji
from init_bot import bot
from utils.format import box, send_by_bot


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
        first = second = timedelta(hours=7)
        third = timedelta(hours=9)
        start_time = datetime.strptime("10/03/2021 00:00", "%d/%m/%Y %H:%M")  # all daily updated
        current_time = datetime.utcnow()
        delta = current_time - start_time
        starts_first = ("Дейлы 7 и 13 уровня начнутся в {} по мск", current_time + (first - delta % first))
        starts_next = ("Дейл 16 уровня начнётся в {} по мск", current_time + (third - delta % third))
        if starts_first[1] > starts_next[1]:
            starts_first, starts_next = starts_next, starts_first
        before_daily = starts_first[1] - current_time

        msg = 'Следующий дейл начнётся через {next_daily}.\n{first}.\n{second}.'.format(
            next_daily=f'{int(before_daily.seconds // 3600)} часов {int(before_daily.seconds / 60 % 60)} минут {before_daily.seconds % 60} секунд',
            first=starts_first[0].format((starts_first[1] + timedelta(hours=3)).strftime("%H:%M:%S")),  # msk time
            second=starts_next[0].format((starts_next[1] + timedelta(hours=3)).strftime("%H:%M:%S"))  # msk time
        )
        await send_by_bot(ctx, box(msg), delete=True)

    @commands.command(name='магаз', help='игровой магазин, !магаз <число> для просмотра магазина на дни вперед')
    async def shop(self, ctx, days: str = ''):
        await ctx.message.delete()
        try:
            day_delta = int(days.strip("+"))
        except ValueError:
            day_delta = 0
        start_time = datetime.strptime("21.04.2021 01", "%d.%m.%Y %H")
        current_time = datetime.utcnow() + timedelta(hours=3)  # msk time
        days = (current_time - start_time).days + 1
        shop_date = current_time + timedelta(days=day_delta)
        await ctx.send(
            f'Магазин на {shop_date.strftime("%d.%m.%Y")}',
            file=discord.File(f'files/media/shop/{(days + day_delta) % 12}.jpg')
        )

    @commands.command(
        pass_context=True,
        help='Начать опрос. Если начать текст с число:, то в голсосовании будет от 1 до число(10) вариантов'
    )
    async def vote(self, ctx, *text):
        await ctx.message.delete()

        reactions = vote_reactions
        if text:
            number = text[0].strip(':') if re.match(r'\d+:', text[0]) else []
            if number:
                if int(number) > 10:
                    await ctx.send(box("Слишком много вариантов. Максимум 10."))
                    return
                text = text[1:]
                reactions = [number_emoji[i+1] for i in range(int(number))]
        text = ' '.join(text).replace('\\n', '\n')
        embed = discord.Embed(description=f"{ctx.author.mention}:\n{text}")
        embed.set_thumbnail(url=ctx.author.avatar_url)
        now = datetime.timestamp(datetime.utcnow())
        embed.set_footer(text=f"Опрос от {datetime.fromtimestamp(now + 3*60*60).strftime('%d.%m.%Y - %H:%M')}")
        msg: discord.Message = await ctx.send(embed=embed)

        for reaction in reactions:
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
