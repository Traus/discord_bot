import discord
from discord.ext import commands
from pretty_help import PrettyHelp

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
ending_note = '!help команда - для подробной информации о команде.\n' \
          '!help категория - для информации по категории.'
bot.help_command = PrettyHelp(no_category='Разное', ending_note=ending_note, index_title='Доступые группы команд', active_time=60)
