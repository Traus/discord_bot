from datetime import date

import discord
from discord.utils import get

from commands._mute_control import automoderation
from constants import Channels, Members
from init_bot import bot
from utils.format import create_embed, send_by_bot
from utils.guild_utils import check_for_beer, find_animated_emoji, get_referenced_author, get_members_by_role, \
    is_traus, quote_referenced_message, random_emoji, get_channel


class MessageHandler:
    def __init__(self, message: discord.Message):
        self.message = message

    async def if_todo(self):
        todo_pattern = f'<#{Channels.TODO}> '
        if self.message.content.startswith(todo_pattern) and self.message.author.id == Members.TRAUS:
            todo_channel: discord.TextChannel = get(self.message.channel.guild.channels, id=Channels.TODO)
            await todo_channel.send(self.message.content.replace(todo_pattern, ''))

    async def swear_moderation(self):
        no_moderation = (
            Channels.REQUEST, Channels.JOIN, Channels.MEMES,
            Channels.SEKTA, Channels.FIRE, Channels.DELETED,
            Channels.TODO, Channels.REQUEST_ALIANCE
        )

        if self.message.channel.id not in no_moderation:
            await automoderation(self.message)

    async def on_mems_channel(self):
        if self.message.channel.id == Channels.MEMES:
            if self.message.content:
                await self.message.delete()

    async def on_join_to_guild_channel(self):
        if self.message.channel.id == Channels.JOIN:  # вступление-в-гильдию
            inv_gi_channel: discord.TextChannel = get_channel(Channels.REQUEST)  # заявки-в-ги

            embed = create_embed(description=f"{date.today()}\n{self.message.content}",
                                 thumbnail=self.message.author.avatar_url)

            await inv_gi_channel.send(f"<@{self.message.author.id}>", embed=embed)
            await self.message.delete()

    async def on_join_to_aliance_channel(self):
        if self.message.channel.id == Channels.JOIN_ALIANCE:
            inv_channel: discord.TextChannel = get_channel(Channels.REQUEST_ALIANCE)

            embed = create_embed(description=f"{date.today()}\n{self.message.content}",
                                 thumbnail=self.message.author.avatar_url)

            await inv_channel.send(f"<@{self.message.author.id}>", embed=embed)
            await self.message.delete()

    # async def for_hellman(self):
    #     if self.message.author.id == members.HELLMAN:
    #         await self.message.add_reaction('🍆')

    async def replace_animated_emoji(self) -> list:
        animated_emojis = []

        if self.message.author.bot:
            return animated_emojis

        content = self.message.content
        new_content = content

        if ":" in content:
            words = set(content.split(':'))
            for word in words:
                emoji = find_animated_emoji(word)
                if emoji and emoji not in content and f':{word}:' in content:  # only 1 word without ::
                    animated_emojis.append(emoji)
                    new_content = new_content.replace(f':{word}:', emoji)

        self.message._handle_content(new_content)
        return animated_emojis

    def is_only_emojis(self, animated_emojis) -> bool:
        content = self.message.content
        for emoji in animated_emojis:
            content = content.replace(emoji, '')
        return not bool(content.strip())

    async def send_vacation_message(self):
        vacation_members = get_members_by_role(name="Отпуск")
        for member in vacation_members.members:
            if str(member.id) in self.message.content:
                if is_traus(member):
                    bot_msg = await self.message.channel.send(f"Траус не бухает, Траус отдыхает!")
                else:
                    bot_msg = await self.message.channel.send(f"{member.display_name} отдыхает!")
                await bot_msg.add_reaction(random_emoji())

    async def send_message(self, animated_emojis: list):
        ctx = await bot.get_context(self.message)

        if animated_emojis:
            await ctx.message.delete()
            if not (self.is_only_emojis(animated_emojis) and self.message.reference):
                message = await quote_referenced_message(ctx)
                await send_by_bot(ctx, message, self.message.content)

    async def send_animated_reactions(self, animated_emojis):
        if self.message.reference and self.is_only_emojis(animated_emojis):
            await self.add_reactions(animated_emojis)

    async def add_reactions(self, animated_emojis):
        ctx = await bot.get_context(self.message)

        message_id = ctx.message.reference.message_id
        message = await ctx.fetch_message(message_id)
        for emoji in animated_emojis:
            await message.add_reaction(await ctx.guild.fetch_emoji(emoji.strip(">").split(':')[-1]))


@bot.event
async def on_message(message: discord.Message):
    handler = MessageHandler(message)

    check_for_beer(message.content)

    animated_emojis = await handler.replace_animated_emoji()

    await handler.if_todo()
    await handler.swear_moderation()
    await handler.on_mems_channel()
    await handler.on_join_to_guild_channel()
    await handler.on_join_to_aliance_channel()
    # await handler.for_hellman()

    await handler.send_vacation_message()
    await handler.send_message(animated_emojis)
    await handler.send_animated_reactions(animated_emojis)

    await bot.process_commands(message)


@bot.event
async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent):
    message = payload.cached_message
    if message is None:
        return
    content = message.content
    files = [await attachment.to_file() for attachment in message.attachments]
    author: discord.Member = message.author
    channel: discord.TextChannel = message.channel
    deleted: discord.TextChannel = get_channel(Channels.DELETED)

    embed = create_embed(description=content,
                         fields=[
                             ('автор', author.display_name),
                             ('канал', channel.mention),
                         ])
    await deleted.send(embed=embed, files=files)
