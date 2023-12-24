import asyncio
import re
from datetime import datetime, timedelta, timezone, time

import discord
import requests
from discord.ext import commands, tasks
from discord.utils import get

from commands._base_command import Command
from commands._mute_control import _add_mute
from constants import Channels, tavern_emoji, beer_emoji
from database.stat import add_value, get_value

from utils.format import box, send_by_bot, create_embed
from utils.guild_utils import get_members_by_role, get_bot_avatar, create_and_send_slap, has_immune, \
    set_permissions, get_referenced_author, is_traus, quote_referenced_message, chance, get_channel, get_role_by_name
from utils.states import table_turn_over, immune_until
from utils.tenor_gifs import find_gif
from utils.toasts import find_toast


# If no tzinfo is given then UTC is assumed.
schedule = time(hour=7, minute=0)  # UTC, 10 Msk


def get_next_day_in_seconds() -> int:
    today = datetime.utcnow()
    next_date = datetime.combine(today, schedule)
    if today > next_date:
        next_date += timedelta(days=1)
    return (datetime.utcnow() - next_date).seconds


class FunCommands(Command, name='Веселье'):
    """Рофлы и пасхалки"""

    def __init__(self, bot):
        super().__init__(bot)
        # self.send_daily_toast.start()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()  # Make sure your guild cache is ready so the channel can be found via get_channel
        while True:
            next_iteration = get_next_day_in_seconds()
            await asyncio.sleep(next_iteration)

            toast = find_toast()
            channel = get_channel(channel_id=Channels.GUILD)
            tot = get_role_by_name(name="ToT")
            msg = f'{tot.mention}\n{toast}!\nДавайте же поднимем наши бокалы в этот прекрасный день!'
            await channel.send(box(msg))

    @commands.command(name='осуждаю', help='Осудить!')
    async def blame(self, ctx):
        message = await quote_referenced_message(ctx)
        await send_by_bot(ctx, message, file=discord.File('files/media/tom.jpg'), delete=True)

    @commands.command(name='одобряю', help='Одобрить!')
    async def approve(self, ctx):
        message = await quote_referenced_message(ctx)
        search_term = 'approve'
        limit = 10
        await send_by_bot(ctx, message, find_gif(search_term, limit), delete=True)

    @commands.command(name='шапалах', help='Втащить')
    async def slap(self, ctx, members: commands.Greedy[discord.Member], bot: str = None):
        await ctx.message.delete()

        from_bot = bot is not None and bot == 'bot'
        if not members:
            author = await get_referenced_author(ctx)
            if author is not None:
                members = [author]
            else:
                members = [ctx.author]

        for member in set(members):
            avatar_from = ctx.author.avatar_url
            avatar_to = member.avatar_url

            # check immune
            if has_immune(member) and not from_bot:
                stamp = immune_until[member]
                imune = stamp - datetime.timestamp(datetime.now())
                await ctx.send(box(f'У {member.display_name} иммунитет на {int(imune//60) + 1} минут!'))
                continue

            # chance to dodge
            dodge = chance(5)
            if dodge:
                await ctx.send(box(f'Суперуклон у {member.display_name}!'))
                stamp = datetime.timestamp(datetime.now()) + 5*60
                immune_until[member] = stamp
                continue

            if from_bot:
                avatar_from = get_bot_avatar()

            gif = is_traus(ctx.author) or chance(5)
            add_value('slap')

            # check every 100 slap
            if not (get_value('slap') % 100):
                text = f"{ctx.author.mention} ультует по {member.mention}!"
                embed = create_embed(description=text,
                                     image=find_gif(search_term='super slap', limit=1))
                await ctx.send(embed=embed, reference=ctx.message.reference)
                continue

            # check 10000 slap temp bullshit
            if get_value('slap') == 10000:
                text = f"{ctx.author.mention} выдает супер эпический шапалах по {member.mention} " \
                       f"и вышибает {member.mention} из Таверны"
                embed = create_embed(description=text,
                                     image=find_gif(search_term='super punch', limit=1))
                await ctx.send(embed=embed, reference=ctx.message.reference)
                await ctx.send(f"{member.display_name} :regional_indicator_f:")
                await _add_mute(member, 2*60)
                continue
            await create_and_send_slap(ctx, avatar_from, avatar_to, gif=gif, from_bot=from_bot)

    @commands.command(name='аватар', help='посмотреть аватарку')
    async def avatar(self, ctx, member: discord.Member = None):
        await ctx.message.delete()

        if member is None:
            member = ctx.author
        await ctx.send(member.avatar_url)

    @commands.command(name='секта', help='список участников секты кровавой Мери')
    async def sekta(self, ctx):
        sekta = get_members_by_role(name='Сектант')

        msg = ''
        for role in [sekta]:
            members = role.members
            if members:
                m = '\n'.join([role.members[i].display_name for i in range(len(role.members))])
                msg += f"{role.role}:\n{m}\n"
        await ctx.send(box(msg))

    @commands.command(name='всекту', help='принять в секту беспредела')
    async def join_sekta(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        all_roles = ctx.guild.roles
        sekta = get(all_roles, name='Сектант')
        if is_traus(member):
            return
        await ctx.send(box(f'Добро пожаловать в секту, {member.display_name}!'))
        await set_permissions(Channels.SEKTA, member, read_messages=True, send_messages=True)
        await member.add_roles(sekta)

    @commands.command(name='изсекты', help='выйти из этой криповой секты')
    async def exit_sekta(self, ctx):
        all_roles = ctx.guild.roles
        sekta = get(all_roles, name='Сектант')
        if sekta in ctx.author.roles:
            await ctx.author.remove_roles(sekta)
            await send_by_bot(ctx, file=discord.File('files/media/sekta.jpg'), delete=True)
            await set_permissions(Channels.SEKTA, ctx.author, send_messages=False)

    @commands.command(help='ToT')
    async def tavern(self, ctx):
        msg = await send_by_bot(ctx, tavern_emoji, delete=True)
        for emoji in ('🇴', '🇫', '🇹', '🇦', '🇱', '🇪', '🇸'):
            await msg.add_reaction(emoji)

    @commands.command(name='токсик', help='фу, токсик')
    async def toxic(self, ctx):
        message = await quote_referenced_message(ctx)
        toxic_emoji = f"{tavern_emoji}    :regional_indicator_o: :regional_indicator_f:"
        msg = await send_by_bot(ctx, message, toxic_emoji, delete=True)
        for emoji in ('🇹', '🇴', '🇽', 'ℹ', '🇨', '🇸', '<:emoji_99:866240571759788073>'):
            await msg.add_reaction(emoji)

    @commands.command(name='переиграл', help='Переиграл и уничтожил')
    async def meme_win(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        author = await get_referenced_author(ctx)
        member = member or author
        if member:
            text = f"{ctx.author.mention} переиграл и уничтожил {member.mention}"
            embed = create_embed(image=find_gif(search_term='переиграл', limit=1),
                                 fields=[("Думали я вас не переиграю?", text)])
            await ctx.send(embed=embed, reference=ctx.message.reference)

    @commands.command(name='пять', help='Дать пять')
    async def five(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        author = await get_referenced_author(ctx)
        member = member or author
        if member:
            text = f"{ctx.author.mention} даёт пять {member.mention}!"
            embed = create_embed(description=text,
                                 image=find_gif(search_term='highfive', limit=50))
            await ctx.send(embed=embed, reference=ctx.message.reference)

    @commands.command(name='чок', help='Чокнуться')
    async def chin(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        author = await get_referenced_author(ctx)
        member = member or author
        if member:
            text = f"{ctx.author.mention} чокается с {member.mention}!"
            embed = create_embed(description=text,
                                 image=find_gif(search_term='cheers', limit=10))
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
        message = await quote_referenced_message(ctx, limit=50)
        await send_by_bot(ctx, message, find_gif(search_term, limit), delete=True)

    @commands.command(name='горит', help='горииииит!')
    async def fire(self, ctx):
        search_term = 'ass on fire'
        limit = 5
        message = await quote_referenced_message(ctx, limit=50)
        await send_by_bot(ctx, message, find_gif(search_term, limit), delete=True)

    @commands.command(name='лого', help='лого гильдии')
    async def logo(self, ctx):
        await ctx.send(ctx.guild.icon_url)

    @commands.command(name='гц', help='поздравить')
    async def gc(self, ctx):
        message = await quote_referenced_message(ctx)
        await send_by_bot(ctx, message, file=discord.File('files/media/gc.png'), delete=True)

    @commands.command(name='стат', help='статистика по Таверне')
    async def stat(self, ctx, target: str = 'таверна'):
        await ctx.message.delete()
        start_time = datetime.strptime("26.04.2021", "%d.%m.%Y")
        current_time = datetime.utcnow() + timedelta(hours=3)

        beer = dict(
            names=['пиво', 'beer', beer_emoji['beer']],
            stat_on='пиву',
            value=f"{get_value('beer')} кружек пива",
        )
        ale = dict(
            names=['эль', 'ale', beer_emoji['ale']],
            stat_on='элю',
            value=f"{get_value('ale')} литров эля",
        )
        honey = dict(
            names=['медовуха', 'honey', beer_emoji['honey']],
            stat_on='медовухе',
            value=f"{get_value('honey')} бочек медовухи",
        )
        wine = dict(
            names=['вино', 'wine', beer_emoji['wine']],
            stat_on='вину',
            value=f"{get_value('wine')} бокалов вина",
        )
        vodka = dict(
            names=['водка', 'самогон', 'vodka', beer_emoji['vodka']],
            stat_on='водке',
            value=f"{get_value('vodka')} бутылок водки",
        )
        slap = dict(
            names=['шапалах', 'slap'],
            stat_on='шапалахам',
            value=f"Выдано {get_value('slap')} шапалахов.",
        )
        tavern = dict(
            names=['таверна'],
            stat_on='таверне',
            value=f"Выпито:\n"
                  f"{beer['value']}\n"
                  f"{ale['value']}\n"
                  f"{honey['value']}\n"
                  f"{wine['value']}\n"
                  f"{vodka['value']}\n\n"
                  f"{slap['value']}"
        )

        for choice in [beer, ale, honey, wine, vodka, slap, tavern]:
            if target in choice['names']:
                msg = f"Статистика по {choice['stat_on']} за {(current_time - start_time).days} дней.\n" \
                      f"{choice['value']}"
                await ctx.send(box(msg))

    @commands.command(name='стол', help='перевернуть стол')
    async def table(self, ctx):
        if table_turn_over[ctx.channel.id]:
            await send_by_bot(ctx, '(╮°-°)┳┳', delete=True)
            table_turn_over[ctx.channel.id] = False
        else:
            await send_by_bot(ctx, '( ╯°□°)╯┻┻', delete=True)
            table_turn_over[ctx.channel.id] = True

    @commands.command(name='тост', help='Повод выпить')
    async def toast(self, ctx):
        toast = find_toast()
        msg = f'{toast}\nЗамечательный повод выпить! Погнали!'
        await ctx.send(box(msg))

    @tasks.loop(time=schedule)
    async def send_daily_toast(self):
        await self.bot.wait_until_ready()  # Make sure your guild cache is ready so the channel can be found via get_channel

        toast = find_toast()
        channel = get_channel(channel_id=Channels.GUILD)
        tot = get_role_by_name(name="ToT")
        msg = f'{tot.mention}\n{toast}!\nДавайте же поднимем наши бокалы в этот прекрасный день!'
        await channel.send(box(msg))


def setup(bot):
    bot.add_cog(FunCommands(bot))
