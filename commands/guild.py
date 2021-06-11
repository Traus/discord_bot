import discord
from discord.ext import commands
from discord.utils import get

from commands.mute_control import _add_mute
from constants import roles
from init_bot import bot
from utils.format import box, send_by_bot
from utils.guild_utils import is_spam, get_member_by_role, strip_tot, get_guild_members, is_traus
from utils.states import when_all_called


class GuildCommands(commands.Cog, name='Гильдия'):
    """Команды, доступные участникам гильдии с ролью ToT"""

    @commands.command(pass_context=True, name='all',  help='Вызвать всю гильдию ТоТ. '
                                                           'Доступ к команде - Совет, Актив, Наставник. '
                                                           'Злоупотребление наказуемо!')
    @commands.has_any_role("Совет ги", "Актив гильдии", "Наставник")
    async def _all(self, ctx, *message):
        if is_spam(ctx.author, when_all_called, 60) and not is_traus(ctx, ctx.author):
            await ctx.send(box(f'{ctx.author.display_name} получил мут на 5 минут по причине: не злоупотреблять!'))
            await _add_mute(ctx.author, 5*60)
        else:
            all_roles = ctx.guild.roles
            councils = get(all_roles, id=roles.COUNCILS)
            tot = get(all_roles, id=roles.TOT)
            recruit = get(all_roles, id=roles.RECRUIT)
            msg = f'{councils.mention} {tot.mention} {recruit.mention}\n'

            if message:
                msg += ' '.join(message)
            else:
                msg += box("Общий сбор!")

            await send_by_bot(ctx, msg, delete=True)

    @commands.command(pass_context=True, name='хайлвл', help="Список хай лвл гильдии")
    @commands.has_any_role("Совет ги", "ToT")
    async def high_lvl(self, ctx):
        tot = get_member_by_role(ctx, name="ToT")
        high = get_member_by_role(ctx, name="Хай лвл")
        group = set(high.members) & set(tot.members)
        message = ''
        for count, member in enumerate(group, 1):
            message += f'{count}. {strip_tot(name=member.display_name)}\n'
        await ctx.send(box(message))

    @commands.command(pass_context=True, name='алхимик', help="Список алхимиков ToT")
    @commands.has_any_role("Совет ги", "ToT")
    async def alchemist(self, ctx):
        message = get_guild_members(ctx, name='💉')
        await ctx.send(box(message))

    @commands.command(pass_context=True, name='маг', help="Список чародеев ToT")
    @commands.has_any_role("Совет ги", "ToT")
    async def mage(self, ctx):
        message = get_guild_members(ctx, name='🔮')
        await ctx.send(box(message))

    @commands.command(pass_context=True, name='охотник', help="Список охотников ToT")
    @commands.has_any_role("Совет ги", "ToT")
    async def hunter(self, ctx):
        message = get_guild_members(ctx, name='🏹')
        await ctx.send(box(message))

    @commands.command(pass_context=True, name='страж', help="Список стражей ToT")
    @commands.has_any_role("Совет ги", "ToT")
    async def guard(self, ctx):
        message = get_guild_members(ctx, name='🛡️')
        await ctx.send(box(message))

    @commands.command(pass_context=True, name='тень', help="Список теней ToT")
    @commands.has_any_role("Совет ги", "ToT")
    async def rouge(self, ctx):
        message = get_guild_members(ctx, name='🗡️')
        await ctx.send(box(message))


bot.add_cog(GuildCommands())
