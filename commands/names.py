import random

import discord
from discord.ext import commands

from constants import members, tavern_emoji
from init_bot import bot
from utils.tenor_gifs import find_gif


class NamedCommands(commands.Cog, name='Именные команды'):
    """Команды для увеселения отдельных игроков =)"""

    @commands.command(help='рофлить')
    async def rofl(self, ctx):
        await ctx.send(f'{ctx.author.display_name} <@{members.ROFL}>`ит')

    @commands.command(help='для fanatik')
    async def fanatik(self, ctx):
        await ctx.send(f':regional_indicator_f: '
                       f':regional_indicator_a: '
                       f':regional_indicator_n: '
                       f':regional_indicator_a: '
                       f':regional_indicator_t: '
                       f':regional_indicator_i: '
                       f':regional_indicator_k:')

    @commands.command(name='соус', help='для соуса')  # ru
    async def coyc(self, ctx):
        search_term = 'sause'
        limit = 10
        await ctx.send(find_gif(search_term, limit))

    @commands.command(name='котик', help='для котика')
    async def cat(self, ctx):
        search_term = 'meow'
        limit = 10
        await ctx.send(find_gif(search_term, limit))

    @commands.command(name='метеор', help='для метеора')
    async def meteor(self, ctx):
        search_term = 'nyan cat'
        limit = 6
        await ctx.send(find_gif(search_term, limit))

    @commands.command(name='дедуля', help='для DeDuJI9I')
    async def ded(self, ctx):
        search_term = 'old'
        limit = 15
        await ctx.send(find_gif(search_term, limit))

    @commands.command(help='для варлока')
    async def warlock(self, ctx):
        search_term = 'warlock wow'
        limit = 5
        await ctx.send(find_gif(search_term, limit))

    @commands.command(help='для Mortuus')
    async def mortuus(self, ctx):
        search_term = 'skelet dancing'
        limit = 10
        await ctx.send(find_gif(search_term, limit))

    @commands.command(name='арт', help='танцули Арта')
    async def art(self, ctx):
        search_term = random.choice(['naruto dance', 'anime dance'])
        limit = 10
        await ctx.send(find_gif(search_term, limit))

    @commands.command(help='для walidor')
    async def walidor(self, ctx):
        await ctx.message.delete()
        await ctx.send(file=discord.File('files/media/walidor.png'))

    @commands.command(help='для dommag')
    async def dommag(self, ctx):
        await ctx.send(file=discord.File('files/media/dommag.jpg'))

    @commands.command(name='мыша', help='для domino')
    async def domino(self, ctx):
        domino = ctx.guild.get_member(members.DOMINO)
        await ctx.send(domino.avatar_url)

    @commands.command(name='кибермедведь', help='для соуса')
    async def bear(self, ctx):
        await ctx.send(file=discord.File('files/media/cyber.jpg'))

    @commands.command(help='=)')
    async def traus(self, ctx):
        msg = await ctx.send(tavern_emoji)
        for emoji in ('🇴', '🇫', '🇹', '🇷', '🇦', '🇺', '🇸'):
            await msg.add_reaction(emoji)


bot.add_cog(NamedCommands())
