# TODO: Modify it so it will work for multiple servers (channel ids, guild ids, user ids)

from discord.ext.commands import Cog

from ..db import db


class Welcome(Cog):
    def __init__(self, bot):
        self.welcome_channel = None
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.welcome_channel = self.bot.get_channel(968165135191531540)
            self.bot.cogs_ready.ready_up("Welcome")

    @Cog.listener()
    async def on_member_join(self, member):
        db.execute("INSERT INTO users (UserID) VALUES (?)", member.id)
        # await self.bot.get_context(member.guild.channel)
        await self.welcome_channel.send(
            f"Welcome to **{member.guild.name}**, {member.mention}! Head over to <#967099551569805455> to say hi")

        # await member.edit(roles=[*member.roles, *[member.guild.get_role(id_) for id_ in(role_id1, role_id2)])

    @Cog.listener()
    async def on_member_leave(self, member):
        db.execute("DELETE FROM users WHERE UserID = ?", member.id)
        await self.welcome_channel.send(f"Member {member.display_name} has left the server.")


def setup(bot):
    bot.add_cog(Welcome(bot))
