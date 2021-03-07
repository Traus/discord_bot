import discord

from init_bot import bot
from constants import members
from utils.guild_utils import get_member_by_role
from utils.tenor_gifs import find_gif


_tavern_emoji = f':regional_indicator_t: ' \
               f':regional_indicator_a: ' \
               f':regional_indicator_v: ' \
               f':regional_indicator_e: ' \
               f':regional_indicator_r: ' \
               f':regional_indicator_n:'


@bot.command(help='rofl')
async def rofl(ctx):
    await ctx.send(f'{ctx.author.display_name} <@{members.ROFL}>`ит')


@bot.command(help='fanatik')
async def fanatik(ctx):
    await ctx.send(f':regional_indicator_f: '
                   f':regional_indicator_a: '
                   f':regional_indicator_n: '
                   f':regional_indicator_a: '
                   f':regional_indicator_t: '
                   f':regional_indicator_i: '
                   f':regional_indicator_k:')


@bot.command(help='coycb')
async def соус(ctx):  # ru
    search_term = 'sause'
    limit = 10
    await ctx.send(find_gif(search_term, limit))


@bot.command(help='котик')
async def котик(ctx):
    search_term = 'meow'
    limit = 10
    await ctx.send(find_gif(search_term, limit))


@bot.command(help='метеор')
async def метеор(ctx):
    search_term = 'nyan cat'
    limit = 6
    await ctx.send(find_gif(search_term, limit))


@bot.command(help='DeDuJI9I')
async def дедуля(ctx):
    search_term = 'old'
    limit = 15
    await ctx.send(find_gif(search_term, limit))


@bot.command(help='walidor')
async def walidor(ctx):
    await ctx.send(file=discord.File('files/media/walidor.png'))


@bot.command(help='dommag')
async def dommag(ctx):
    await ctx.send(file=discord.File('files/media/dommag.jpg'))


@bot.command(help='domino')
async def мыша(ctx):
    domino = ctx.guild.get_member(members.DOMINO)
    await ctx.send(domino.avatar_url)


@bot.command(help='для соуса')
async def кибермедведь(ctx):
    await ctx.send(file=discord.File('files/media/cyber.jpg'))


@bot.command(help='осуждение')
async def осуждаю(ctx):
    await ctx.message.delete()
    await ctx.send(file=discord.File('files/media/tom.jpg'))


@bot.command(help='клуб любителей домино')
async def секта(ctx):
    holy = get_member_by_role(ctx, name='Первосвященник секты')
    sekta = get_member_by_role(ctx, name='Верный адепт')
    msg = f"Ересиарх:\n{ctx.guild.get_member(members.DOMINO).display_name}\n\n"
    msg += f"{holy.role}:\n{holy.members[0].display_name}\n\nКультисты:\n"
    for member in sekta.members:
        msg += member.display_name + '\n'
    await ctx.send(msg)


@bot.command(help='ToT')
async def tavern(ctx):
    msg = await ctx.send(_tavern_emoji)
    for emoji in ('🇴', '🇫', '🇹', '🇦', '🇱', '🇪', '🇸'):
        await msg.add_reaction(emoji)
