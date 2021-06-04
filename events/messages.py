from datetime import date

import discord
from discord.utils import get

from commands import automoderation, send_by_bot
from constants import channels
from init_bot import bot
from utils.guild_utils import check_for_beer, find_animated_emoji, get_renference_author


class MessageHandler:
    def __init__(self, message: discord.Message):
        self.message = message

    async def swear_moderation(self):
        no_moderation = (channels.REQUEST, channels.JOIN, channels.MEMES)

        if self.message.channel.id not in no_moderation:
            await automoderation(self.message)

    async def on_mems_channel(self):
        if self.message.channel.id == channels.MEMES:
            if self.message.content:
                await self.message.delete()

    async def on_join_to_guild_channel(self):
        if self.message.channel.id == channels.JOIN:  # вступление-в-гильдию
            inv_gi_channel: discord.TextChannel = get(self.message.channel.guild.channels,
                                                      id=channels.REQUEST)  # заявки-в-ги

            embed = discord.Embed(description=f"{date.today()}\n{self.message.content}")
            embed.set_thumbnail(url=self.message.author.avatar_url)

            await inv_gi_channel.send(f"<@{self.message.author.id}>", embed=embed)
            await self.message.delete()

    async def replace_animated_emoji(self) -> list:
        animated_emojis_ids = []

        content = self.message.content
        words = set(content.split(':'))
        for word in words:
            emoji = find_animated_emoji(word)
            if emoji and f':{word}:' in content:  # only 1 word without ::
                animated_emojis_ids.append(emoji.strip(">").split(':')[-1])
                content = content.replace(f':{word}:', emoji)
        self.message._handle_content(content)

        return animated_emojis_ids

    async def send_message(self, is_animated: bool):
        ctx = await bot.get_context(self.message)

        if is_animated:
            if self.message.author.bot:
                return
            # todo переделать
            # reference_author = await get_renference_author(ctx)
            # await send_by_bot(ctx, f"{reference_author.mention if reference_author else ''}\n{self.message.content}", delete=True)
            await send_by_bot(ctx, self.message.content, delete=True)
        await bot.process_commands(self.message)

    async def add_reactions(self, animated_emojis_ids):
        ctx = await bot.get_context(self.message)

        message_id = ctx.message.reference.message_id
        message = await ctx.fetch_message(message_id)
        for emoji_id in animated_emojis_ids:
            await message.add_reaction(await ctx.guild.fetch_emoji(emoji_id))


@bot.event
async def on_message(message: discord.Message):
    handler = MessageHandler(message)

    check_for_beer(message.content)

    animated_emojis_ids = await handler.replace_animated_emoji()
    is_animated = animated_emojis_ids != []

    await handler.swear_moderation()
    await handler.on_mems_channel()
    await handler.on_join_to_guild_channel()

    await handler.send_message(is_animated)
    if message.reference:
        await handler.add_reactions(animated_emojis_ids)
