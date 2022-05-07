import discord
from discord.utils import get

from constants import Categories, Channels
from init_bot import bot
from utils.states import voice_owners


@bot.event
async def on_voice_state_update(member: discord.Member, before, after):
    role = discord.utils.get(member.guild.roles, name='У микрофона')
    new_voice: discord.VoiceChannel = get(member.guild.channels, id=Channels.NEWVOICE)

    if not before.channel and after.channel:
        await member.add_roles(role)
    elif before.channel and not after.channel:
        await member.remove_roles(role)

    if after.channel == new_voice:
        new_voc = await new_voice.clone(name=f"{member.display_name}'s Channel")
        voice_owners[new_voc] = member
        await member.move_to(new_voc)
    if before.channel is not None:
        if all([before.channel.category_id == Categories.PRIVATE, before.channel != new_voice, not before.channel.members]):
            await before.channel.delete()
            del voice_owners[before.channel]
