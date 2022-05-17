from discord.ext.commands import Cog, CheckFailure, command, has_permissions

from ..db import db


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="prefix")
    @has_permissions(administrator=True)
    async def change_prefix(self, ctx, new: str):
        if len(new) > 2:
            await ctx.send("The prefix cannot be longer than 2 characters in length")
        else:
            db.execute("UPDATE servers SET ServerPrefix = ? WHERE ServerID = ?", new, ctx.guild.id)
            await ctx.send(f"Prefix has been set to {new}")

    @change_prefix.error
    async def change_prefix_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("You need to be an Admin to do that.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Misc")


def setup(bot):
    bot.add_cog(Misc(bot))
