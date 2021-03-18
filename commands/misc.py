from init_bot import bot
from utils.format import box
from utils.guild_utils import get_member_by_role


@bot.command(pass_context=True, name='хай', help="Список хай лвл гильдии")
async def high(ctx):
    group = get_member_by_role(ctx, name="Хай лвл")
    message = ''
    count = 1
    for member in group.members:
        name = member.display_name
        if '[tot]' in name.lower() or '[тот]' in name.lower():
            name = name[5:].strip()
        message += f'{count}. {name}\n'
        count += 1
    await ctx.send(box(message))
