from glob import glob

import discord
from discord.ext import commands
from discord.ext.commands import Bot as BotBase
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asyncio import sleep
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown)
from discord.errors import HTTPException, Forbidden
from discord import Embed
from datetime import datetime
from discord.ext.commands import when_mentioned_or
from discord import Intents
from ..db import db

cogs = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]

# intents zone # TODO: Do this server-sided as well.
intents = discord.Intents.default()
intents.members = True
intents.presences = True


def get_prefix(client, message):  # client = bot to avoid shadowing.
    prefix = db.field("SELECT ServerPrefix FROM servers WHERE ServerID=?", message.guild.id)
    return when_mentioned_or(prefix)(client, message)


# cog class
class Ready(object):
    def __init__(self):
        for cog in cogs:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"{cog} cog ready.")

    def all_ready(self):
        return all([getattr(self, cog) for cog in cogs])


class Bot(BotBase):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, help_command=CustomHelpCommand(), intents=intents)
        self.stdout = None
        self.token = None
        self.version = None
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)

    def setup(self):
        for cog in cogs:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog loaded")

        print("Setup complete")

    def run(self, version):
        self.version = version

        print("Running setup...")
        self.setup()

        with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
            self.token = tf.read()

        print("Running Bot...")
        super().run(self.token, reconnect=True)

    @staticmethod
    async def on_connect():
        print(f"Bot connected as {Bot.user}")

    @staticmethod
    async def on_disconnect():
        print(f"Bot disconnected.")

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(967099551569805453)
            self.stdout = self.get_channel(968165135191531540)
            self.scheduler.start()

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            print("Bot ready.")
        else:
            print("Bot reconnected.")

    async def on_error(self, error, *args, **kwargs):
        if error == "on_command_error":
            await args[0].send("ERROR.")
        else:
            await self.stdout.send("An error occurred. Contact the bot admin.")
        raise

    async def on_command_error(self, context, exception):
        if isinstance(exception, CommandNotFound):
            pass
        elif hasattr(exception, "original"):
            if isinstance(exception, Forbidden):
                await context.send("I do not have permission for that.")
            else:
                raise exception.original
        elif isinstance(exception, HTTPException):
            await context.send("Unable to send message.")
        elif isinstance(exception, BadArgument):
            pass
        elif isinstance(exception, MissingRequiredArgument):
            await context.send("One or more arguments required.")
        elif isinstance(exception, CommandOnCooldown):
            await context.send(f"Command cooldown. Try again in {exception.retry_after:,.2f} seconds.")
        else:
            raise exception

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):  # override the send_bot_help command
        embed = Embed(title="Help command", colour=self.context.author.color,
                      timestamp=datetime.utcnow())  # create the embed

        for cog, cmds in mapping.items():
            if cog is None or len(cmds) == 0:
                continue
            cmd = [f"`{self.context.prefix}{com.name}`" for com in cmds]  # get command list
            cmd_str = ' '.join(cmd)  # join them in a single long string
            embed.add_field(name=cog.qualified_name,
                            value=f"{cmd_str}",
                            inline=False)  # create the field with the long string as value

        embed.set_author(name="Katheryne", icon_url=self.context.bot.guild.icon_url)  # author of the embed
        embed.set_footer(
            icon_url=self.context.bot.guild.icon_url,
            # TODO : Change everywhere to the main server icon if multiple servers are used
            text=f"{str(self.context.bot.user).split('#')[0]}"
        )
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = Embed(title=f"{cog.qualified_name} category commands", colour=self.context.author.color,
                      timestamp=datetime.utcnow())  # create the embed
        embed.set_author(name="Katheryne", icon_url=self.context.bot.guild.icon_url)
        embed.set_footer(
            icon_url=self.context.bot.guild.icon_url,
            # TODO : Change everywhere to the main server icon if multiple servers are used.
            text=f"{str(self.context.bot.user).split('#')[0]}"
        )
        cmd = [f"`{self.context.prefix}{com.name}`" for com in cog.get_commands()]  # get command list
        cmd_str = ' '.join(cmd)  # join the list elements in a single long string
        embed.add_field(name="Commands:", value=f"{cmd_str}",
                        inline=False)  # create the embed field with the long string as value
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        await self.get_destination().send(
            f"{group.name} : {[command.name for index, command in enumerate(group.commands)]}")

    async def send_command_help(self, command):
        embed = Embed(title=f"{command.name} command", colour=self.context.author.color,
                      timestamp=datetime.utcnow())  # create the embed
        embed.set_author(name="Katheryne", icon_url=self.context.bot.guild.icon_url)
        embed.set_footer(
            icon_url=self.context.bot.guild.icon_url,
            # TODO : Change everywhere to the main server icon if multiple servers are used.
            text=f"{str(self.context.bot.user).split('#')[0]}"
        )
        embed.add_field(name="Command:", value=f"{command.name}", inline=False)
        embed.add_field(name="Description:", value=f"{command.description}", inline=False)
        aliases = [f"`{self.context.prefix}{alias}`" for alias in command.aliases]  # get alias list
        aliases_str = ' '.join(aliases)  # join the list elements in a single long string
        embed.add_field(name="Aliases:", value=f"{aliases_str}",
                        inline=False)  # create the embed with the long string as valuees

        # embed.description(f"The bot prefix is: {self.context.bot.prefix}")
        await self.get_destination().send(embed=embed)


bot = Bot()
