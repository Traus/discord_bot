from datetime import date

import discord
from discord.utils import get

from commands import automoderation, send_by_bot
from constants import channels
from init_bot import bot
from utils.guild_utils import check_for_beer, find_animated_emoji


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

    async def replace_animated_emoji(self) -> bool:
        animated_emoji_flag = False

        content = self.message.content
        words = set(content.split(':'))
        for word in words:
            emoji = find_animated_emoji(word)
            if emoji and f':{word}:' in content:  # only 1 word without ::
                animated_emoji_flag = True
                content = content.replace(f':{word}:', emoji)
        self.message._handle_content(content)

        return animated_emoji_flag

    async def send_message(self, is_animated: bool):
        if is_animated:
            if self.message.author.bot:
                return
            ctx = await bot.get_context(self.message)
            await send_by_bot(ctx, self.message.content, delete=True)
        await bot.process_commands(self.message)


@bot.event
async def on_message(message: discord.Message):
    handler = MessageHandler(message)

    check_for_beer(message.content)

    is_animated = await handler.replace_animated_emoji()

    await handler.swear_moderation()
    await handler.on_mems_channel()
    await handler.on_join_to_guild_channel()

    await handler.send_message(is_animated)
