import discord
from discord import Member, Embed
from datetime import datetime
from discord.ext.commands import Cog, command, has_permissions, bot_has_permissions, CheckFailure, Greedy, cooldown
from discord.ext.commands import BucketType
from typing import Optional


class Mod(Cog):
    def __init__(self, bot):
        self.log_channel = None
        self.bot = bot

    @command(name="kick")
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send(f"Command syntax: {self.bot.user.prefix}kick [list_of_members]")
        else:
            for target in targets:
                if ctx.guild.me.top_role.position > target.top_role.position:
                    await target.kick(reason=reason)

                    embed = Embed(title="Member kicked", colour=discord.Colour.red, timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=target.avatar_url)

                    embed.set_footer(
                        icon_url=self.bot.user.avatar_url,
                        text=f"{str(self.bot.user).split('#')[0]}"
                    )

                    fields = [("Member", target.display_name, False),
                              ("Kicked by", ctx.author.display_name, False),
                              ("Reason", reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    await self.log_channel.send(embed=embed)
                else:
                    await ctx.send(f"{target.display_name} could not be kicked.")

    @kick_members.error
    async def kick_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Nice try, but you need certain permissions for this.")

    @command(name="ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send(f"Command syntax: {self.bot.user.prefix}ban [list_of_members]")
        else:
            for target in targets:
                if ctx.guild.me.top_role.position > target.top_role.position:
                    await target.ban(reason=reason)

                    embed = Embed(title="Member banned", colour=discord.Colour.red, timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=target.avatar_url)

                    embed.set_footer(
                        icon_url=self.bot.user.avatar_url,
                        text=f"{str(self.bot.user).split('#')[0]}"
                    )

                    fields = [("Member", target.display_name, False),
                              ("Banned by", ctx.author.display_name, False),
                              ("Reason", reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    await self.log_channel.send(embed=embed)
                else:
                    await ctx.send(f"{target.display_name} could not be banned.")

    @ban_members.error
    async def ban_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Nice try, but you need certain permissions for this.")

    @command(name="clear", aliases=["purge"], help="Deletes last 20 messages by default if no number is provided.")
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    @cooldown(1, 5, BucketType.user)
    async def clear_messages(self, ctx, limit: Optional[int] = 20):
        with ctx.channel.typing():
            deleted = await ctx.channel.purge(limit=limit + 1)

            await ctx.send(f"Deleted {len(deleted):,} messages.", delete_after=5)

    @command(name="clearall", aliases=["purgeall"], help="Deletes all messages.")
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    @cooldown(1, 5, BucketType.user)
    async def clear_all_messages(self, ctx):
        await ctx.channel.purge()
        await ctx.send(f"Deleted all messages.", delete_after=5)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(
                969597889850519592)  # TODO : make this available not just for a single server
            self.bot.cogs_ready.ready_up("Mod")


def setup(bot):
    bot.add_cog(Mod(bot))
