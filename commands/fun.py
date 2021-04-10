import re

import discord
import requests
from discord.ext import commands
from discord.utils import get

from constants import channels, tavern_emoji
from init_bot import bot
from utils.format import box
from utils.guild_utils import get_member_by_role, get_bot_avatar, create_and_send_slap, has_immune, \
    set_permissions
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
        msg = f"{main.role}:\n{main.members[0].display_name}\n"
        msg += f"{zam.role}:\n{zam.members[0].display_name}\n"
        msg += f"{rip.role}:\n{rip.members[0].display_name}\n\nПрихожане:\n"
        for member in sekta.members:
            msg += member.display_name + '\n'
        await ctx.send(box(msg))

    @commands.command(name='всекту', help='принять в культ')
    @commands.has_any_role("Совет ги", "Крот с ЕС", "Верховная жрица", "Верховный жрец", "Палач")
    async def join_sekta(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        all_roles = ctx.guild.roles
        sekta = get(all_roles, name='Прихожанин')
        mery = get(all_roles, name='Верховная жрица')
        warlock = get(all_roles, name='Верховный жрец')
        for role in [mery, warlock]:
            if role in member.roles:
                return
            if role in ctx.author.roles:
                await ctx.send(box(f'Добро пожаловать в секту, {member.display_name}!'))
                await set_permissions(channels.MERY, member._user.id, read_messages=True, send_messages=True)
                await member.add_roles(sekta)

    @commands.command(name='изсекты', help='выйти из этой криповой секты')
    async def exit_sekta(self, ctx):
        all_roles = ctx.guild.roles
        sekta = get(all_roles, name='Прихожанин')
        if sekta in ctx.author.roles:
            await ctx.author.remove_roles(sekta)
            await ctx.send(file=discord.File('files/media/sekta.jpg'))
            await set_permissions(channels.MERY, ctx.author._user.id, send_messages=False)

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
        embed.set_image(url='https://i.ytimg.com/vi/cD4avzML2rw/hqdefault.jpg')
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


bot.add_cog(FunCommands())
