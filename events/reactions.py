import discord

from commands._mute_control import _add_mute
from constants import Members, Messages, Channels, vote_reactions
from init_bot import bot
from utils.format import box
from utils.guild_utils import set_permissions, get_class_roles, check_for_beer, get_channel


class ReactionHandler:
    def __init__(self,
                 payload: discord.RawReactionActionEvent,
                 emoji: discord.Emoji,
                 guild: discord.Guild,
                 member: discord.Member,
                 channel: discord.TextChannel,
                 message: discord.Message
                 ):
        self.payload = payload
        self.emoji = emoji
        self.guild = guild
        self.channel = channel
        self.member = member
        self.message = message

    async def on_traus_reaction(self):
        if self.emoji.name == 'approved' and self.payload.user_id != Members.TRAUS:
            await self.message.remove_reaction(self.emoji, self.member)

    async def on_samka_reaction(self):
        if self.emoji.name == 'delete' and self.payload.user_id in [Members.TRAUS, Members.SAMKA]:
            await self.message.delete()
            await self.message.channel.send(
                box('Аниме на сервере осуждается и удаляется.'),
                file=discord.File('files/media/no_anime.jpg')
            )
            await _add_mute(self.message.author, time=30)

    async def on_private_room_reaction(self):
        if self.payload.message_id == Messages.ROOMS:
            if self.emoji.name == '🇩':
                perms_flag = False
                for role in self.payload.member.roles:
                    if role.name in ['Совет ги', 'ToT', 'Верховная жрица', 'Верховный жрец', 'Сектант']:
                        perms_flag = True
                await set_permissions(Channels.SEKTA, self.member, read_messages=True, send_messages=perms_flag)
            elif self.emoji.name == '🇰':
                await set_permissions(Channels.KEFIR, self.member, read_messages=True, send_messages=True)
            else:
                await self.message.clear_reaction(self.emoji)

    async def on_class_channels_reaction(self):
        if self.payload.message_id == Messages.CHOOSE_CLASS:
            roles_dict = get_class_roles(self.guild)
            if self.emoji.name in roles_dict:
                await self.member.add_roles(roles_dict[self.emoji.name])
            else:
                await self.message.clear_reaction(self.emoji)

    async def on_vote_reaction(self):
        # can be lag of quick click
        if self.message.embeds:
            if all([
                self.member != self.guild.get_member(Members.BOT),
                'Опрос от' in str(self.message.embeds[0].footer.text),
                str(self.emoji) in vote_reactions
            ]):
                opposite = vote_reactions[0] if str(self.emoji) == vote_reactions[1] else vote_reactions[1]
                for old_reaction in self.message.reactions:
                    if str(old_reaction) == opposite:
                        async for user in old_reaction.users():
                            if user == self.member:
                                await self.message.remove_reaction(old_reaction, self.member)


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    emoji: discord.Emoji = payload.emoji
    guild: discord.Guild = bot.get_guild(payload.guild_id)
    member: discord.Member = await guild.fetch_member(payload.user_id)
    channel: discord.TextChannel = get_channel(payload.channel_id)
    message: discord.Message = await channel.fetch_message(payload.message_id)

    handler = ReactionHandler(payload=payload, emoji=emoji, guild=guild, member=member, channel=channel, message=message)

    check_for_beer(emoji)

    await handler.on_traus_reaction()
    await handler.on_samka_reaction()
    await handler.on_private_room_reaction()
    await handler.on_class_channels_reaction()
    await handler.on_vote_reaction()


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    emoji = payload.emoji
    guild = bot.get_guild(payload.guild_id)
    member: discord.Member = await guild.fetch_member(payload.user_id)

    if payload.message_id == Messages.ROOMS:
        if emoji.name == '🇩':
            await set_permissions(Channels.SEKTA, member, read_messages=False, send_messages=False)
        if emoji.name == '🇰':
            await set_permissions(Channels.KEFIR, member, read_messages=False, send_messages=False)

    if payload.message_id == Messages.CHOOSE_CLASS:
        roles_dict = get_class_roles(guild)
        await member.remove_roles(roles_dict[emoji.name])
