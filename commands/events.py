import random
from collections import Counter
from time import sleep

import discord
from discord.ext import commands

from commands.base_command import Command
from init_bot import bot
from utils.format import box
from utils.guild_utils import get_reputation_income


class EventsCommands(Command, name='Ивенты'):
    """Команды под различные мероприятия"""
    @commands.command(pass_context=True, name='победитель', help='Определить победителя конкурса')
    @commands.has_role("Глава ги")
    async def winner(self,
                     ctx,
                     role: discord.Role,
                     necessary_points: str = '500',
                     tax: str = '0',
                     prizes: str = 5):
        pass_members = []

        all_income = get_reputation_income(int(tax))
        participants = []
        winners = []
        for member, income in all_income.items():
            participants.extend([member]*(income//int(necessary_points)))

        prizes = int(prizes)
        assert prizes <= len(set(participants))
        while prizes:
            winner = random.choice([p for p in participants if p not in pass_members])
            if winner not in winners:
                winners.append(winner)
                prizes -= 1

        await ctx.send(box(f"Начало рассчета..."))
        await ctx.send(box(f"Наши участники: {Counter(participants).most_common()}"))
        for i in reversed(range(10)):
            await ctx.send(i)
            sleep(1)
        await ctx.send(box(f"Траус считает на калькуляторе...."))
        sleep(1)
        await ctx.send(f"{role.mention} Друзья!")
        await ctx.send(box(f"{', '.join(winners)} поздравляем с победой в конкурсе!!!! Приз-скайпасс или его эквивалент. "
                           f"При желании, приз можно передать любому другому участнику гильдии! "
                           f"В скором времени совет свяжется с победителями и обсудит возможность передачи награды =)"))

    # @commands.command(name='поздравляю', help='Поздравить Ирочку')
    # async def birthday(self, ctx):
    #     await ctx.send(f'Поздравляем нашу <@{693210152127692920}> с Днём Рождения!')
    #     await ctx.send(find_gif('Поздравляю', 10))


bot.add_cog(EventsCommands())
