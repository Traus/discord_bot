from init_bot import bot
from constants import members
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
async def соус(ctx):  # en
    search_term = 'sause'
    limit = 10
    await ctx.send(find_gif(search_term, limit))


@bot.command(help='ToT')
async def tavern(ctx):
    msg = await ctx.send(_tavern_emoji)
    for emoji in ('🇴', '🇫', '🇹', '🇦', '🇱', '🇪', '🇸'):
        await msg.add_reaction(emoji)
