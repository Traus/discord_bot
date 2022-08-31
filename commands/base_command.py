import discord
from discord.ext import commands
from discord.ext.commands import CommandError

from constants import Channels
from init_bot import bot
from utils.format import create_embed


class Command(commands.Cog):
    async def cog_command_error(self, ctx, error: CommandError):
        logs: discord.TextChannel = bot.get_channel(Channels.LOGS)

        embed = create_embed(description=str(error)[:4096],
                             fields=[
                                 ('автор', ctx.author.display_name),
                                 ('канал', ctx.channel.mention),
                                 ('сообщение', ctx.message.content),
                             ])
        await logs.send(embed=embed)
