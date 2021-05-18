import re
from datetime import datetime, timedelta

import discord
import requests
from discord.ext import commands
from discord.utils import get

from constants import channels, tavern_emoji, beer_emoji
from database.stat import add_value, get_value
from init_bot import bot
from utils.format import box
from utils.guild_utils import get_member_by_role, get_bot_avatar, create_and_send_slap, has_immune, \
    set_permissions
from utils.states import table_turn_over
from utils.tenor_gifs import find_gif


class FunCommands(commands.Cog, name='Веселье'):
    """Рофлы и пасхалки"""

    @commands.command(name='осуждаю', help='Осудить!')
    async def blame(self, ctx):
        await ctx.message.delete()
        await ctx.send(file=discord.File('files/media/tom.jpg'))

    @commands.command(name='шапалах', help='Втащить')
    async def slap(self, ctx, member: discord.Member = None, bot: str = None):
        add_value('slap')
        if member is None:
            if ctx.message.reference is not None:
                message_id = ctx.message.reference.message_id
                message = await ctx.fetch_message(message_id)
                member = message.author
            else:
                member = ctx.author

        avatar_from = ctx.author.avatar_url
        avatar_to = member.avatar_url

        if has_immune(member):
            await ctx.send(box(f'Иммунитет!'))
            return

        if bot is not None and bot == 'bot':
            avatar_from = get_bot_avatar(ctx)
            await ctx.message.delete()

        await create_and_send_slap(ctx, avatar_from, avatar_to)

    @commands.command(name='аватар', help='посмотреть аватарку')
    async def avatar(self, ctx, member: discord.Member):
        await ctx.send(member.avatar_url)

    @commands.command(name='секта', help='список участников секты кровавой Мери')
    async def sekta(self, ctx):
        main = get_member_by_role(ctx, name='Верховная жрица')
        zam = get_member_by_role(ctx, name='Верховный жрец')
        rip = get_member_by_role(ctx, name='Палач')
        sekta = get_member_by_role(ctx, name='Прихожанин')

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
        traus = get(all_roles, name='Глава ги')
        if traus in member.roles:
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
            await ctx.send(file=discord.File('files/media/sekta.jpg'))
            await set_permissions(channels.MERY, ctx.author, send_messages=False)

    @commands.command(help='ToT')
    async def tavern(self, ctx):
        msg = await ctx.send(tavern_emoji)
        for emoji in ('🇴', '🇫', '🇹', '🇦', '🇱', '🇪', '🇸'):
            await msg.add_reaction(emoji)

    @commands.command(name='переиграл', help='Переиграл и уничтожил')
    async def meme_win(self, ctx, member: discord.Member):
        await ctx.message.delete()
        text = f"{ctx.author.mention} переиграл и уничтожил {member.mention}"
        embed = discord.Embed()
        embed.set_image(url=find_gif(search_term='уничтожу', limit=1))
        embed.add_field(name=f"Думали я вас не переиграю?", value=text)
        await ctx.send(embed=embed)

    @commands.command(name='пять', help='Дать пять')
    async def five(self, ctx, member: discord.Member):
        await ctx.message.delete()
        text = f"{ctx.author.mention} даёт пять {member.mention}!"
        embed = discord.Embed(description=text)
        embed.set_image(url=find_gif(search_term='highfive', limit=20))
        await ctx.send(embed=embed)

    @commands.command(name='факт', help='рандомный факт')
    async def fact(self, ctx):
        await ctx.message.delete()
        url = 'https://randstuff.ru/fact/'
        pattern = r'(?<=Факт:</h1><div id="fact"><table class="text"><tr><td>).*(?=</td>)'
        resp = requests.get(url)
        text = re.findall(pattern=pattern, string=resp.content.decode('utf8'))[0]
        embed = discord.Embed(description=f"{ctx.author.mention}:\n{text}")
        await ctx.send(embed=embed)

    @commands.command(help='РОЦК!')
    async def rockon(self, ctx):
        search_term = 'rockon'
        limit = 20
        await ctx.send(find_gif(search_term, limit))

    @commands.command(name='горит', help='горииииит!')
    async def fire(self, ctx):
        search_term = 'ass on fire'
        limit = 5
        await ctx.send(find_gif(search_term, limit))

    @commands.command(name='лого', help='лого гильдии')
    async def logo(self, ctx):
        await ctx.send(ctx.guild.icon_url)

    @commands.command(name='гц', help='поздравить')
    async def gc(self, ctx):
        await ctx.send(file=discord.File('files/media/gc.png'))

    @commands.command(name='стат', help='статистика по таверне')
    async def stat(self, ctx):
        await ctx.message.delete()
        start_time = datetime.strptime("26.04.2021", "%d.%m.%Y")
        current_time = datetime.utcnow() + timedelta(hours=3)

        beer = get_value('beer')
        ale = get_value('ale')
        wine = get_value('wine')
        vodka = get_value('vodka')
        slap = get_value('slap')

        msg = f"Статистика по таверне.\nВыпито за {(current_time - start_time).days} дней:\n" \
              f"{beer} кружек пива\n" \
              f"{ale} литров эля\n" \
              f"{wine} бокалов вина\n" \
              f"{vodka} бутылок водки\n\n" \
              f"Выдано {slap} шапалахов."
        await ctx.send(box(msg))

    @commands.command(name='стол', help='перевернуть стол')
    async def table(self, ctx):
        await ctx.message.delete()

        if table_turn_over[0]:
            await ctx.send(f'{ctx.author.mention} (╮°-°)┳┳')
            table_turn_over[0] = False
        else:
            await ctx.send(f'{ctx.author.mention} ( ╯°□°)╯┻┻ ')
            table_turn_over[0] = True


bot.add_cog(FunCommands())
