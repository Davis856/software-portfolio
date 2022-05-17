# TODO: Modify it so it will work for multiple servers (channel ids, guild ids, user ids)

from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="hello", aliases=["hi", "sup"], description="Basic hello command")
    @cooldown(1, 5, BucketType.user)
    async def hello(self, ctx):
        await ctx.send(f"Welcome to Haragems, {ctx.author.mention}!")

    @command(name="test", aliases=["tst"], description="Test lmao")
    @cooldown(1, 5, BucketType.user)
    async def test(self, ctx):
        await ctx.send(f"Test bruh, {ctx.author.mention}!")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
