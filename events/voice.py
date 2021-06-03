import discord
from discord.utils import get

from constants import categories, channels
from init_bot import bot
from utils.states import voice_owners


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
