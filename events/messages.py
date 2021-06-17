from datetime import date

import discord
from discord.utils import get

from commands import automoderation, send_by_bot
from constants import channels
from init_bot import bot
from utils.guild_utils import check_for_beer, find_animated_emoji, get_renference_author, get_member_by_role, is_traus


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

    async def send_vacation_message(self, message: discord.Message):
        ctx = await bot.get_context(self.message)
        vaction_members = get_member_by_role(ctx, name="Отпуск")
        for member in vaction_members.members:
            if str(member.id) in message.content:
                if is_traus(ctx, member):
                    await message.channel.send(f"Траус не бухает, Траус отдыхает!")
                else:
                    await message.channel.send(f"{member.display_name} отдыхает!")

    async def send_message(self, animated_emojis: list):
        ctx = await bot.get_context(self.message)

        if animated_emojis:
            # todo переделать ответ (красивую ссылку на сообщение) Nqn bot
            # reference_author = await get_renference_author(ctx)
            # await send_by_bot(ctx, f"{reference_author.mention if reference_author else ''}\n{self.message.content}", delete=True)
            await ctx.message.delete()
            if not (self.is_only_emojis(animated_emojis) and self.message.reference):
                await send_by_bot(ctx, self.message.content)
        await bot.process_commands(self.message)

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

    await handler.swear_moderation()
    await handler.on_mems_channel()
    await handler.on_join_to_guild_channel()

    await handler.send_vacation_message(message)
    await handler.send_message(animated_emojis)
    if message.reference:
        await handler.add_reactions(animated_emojis)
