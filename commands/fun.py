import random
from io import BytesIO
from pathlib import Path

import discord
import requests
from PIL import Image
from discord.ext import commands

from constants import members
from init_bot import bot
from utils.format import box
from utils.guild_utils import get_member_by_role
from utils.tenor_gifs import find_gif


class FunCommands(commands.Cog, name='Для веселья'):
    """Рофлы и пасхалки"""

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

    @commands.command(name='осуждаю', help='Осудить!')
    async def blame(self, ctx):
        await ctx.message.delete()
        await ctx.send(file=discord.File('files/media/tom.jpg'))

    @commands.command(name='шапалах', help='Втащить')
    async def slap(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        avatar0 = ctx.author.avatar_url
        avatar1 = member.avatar_url

        base = Image.open(Path('files/media/batslap.png')).resize((1000, 500)).convert('RGBA')

        image_bytes = BytesIO(requests.get(avatar1).content)
        avatar = Image.open(image_bytes).resize((220, 220)).convert('RGBA')
        image_bytes = BytesIO(requests.get(avatar0).content)
        avatar2 = Image.open(image_bytes).resize((200, 200)).convert('RGBA')

        base.paste(avatar, (610, 210), avatar)
        base.paste(avatar2, (380, 70), avatar2)
        base = base.convert('RGB')

        b = BytesIO()
        base.save(b, format='png')
        b.seek(0)

        tmp_file_path = Path('files/media/temp_slap.png')
        try:
            tmp_file_path.write_bytes(b.read())
            await ctx.send(file=discord.File(tmp_file_path))
        finally:
            tmp_file_path.unlink()

    @commands.command(name='аватар', help='помотреть аватарку')
    async def avatar(self, ctx, member: discord.Member):
        await ctx.send(member.avatar_url)

    @commands.command(name='секта', help='список участников секты домино')
    async def sekta(self, ctx):
        holy = get_member_by_role(ctx, name='Первосвященник секты')
        zam = get_member_by_role(ctx, name='Просвящённый культист')
        sekta = get_member_by_role(ctx, name='Верный адепт')
        msg = f"Ересиарх:\n{ctx.guild.get_member(members.DOMINO).display_name}\n\n"
        msg += f"{holy.role}:\n{holy.members[0].display_name}\n"
        msg += f"{zam.role}:\n{zam.members[0].display_name}\n\nКультисты:\n"
        for member in sekta.members:
            msg += member.display_name + '\n'
        await ctx.send(box(msg))

    @commands.command(help='=)')
    async def traus(self, ctx):
        msg = await ctx.send(_tavern_emoji)
        for emoji in ('🇴', '🇫', '🇹', '🇷', '🇦', '🇺', '🇸'):
            await msg.add_reaction(emoji)

    @commands.command(help='ToT')
    async def tavern(self, ctx):
        msg = await ctx.send(_tavern_emoji)
        for emoji in ('🇴', '🇫', '🇹', '🇦', '🇱', '🇪', '🇸'):
            await msg.add_reaction(emoji)


_tavern_emoji = f':regional_indicator_t: ' \
               f':regional_indicator_a: ' \
               f':regional_indicator_v: ' \
               f':regional_indicator_e: ' \
               f':regional_indicator_r: ' \
               f':regional_indicator_n:'

bot.add_cog(FunCommands())
