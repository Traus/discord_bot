import os
import discord
from datetime import date
from constants import *

# commands
from commands import *
from utils.guild_utils import set_permissions

try:
    from local_settings import TOKEN
except ImportError:
    TOKEN = os.environ.get("TOKEN")


@bot.command(pass_context=True)
async def test(ctx, *args):
    # retStr = str("""```css\nThis is some colored Text```""")
    # embed = discord.Embed(title="Random test")
    # embed.add_field(name="Name field can't be colored as it seems",value=retStr)
    # await ctx.send(embed=embed)
    retStr = "```css\nпам пам```"
    await ctx.send(retStr)
    print(args)
    # print(ctx.message.id)
    # print(ctx.message.author.id)
    print(ctx.guild.roles)
    print(ctx.channel.id)


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.message_id == messages.ROOMS:
        emoji = payload.emoji
        if emoji.name == '🇩':
            perms_flag = False
            for role in payload.member.roles:
                if role.name in ['Совет ги', 'ToT', 'Крот с ЕС', 'Первосвященник секты', 'Просвящённый культист', 'Верный адепт']:
                    perms_flag = True
            await set_permissions(channels.DOMINO, payload.user_id, read_messages=True, send_messages=perms_flag)
        if emoji.name == '🇰':
            await set_permissions(channels.KEFIR, payload.user_id, read_messages=True, send_messages=True)
        else:
            channel = bot.get_channel(channels.PRIVATE_CHANNELS)
            message = await channel.fetch_message(payload.message_id)
            await message.clear_reaction(emoji)

    if payload.message_id == messages.RULES:
        emoji = payload.emoji
        if emoji.name == '✅':
            guild = bot.get_guild(payload.guild_id)
            member: discord.Member = await guild.fetch_member(payload.user_id)
            guest = get(guild.roles, name='Гость')
            if len(member.roles) == 1 and member.roles[0].name == '@everyone':
                await member.add_roles(guest)
                channel = bot.get_channel(channels.GUEST)
                emoji = await member.guild.fetch_emoji(811516186453082133)
                await channel.send(f'{member.mention} {emoji}')


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    if payload.message_id == messages.ROOMS:
        emoji = payload.emoji
        if emoji.name == '🇩':
            await set_permissions(channels.DOMINO, payload.user_id, read_messages=False, send_messages=False)
        if emoji.name == '🇰':
            await set_permissions(channels.KEFIR, payload.user_id, read_messages=False, send_messages=False)


@bot.event
async def on_message(message: discord.Message):
    no_moderation = (channels.REQUEST, channels.JOIN, channels.MEMES)
    if message.channel.id not in no_moderation:
        await automoderation(message)

    if message.channel.id == channels.MEMES:
        if message.content:
            await message.delete()

    if message.channel.id == channels.JOIN:  # вступление-в-гильдию
        inv_gi_channel: discord.TextChannel = get(message.channel.guild.channels, id=channels.REQUEST)  # заявки-в-ги
        message.content = f"{date.today()}\n{message.content}"
        await inv_gi_channel.send(f"<@{message.author.id}>\n{box(message.content)}")
        await message.delete()
    await bot.process_commands(message)


@bot.event
async def on_member_remove(member: discord.Member):
    channel = bot.get_channel(channels.GUEST)
    await channel.send(f'{member.display_name} :regional_indicator_f:')


bot.run(TOKEN)
