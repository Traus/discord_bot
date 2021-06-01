import os
import discord
from datetime import date
from constants import *

# commands
from commands import *
from on_reaction import ReactionHandler
from utils.guild_utils import set_permissions, get_class_roles, check_for_beer, find_animated_emoji
from utils.states import voice_owners

try:
    from local_settings import TOKEN
except ImportError:
    TOKEN = os.environ.get("TOKEN")


@bot.command(pass_context=True, help='Траус ломает бота')
async def test(ctx, *args):
    # retStr = str("""```css\nThis is some colored Text```""")
    # embed = discord.Embed(title="Random test")
    # embed.add_field(name="Name field can't be colored as it seems",value=retStr)
    # await ctx.send(embed=embed)
    retStr = "```css\nпам пам```"
    await ctx.send(retStr)
    print(args)
    print(ctx.message.id)
    print(ctx.guild.roles)
    print(ctx.channel.id)


@bot.event
async def on_member_join(member: discord.Member):
    welcome = bot.get_channel(channels.WELCOME)
    text = f"""
Для доступа к каналам ознакомься с {bot.get_channel(channels.RULES).mention} и поставь под ними ✅.

-Информация о гильдии Tavern of Tales - {bot.get_channel(channels.INFO).mention}
-Заявка для вступления в гильдию (заполняется одним сообщением прямо на канале) - {bot.get_channel(channels.JOIN).mention}
-Выбрать себе классовую роль для доступа к соответствующему каналу - {bot.get_channel(channels.CHOOSE_CLASS).mention}
-Гостевая для общения - {bot.get_channel(channels.GUEST).mention}
-На сервере доступна система приватных комнат - {bot.get_channel(channels.PRIVATE_CHANNELS).mention}
{bot.get_emoji(828026991361261619)}
"""
    embed = discord.Embed(description=f"Добро пожаловать в Таверну Сказаний {member.mention}!")
    embed.set_thumbnail(url=member.avatar_url)

    await welcome.send(embed=embed)
    await welcome.send(text)
    if muted_queue[member]:
        await member.add_roles(member.guild.get_role(roles.MUTED))


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    emoji: discord.Emoji = payload.emoji
    guild: discord.Guild = bot.get_guild(payload.guild_id)
    member: discord.Member = await guild.fetch_member(payload.user_id)
    channel: discord.TextChannel = bot.get_channel(payload.channel_id)
    message: discord.Message = await channel.fetch_message(payload.message_id)

    handler = ReactionHandler(payload=payload, emoji=emoji, guild=guild, member=member, channel=channel, message=message)

    check_for_beer(emoji)

    await handler.on_traus_reaction()
    await handler.on_private_room_reaction()
    await handler.on_rules_channel_reaction()
    await handler.on_class_channels_reaction()
    await handler.on_vote_reaction()


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    emoji = payload.emoji
    guild = bot.get_guild(payload.guild_id)
    member: discord.Member = await guild.fetch_member(payload.user_id)

    if payload.message_id == messages.ROOMS:
        if emoji.name == '🇩':
            await set_permissions(channels.MERY, member, read_messages=False, send_messages=False)
        if emoji.name == '🇰':
            await set_permissions(channels.KEFIR, member, read_messages=False, send_messages=False)

    if payload.message_id == messages.CHOOSE_CLASS:
        roles_dict = get_class_roles(guild)
        await member.remove_roles(roles_dict[emoji.name])


@bot.event
async def on_message(message: discord.Message):
    no_moderation = (channels.REQUEST, channels.JOIN, channels.MEMES)

    check_for_beer(message.content)

    animated_emoji_flag = False
    content = message.content
    words = set(content.split(':'))
    for word in words:
        emoji = find_animated_emoji(word)
        if emoji:
            animated_emoji_flag = True
            content = content.replace(f':{word}:', emoji)
    message._handle_content(content)

    if message.channel.id not in no_moderation:
        await automoderation(message)

    if message.channel.id == channels.MEMES:
        if message.content:
            await message.delete()

    if message.channel.id == channels.JOIN:  # вступление-в-гильдию
        inv_gi_channel: discord.TextChannel = get(message.channel.guild.channels, id=channels.REQUEST)  # заявки-в-ги

        embed = discord.Embed(description=f"{date.today()}\n{message.content}")
        embed.set_thumbnail(url=message.author.avatar_url)

        await inv_gi_channel.send(f"<@{message.author.id}>", embed=embed)
        await message.delete()

    if animated_emoji_flag:
        # todo немного костыльно. Подумать на свежую голову
        if message.author.bot:
            return
        ctx = await bot.get_context(message)
        await send_by_bot(ctx, content, delete=True)
    await bot.process_commands(message)


@bot.event
async def on_voice_state_update(member: discord.Member, before, after):
    voice: discord.VoiceChannel = get(member.guild.channels, id=channels.VOICE)
    if after.channel == voice:
        new_voc = await voice.clone(name=f"{member.display_name}'s Channel")
        voice_owners[new_voc] = member
        await member.move_to(new_voc)
    if before.channel is not None:
        if all([before.channel.category_id == categories.PRIVATE, before.channel != voice, not before.channel.members]):
            await before.channel.delete()
            del voice_owners[before.channel]


@bot.event
async def on_member_remove(member: discord.Member):
    channel = bot.get_channel(channels.GUEST)
    await channel.send(f'{member.display_name} :regional_indicator_f:')


bot.run(TOKEN)
