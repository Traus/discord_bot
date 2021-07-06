import random
import re
from datetime import datetime, timedelta

import discord
import requests
from discord.ext import commands
from discord.utils import get

from constants import channels, tavern_emoji
from database.stat import add_value, get_value
from init_bot import bot
from utils.format import box, send_by_bot
from utils.guild_utils import get_members_by_role, get_bot_avatar, create_and_send_slap, has_immune, \
    set_permissions, get_renferenced_author, is_traus, quote_renferenced_message
from utils.states import table_turn_over
from utils.tenor_gifs import find_gif


class FunCommands(commands.Cog, name='Веселье'):
    """Рофлы и пасхалки"""

    @commands.command(name='осуждаю', help='Осудить!')
    async def blame(self, ctx):
        message = await quote_renferenced_message(ctx)
        await send_by_bot(ctx, message, file=discord.File('files/media/tom.jpg'), delete=True)

    @commands.command(name='одобряю', help='Одобрить!')
    async def approve(self, ctx):
        message = await quote_renferenced_message(ctx)
        search_term = 'approve'
        limit = 10
        await send_by_bot(ctx, message, find_gif(search_term, limit), delete=True)

    @commands.command(name='шапалах', help='Втащить')
    async def slap(self, ctx, members: commands.Greedy[discord.Member], bot: str = None):
        await ctx.message.delete()

        from_bot = bot is not None and bot == 'bot'
        if not members:
            author = await get_renferenced_author(ctx)
            if author is not None:
                members = [author]
            else:
                members = [ctx.author]

        add_value('slap', number=len(members))

        for member in set(members):
            avatar_from = ctx.author.avatar_url
            avatar_to = member.avatar_url

            if has_immune(member) and not from_bot:
                await ctx.send(box(f'У {member.display_name} иммунитет!'))
                continue

            if from_bot:
                avatar_from = get_bot_avatar(ctx)

            gif = is_traus(ctx, ctx.author) or random.randint(0, 100) >= 95
            await create_and_send_slap(ctx, avatar_from, avatar_to, gif=gif, from_bot=from_bot)

    @commands.command(name='аватар', help='посмотреть аватарку')
    async def avatar(self, ctx, member: discord.Member = None):
        await ctx.message.delete()

        if member is None:
            member = ctx.author
        await ctx.send(member.avatar_url)

    @commands.command(name='секта', help='список участников секты кровавой Мери')
    async def sekta(self, ctx):
        main = get_members_by_role(ctx, name='Верховная жрица')
        zam = get_members_by_role(ctx, name='Верховный жрец')
        rip = get_members_by_role(ctx, name='Палач')
        sekta = get_members_by_role(ctx, name='Прихожанин')

        msg = ''
        for role in [main, zam, rip, sekta]:
            members = role.members
            if members:
                m = '\n'.join([role.members[i].display_name for i in range(len(role.members))])
                msg += f"{role.role}:\n{m}\n"
        await ctx.send(box(msg))

    @commands.command(name='всекту', help='принять в культ')
    async def join_sekta(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        all_roles = ctx.guild.roles
        sekta = get(all_roles, name='Прихожанин')
        if is_traus(ctx, member):
            return
        await ctx.send(box(f'Добро пожаловать в секту, {member.display_name}!'))
        await set_permissions(channels.MERY, member, read_messages=True, send_messages=True)
        await member.add_roles(sekta)

    @commands.command(name='изсекты', help='выйти из этой криповой секты')
    async def exit_sekta(self, ctx):
        all_roles = ctx.guild.roles
        sekta = get(all_roles, name='Прихожанин')
        if sekta in ctx.author.roles:
            await ctx.author.remove_roles(sekta)
            await send_by_bot(ctx, file=discord.File('files/media/sekta.jpg'), delete=True)
            await set_permissions(channels.MERY, ctx.author, send_messages=False)

    @commands.command(help='ToT')
    async def tavern(self, ctx):
        msg = await send_by_bot(ctx, tavern_emoji, delete=True)
        for emoji in ('🇴', '🇫', '🇹', '🇦', '🇱', '🇪', '🇸'):
            await msg.add_reaction(emoji)

    @commands.command(name='переиграл', help='Переиграл и уничтожил')
    async def meme_win(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        author = await get_renferenced_author(ctx)
        member = member or author
        if member:
            text = f"{ctx.author.mention} переиграл и уничтожил {member.mention}"
            embed = discord.Embed()
            embed.set_image(url=find_gif(search_term='переиграл', limit=1))
            embed.add_field(name=f"Думали я вас не переиграю?", value=text)
            await ctx.send(embed=embed, reference=ctx.message.reference)

    @commands.command(name='пять', help='Дать пять')
    async def five(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        author = await get_renferenced_author(ctx)
        member = member or author
        if member:
            text = f"{ctx.author.mention} даёт пять {member.mention}!"
            embed = discord.Embed(description=text)
            embed.set_image(url=find_gif(search_term='highfive', limit=20))
            await ctx.send(embed=embed, reference=ctx.message.reference)

    @commands.command(name='факт', help='рандомный факт')
    async def fact(self, ctx):
        url = 'https://randstuff.ru/fact/'
        pattern = r'(?<=Факт:</h1><div id="fact"><table class="text"><tr><td>).*(?=</td>)'
        resp = requests.get(url)
        text = re.findall(pattern=pattern, string=resp.content.decode('utf8'))[0]
        await send_by_bot(ctx, box(text), delete=True)

    @commands.command(help='РОЦК!')
    async def rockon(self, ctx):
        search_term = 'rockon'
        limit = 20
        await send_by_bot(ctx, find_gif(search_term, limit), delete=True)

    @commands.command(name='горит', help='горииииит!')
    async def fire(self, ctx):
        search_term = 'ass on fire'
        limit = 5
        message = await quote_renferenced_message(ctx)
        await send_by_bot(ctx, message, find_gif(search_term, limit), delete=True)

    @commands.command(name='лого', help='лого гильдии')
    async def logo(self, ctx):
        await ctx.send(ctx.guild.icon_url)

    @commands.command(name='гц', help='поздравить')
    async def gc(self, ctx):
        message = await quote_renferenced_message(ctx)
        await send_by_bot(ctx, message, file=discord.File('files/media/gc.png'), delete=True)

    @commands.command(name='стат', help='статистика по таверне')
    async def stat(self, ctx):
        await ctx.message.delete()
        start_time = datetime.strptime("26.04.2021", "%d.%m.%Y")
        current_time = datetime.utcnow() + timedelta(hours=3)

        beer = get_value('beer')
        ale = get_value('ale')
        wine = get_value('wine')
        vodka = get_value('vodka')
        honey = get_value('honey')
        slap = get_value('slap')

        msg = f"Статистика по таверне за {(current_time - start_time).days} дней.\n" \
              f"Выпито:\n" \
              f"{beer} кружек пива\n" \
              f"{ale} литров эля\n" \
              f"{honey} бочек медовухи\n" \
              f"{wine} бокалов вина\n" \
              f"{vodka} бутылок водки\n\n" \
              f"Выдано {slap} шапалахов."
        await ctx.send(box(msg))

    @commands.command(name='стол', help='перевернуть стол')
    async def table(self, ctx):
        if table_turn_over[0]:
            await send_by_bot(ctx, '(╮°-°)┳┳', delete=True)
            table_turn_over[0] = False
        else:
            await send_by_bot(ctx, '( ╯°□°)╯┻┻', delete=True)
            table_turn_over[0] = True


bot.add_cog(FunCommands())
