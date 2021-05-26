import discord
from discord.utils import get

from constants import members, messages, channels, vote_reactions
from init_bot import bot
from utils.guild_utils import set_permissions, get_class_roles


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
        if self.emoji.name == 'approved' and self.payload.user_id != members.TRAUS:
            await self.message.remove_reaction(self.emoji, self.member)

    async def on_private_room_reaction(self):
        if self.payload.message_id == messages.ROOMS:
            if self.emoji.name == '🇩':
                perms_flag = False
                for role in self.payload.member.roles:
                    if role.name in ['Совет ги', 'ToT', 'Крот с ЕС', 'Верховная жрица', 'Верховный жрец', 'Палач', 'Прихожанин']:
                        perms_flag = True
                await set_permissions(channels.MERY, self.member, read_messages=True, send_messages=perms_flag)
            elif self.emoji.name == '🇰':
                await set_permissions(channels.KEFIR, self.member, read_messages=True, send_messages=True)
            else:
                await self.message.clear_reaction(self.emoji)

    async def on_rules_channel_reaction(self):
        if self.payload.message_id == messages.RULES:
            if self.emoji.name == '✅':
                guest = get(self.guild.roles, name='Гость')
                if len(self.member.roles) == 1 or (len(self.member.roles) == 2 and get(self.guild.roles, name='Muted') in self.member.roles):
                    await self.member.add_roles(guest)
                    emoji = await self.member.guild.fetch_emoji(811516186453082133)
                    guest_channel: discord.TextChannel = bot.get_channel(channels.GUEST)
                    await guest_channel.send(f'{self.member.mention} {emoji}')

    async def on_class_channels_reaction(self):
        if self.payload.message_id == messages.CHOOSE_CLASS:
            roles_dict = get_class_roles(self.guild)
            if self.emoji.name in roles_dict:
                await self.member.add_roles(roles_dict[self.emoji.name])
            else:
                await self.message.clear_reaction(self.emoji)

    async def on_vote_reaction(self):
        # can be lag of quick click
        if self.message.embeds:
            if all([
                self.member != self.guild.get_member(members.BOT),
                'Опрос от' in str(self.message.embeds[0].footer.text),
                str(self.emoji) in vote_reactions
            ]):
                opposite = vote_reactions[0] if str(self.emoji) == vote_reactions[1] else vote_reactions[1]
                for old_reaction in self.message.reactions:
                    if str(old_reaction) == opposite:
                        async for user in old_reaction.users():
                            if user == self.member:
                                await self.message.remove_reaction(old_reaction, self.member)
