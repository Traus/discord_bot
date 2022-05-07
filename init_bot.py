from random import randint

import discord
from discord.ext import commands
from discord.ext.commands import MinimalHelpCommand

from utils.format import create_embed

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
ending_note = '`!help <команда> - для подробной информации о команде.`\n' \
          '`!help <категория> - для информации по категории.`'


class ShortHelp(MinimalHelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self.color = options.pop(
            "color",
            discord.Color.from_rgb(randint(0, 255), randint(0, 255), randint(0, 255)),
        )

    async def send_pages(self):
        destination = self.get_destination()
        e = create_embed(description='')
        for page in self.paginator.pages:
            e.description += page
        await destination.send(embed=e)

    def get_opening_note(self):
        return

    def get_ending_note(self):
        return ending_note

    def add_bot_commands_formatting(self, commands, heading):
        """Adds the minified bot heading with commands to the output.

        The formatting should be added to the :attr:`paginator`.

        The default implementation is a bold underline heading followed
        by commands separated by an EN SPACE (U+2002) in the next line.

        Parameters
        -----------
        commands: Sequence[:class:`Command`]
            A list of commands that belong to the heading.
        heading: :class:`str`
            The heading to add to the line.
        """
        if commands:
            cmds = [f"`{c.name}`" for c in commands]

            self.paginator.add_line('**%s**' % heading)
            self.paginator.add_line(', '.join(cmds), empty=True)

    def add_command_formatting(self, command):
        """A utility function to format commands and groups.

        Parameters
        ------------
        command: :class:`Command`
            The command to format.
        """

        if command.description:
            self.paginator.add_line(command.description, empty=True)

        signature = self.get_command_signature(command)
        if command.aliases:
            self.paginator.add_line(signature)
            self.add_aliases_formatting(command.aliases)
        else:
            self.paginator.add_line(f'```{signature}```', empty=True)

        if command.help:
            try:
                self.paginator.add_line(f'`{command.help}`', empty=True)
            except RuntimeError:
                for line in command.help.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()

    async def send_cog_help(self, cog):
        bot = self.context.bot
        if bot.description:
            self.paginator.add_line(bot.description, empty=True)

        note = self.get_opening_note()
        if note:
            self.paginator.add_line(note, empty=True)

        if cog.description:
            self.paginator.add_line(f'__**{cog.description}**__', empty=True)

        filtered = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)
        if filtered:
            self.paginator.add_line('```%s```' % (cog.qualified_name))
            for command in filtered:
                self.add_subcommand_formatting(command)

            note = self.get_ending_note()
            if note:
                self.paginator.add_line()
                self.paginator.add_line(note)

        await self.send_pages()


bot.help_command = ShortHelp(
    no_category='Разное',
    ending_note=ending_note,
    index_title='Доступные группы команд',
    active_time=60,
    commands_heading='Команды:',
)
