# TODO: Modify it so it will work for multiple servers (channel ids, guild ids, user ids)

from discord.ext.commands import Cog
from discord import Forbidden
from discord.ext.commands import command
from discord import Embed
from datetime import datetime

from ..db import db


class Log(Cog):
    def __init__(self, bot):
        self.log_channel = None
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(969597889850519592)
            self.bot.cogs_ready.ready_up("Logs")

    @Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name:
            embed = Embed(title="Member update!", colour=after.color, timestamp=datetime.utcnow(),
                          description=f"**{before.mention}** changed their username.")
            embed.add_field(name="Information",
                            value=f"**{before.name}** has been changed to **{after.name}**")
            embed.set_author(name=f"{after.display_name}",
                             icon_url=before.avatar_url)  # author of the embed
            embed.set_footer(
                icon_url=self.bot.user.avatar_url,
                text=f"{str(self.bot.user).split('#')[0]}"
            )
            await self.log_channel.send(embed=embed)

        if before.avatar_url != after.avatar_url:
            embed = Embed(title="Member update!", colour=after.color, timestamp=datetime.utcnow(),
                          description=f"**{before.mention}** changed their avatar (below image is the new one).")

            embed.set_thumbnail(url=before.avatar_url)
            embed.set_image(url=after.avatar_url)

            embed.set_author(name=f"{before.display_name}",
                             icon_url=after.avatar_url)  # author of the embed
            embed.set_footer(
                icon_url=self.bot.user.avatar_url,
                text=f"{str(self.bot.user).split('#')[0]}"
            )
            await self.log_channel.send(embed=embed)

        if before.discriminator != after.discriminator:
            embed = Embed(title="Member update!", colour=after.color, timestamp=datetime.utcnow(),
                          description=f"**{before.mention}** changed their discriminator.")
            embed.add_field(name="Information",
                            value=f"**{before.discriminator}** has been changed to **{after.discriminator}**")
            embed.set_author(name=f"{before.display_name}",
                             icon_url=before.avatar_url)  # author of the embed
            embed.set_footer(
                icon_url=self.bot.user.avatar_url,
                text=f"{str(self.bot.user).split('#')[0]}"
            )
            await self.log_channel.send(embed=embed)

    @Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick and after.nick:
            embed = Embed(title="Member update!", colour=after.color, timestamp=datetime.utcnow(),
                          description=f"**{before.mention}** changed their nickname.")
            embed.add_field(name="Old nickname",
                            value=f"**{before.nick}**",
                            inline=False)
            embed.add_field(name="New nickname",
                            value=f"**{after.nick}**",
                            inline=False)
            embed.set_author(name=f"{after.display_name}",
                             icon_url=before.avatar_url)  # author of the embed
            embed.set_footer(
                icon_url=self.bot.user.avatar_url,
                text=f"{str(self.bot.user).split('#')[0]}"
            )
            await self.log_channel.send(embed=embed)
        elif len(before.roles) < len(after.roles):
            # TODO - try to do this part more efficient if possible
            result = None
            for i in range(len(before.roles)):
                if before.roles[i] != after.roles[i] and after.roles[i] is not None:
                    result = after.roles[i]
                    continue
                else:
                    result = after.roles[-1]
                    continue
            embed = Embed(title="Member update!", colour=after.color, timestamp=datetime.utcnow(),
                          description=f"**{before.mention}** changed their roles.")
            embed.add_field(name="✅ Roles added",
                            value=result, inline=False)
            embed.set_author(name=f"{before.display_name}",
                             icon_url=before.avatar_url)  # author of the embed
            embed.set_footer(
                icon_url=self.bot.user.avatar_url,
                text=f"{str(self.bot.user).split('#')[0]}"
            )
            await self.log_channel.send(embed=embed)
        elif len(before.roles) > len(after.roles):
            # TODO - try to do this part more efficient if possible
            result = None
            for i in range(len(after.roles)):
                if after.roles[i] != before.roles[i] and before.roles[i] is not None:
                    result = before.roles[i]
                    continue
                else:
                    result = before.roles[-1]
                    continue
            embed = Embed(title="Member update!", colour=after.color, timestamp=datetime.utcnow(),
                          description=f"**{after.mention}** changed their roles.")
            embed.add_field(name="⛔ Roles deleted",
                            value=result, inline=False)
            embed.set_author(name=f"{after.display_name}",
                             icon_url=after.avatar_url)  # author of the embed
            embed.set_footer(
                icon_url=self.bot.user.avatar_url,
                text=f"{str(self.bot.user).split('#')[0]}"
            )
            await self.log_channel.send(embed=embed)

    @Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.author.bot:
            if before.content != after.content:
                embed = Embed(title="Member message update!", colour=after.author.color, timestamp=datetime.utcnow(),
                              description=f"**{before.author.mention}** changed their message in <#{before.channel.id}>.")
                embed.add_field(name="Old message",
                                value=f"{before.content}",
                                inline=False)
                embed.add_field(name="New message",
                                value=f"{after.content}",
                                inline=False)
                embed.set_author(name=f"{before.author.display_name}",
                                 icon_url=before.author.avatar_url)  # author of the embed
                embed.set_footer(
                    icon_url=self.bot.user.avatar_url,
                    text=f"{str(self.bot.user).split('#')[0]}"
                )
                await self.log_channel.send(embed=embed)

    @Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            embed = Embed(title="Member message update!", colour=message.author.color, timestamp=datetime.utcnow(),
                          description=f"**{message.author.mention}** deleted their message.")
            embed.add_field(name="Information",
                            value=f"**{message.content}** has been deleted.")
            embed.set_author(name=f"{message.author.display_name}",
                             icon_url=message.author.avatar_url)  # author of the embed
            embed.set_footer(
                icon_url=self.bot.user.avatar_url,
                text=f"{str(self.bot.user).split('#')[0]}"
            )
            await self.log_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Log(bot))
