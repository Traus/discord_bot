from typing import List

import discord
from discord.ext import commands
from pretty_help import PrettyHelp
from pretty_help.pretty_help import Paginator

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
ending_note = '!help команда - для подробной информации о команде.\n' \
          '!help категория - для информации по категории.'


class ShortPaginator(Paginator):
    def _add_command_fields(self, embed: discord.Embed, page_title: str, commands: List[commands.Command]):
        """
        Adds command fields to Category/Cog and Command Group pages

        Args:
            embed (discord.Embed): The page to add command descriptions
            page_title (str): The title of the page
            commands (List[commands.Command]): The list of commands for the fields
        """
        description = "```"
        for command in commands:
            if not self._check_embed(
                    embed,
                    self.ending_note,
                    command.name,
                    command.short_doc,
                    self.prefix,
                    self.suffix,
            ):
                self._add_page(embed)
                embed = self._new_page(page_title, embed.description)

            description += f"\n{command.name}"
        embed.description += f"{description}```"
        self._add_page(embed)

    def add_index(self, include: bool, title: str, bot: commands.Bot):
        """
        Add an index page to the response of the bot_help command

        Args:
            include (bool): Include the index page or not
            title (str): The title of the index page
            bot (commands.Bot): The bot instance
        """
        if include:
            index = self._new_page(title, bot.description or "")

            # todo ковыряться
            for page_no, page in enumerate(self._pages, 2):
                if not page.description:
                    description = "No Description"
                else:
                    description = page.description.split('\n')[0].strip('`')

                index.add_field(
                    name=f"{page_no}) {page.title}",
                    value=f'{self.prefix}{description}{self.suffix}',
                    inline=False,
                )
            index.set_footer(text=self.ending_note)
            self._pages.insert(0, index)
        else:
            self._pages[0].description = bot.description


class ShortHelp(PrettyHelp):
    def __init__(self, **options):
        super().__init__(**options)
        self.paginator = ShortPaginator(color=self.color)


bot.help_command = PrettyHelp(
    no_category='Разное',
    ending_note=ending_note,
    index_title='Доступные группы команд',
    active_time=60,
)
