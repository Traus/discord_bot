import random
import re
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from discord.utils import get

from commands.base_command import Command
from constants import Channels, vote_reactions, number_emoji, Members
from init_bot import bot
from utils.format import box, send_by_bot, create_embed, edit_new_strings
from utils.guild_utils import get_members_by_role, mention_member_by_id, get_role_by_name


class MainCommands(Command, name='Основное'):
    """Основные команды, доступные каждому"""

    @commands.command(pass_context=True, name='устав', help='Глава устава. Вывод глав устава')
    async def charter(self, ctx, par):
        channel: discord.TextChannel = get(ctx.channel.guild.channels, id=Channels.CHARTER)
        messages = await channel.history().flatten()
        text = '\n'.join(message.content for message in messages)
        if par == '100500':
            hellman = await mention_member_by_id(Members.HELLMAN)
            text = f"{hellman} \nЗ\nА\nН\nУ\nД\nА\n!!!"
            embed = create_embed(description=text)
            await ctx.send(embed=embed)
        else:
            await ctx.send(box(_get_paragraph(par, text)))

    @commands.command(pass_context=True, help='Номер правила. Вывод правил')
    async def rule(self, ctx, par):
        channel: discord.TextChannel = get(ctx.channel.guild.channels, id=Channels.RULES)
        messages = await channel.history(limit=1, oldest_first=True).flatten()
        text = '\n'.join(message.content for message in messages)
        if par == '34':
            await ctx.send(_get_paragraph(2, text))
            await ctx.send(file=discord.File('files/media/34.jpg'))
        else:
            await ctx.send(box(_get_paragraph(par, text)))

    @commands.command(pass_context=True, help='Основные принципы гильдии')
    async def main(self, ctx):
        channel: discord.TextChannel = get(ctx.channel.guild.channels, id=Channels.INFO)
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
    async def vote(self, ctx, *, text: str = ''):
        await ctx.message.delete()

        reactions = vote_reactions

        separated_text = text.split(':')
        number = separated_text[0].strip()

        if re.match(r'\d+', number):
            if int(number) > 10:
                await ctx.send(box("Слишком много вариантов. Максимум 10."))
                return
            reactions = [number_emoji[i+1] for i in range(int(number))]
            separated_text.pop(0)
        text = edit_new_strings(' '.join(separated_text))
        now = datetime.timestamp(datetime.utcnow())
        embed = create_embed(description=f"{ctx.author.mention}:\n{text}",
                             thumbnail=ctx.author.avatar_url,
                             footer=f"Опрос от {datetime.fromtimestamp(now + 3*60*60).strftime('%d.%m.%Y - %H:%M')}")
        msg: discord.Message = await ctx.send(embed=embed)

        for reaction in reactions:
            await msg.add_reaction(reaction)

    @commands.command(pass_context=True, help="Кто в муте?")
    async def muted(self, ctx):
        group = get_members_by_role(name="Muted")
        message = 'В муте:\n'
        for count, member in enumerate(group.members, 1):
            message += f'{count}. {member.display_name}\n'
        await ctx.send(box(message))

    @commands.command(pass_context=True, name="арена", help="доступ к чату арены")
    async def arena(self, ctx):
        member = ctx.author
        arena_role = get_role_by_name(name="арена")
        if arena_role not in member.roles:
            await member.add_roles(arena_role)
        else:
            await member.remove_roles(arena_role)


def _get_paragraph(par, text):
    pattern = f'(?<![.\d<@#]){par}.*'
    res = re.findall(pattern, text)
    return '\n\t'.join(res)


def _get_principle(text):
    pattern = r'Основные принципы гильдии.*'
    res = re.findall(pattern, text)
    return res[0]


bot.add_cog(MainCommands())
