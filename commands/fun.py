from init_bot import bot
from constants import members

tavern_emoji = f':regional_indicator_t: ' \
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


@bot.command(help='ToT')
async def tavern(ctx):
    await ctx.send(tavern_emoji)
