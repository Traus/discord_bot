import random
from datetime import datetime

import discord
from discord.ext import commands
from discord.utils import get

from commands.mute_control import _add_mute
from constants import members, channels
from init_bot import bot
from utils.format import box
from utils.guild_utils import get_member_by_role, get_bot_avatar, is_spam, create_and_send_slap, has_immune, \
    set_permissions
from utils.statuses import when_slap_called, immune_until
from utils.tenor_gifs import find_gif


class FunCommands(commands.Cog, name='Для веселья'):
    """Рофлы и пасхалки"""

    @commands.command(name='осуждаю', help='Осудить!')
    async def blame(self, ctx):
        await ctx.message.delete()
        await ctx.send(file=discord.File('files/media/tom.jpg'))

    @commands.command(name='шапалах', help='Втащить')
    async def slap(self, ctx, member: discord.Member = None, bot=None):
        if member is None:
            member = ctx.author

        avatar_from = ctx.author.avatar_url
        avatar_to = member.avatar_url

        if has_immune(member):
            await ctx.send(box(f'Иммунитет!'))
            return

        if is_spam(ctx.author, when_slap_called, 30):
            await ctx.send(box(f'{ctx.author.display_name} получил мут на 1 минуту по причине: хорош спамить!'))
            await create_and_send_slap(ctx, get_bot_avatar(ctx), avatar_from)
            await _add_mute(ctx.author, '1m')
            return

        if bot is not None and bot == 'bot':
            avatar_from = get_bot_avatar(ctx)
            await ctx.message.delete()

        await create_and_send_slap(ctx, avatar_from, avatar_to)

    @commands.command(name='домик', help='временный иммунитет от шапалаха')
    @commands.has_any_role("Совет ги", "ToT")
    async def home(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        minutes = random.randint(1, 10)
        if has_immune(member):
            await ctx.send(box(f'{ctx.author.display_name} не злоупотребляй! {minutes} минут мута'))
            await _add_mute(ctx.author, f'{minutes}m')
            return
        stamp = datetime.timestamp(datetime.now()) + minutes*60
        immune_until[member] = stamp
        await ctx.send(box(f'{member.display_name} получает иммунитет на {minutes} минут.'))

    @commands.command(name='аватар', help='посмотреть аватарку')
    async def avatar(self, ctx, member: discord.Member):
        await ctx.send(member.avatar_url)

    @commands.command(name='секта', help='список участников секты кровавой Мери')
    async def sekta(self, ctx):
        main = get_member_by_role(ctx, name='Верховная жрица')
        zam = get_member_by_role(ctx, name='Верховный жрец')
        rip = get_member_by_role(ctx, name='Палач')
        sekta = get_member_by_role(ctx, name='Прихожанин')
        msg = f"{main.role}:\n{main.members[0].display_name}\n"
        msg += f"{zam.role}:\n{zam.members[0].display_name}\n"
        msg += f"{rip.role}:\n{rip.members[0].display_name}\n\nПрихожане:\n"
        for member in sekta.members:
            msg += member.display_name + '\n'
        await ctx.send(box(msg))

    @commands.command(name='всекту', help='принять в культ')
    @commands.has_any_role("Совет ги", "Крот с ЕС", "Верховная жрица", "Верховный жрец")
    async def join_sekta(self, ctx, member: discord.Member):
        all_roles = ctx.guild.roles
        sekta = get(all_roles, name='Прихожанин')
        await ctx.send(box(f'Добро пожаловать в секту, {member.display_name}!'))
        await set_permissions(channels.MERY, member._user.id, read_messages=True, send_messages=True)
        await member.add_roles(sekta)

    @commands.command(name='изсекты', help='выйти из этой криповой секты')
    async def exit_sekta(self, ctx):
        all_roles = ctx.guild.roles
        sekta = get(all_roles, name='Прихожанин')
        await ctx.author.remove_roles(sekta)
        await ctx.send(file=discord.File('files/media/sekta.jpg'))
        await set_permissions(channels.MERY, ctx.author._user.id, send_messages=False)

    @commands.command(help='ToT')
    async def tavern(self, ctx):
        msg = await ctx.send(_tavern_emoji)
        for emoji in ('🇴', '🇫', '🇹', '🇦', '🇱', '🇪', '🇸'):
            await msg.add_reaction(emoji)


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
        msg = await ctx.send(_tavern_emoji)
        for emoji in ('🇴', '🇫', '🇹', '🇷', '🇦', '🇺', '🇸'):
            await msg.add_reaction(emoji)


_tavern_emoji = f':regional_indicator_t: ' \
               f':regional_indicator_a: ' \
               f':regional_indicator_v: ' \
               f':regional_indicator_e: ' \
               f':regional_indicator_r: ' \
               f':regional_indicator_n:'

bot.add_cog(FunCommands())
bot.add_cog(NamedCommands())
