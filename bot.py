#########################
# File: bot.py
#
# Author: Dobritoiu David-Constantin (HarakiriGod)
#
# Date: 4/22/2022
#########################

# Beginning of bot

import discord
from discord.ext import commands
import datetime
import asyncio
import random
import json


def get_prefix(client, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]


client = commands.Bot(command_prefix=get_prefix)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    pre = prefixes[str(message.guild.id)]

    # message to tell the users the bot prefix and to welcome.

    if message.content.startswith(f'{pre}hello'):
        await message.channel.send('Hello!')

    await client.process_commands(message)


@client.event
async def on_guild_join(guild):
    # get prefix from json file
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = ">"

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f)

    await guild.channel.send(f"Hello! I am Katheryne. I am a Bot from Teyvat, and I have come to your aid."
                             f"For now, my prefix is '>', but it can always be changed by an admin!")


##################################### CLIENT COMMANDS #######################################
@client.command(help="Changes prefix if given one, otherwise just show current one")
@commands.has_permissions(administrator=True)
async def prefix(ctx, pre=None):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    if pre is not None:
        prefixes[str(ctx.guild.id)] = pre

        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f)

        await ctx.send(f"The prefix was changed to: {pre}")
    else:
        await ctx.send(f"Usage: {pre}prefix new_prefix")


@client.command(help="Clear chat")
@commands.has_permissions(administrator=True)
async def clear(ctx):
    await ctx.channel.purge()


##################################### ECONOMY SYSTEM #######################################

# helper functions
async def open_account(user):
    users = await get_bank_data()

    if str(user.id) in users:
        return False

    users[str(user.id)] = {}
    users[str(user.id)]["primogems"] = 0

    await save_bank_data(users)

    return True


async def get_bank_data():
    with open("primogems.json", "r") as f:
        users = json.load(f)

    return users


async def save_bank_data(users):
    with open("primogems.json", "w") as f:
        json.dump(users, f)


@client.command(help="Find your primogems balance")
async def primos(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author
    primogems = users[str(user.id)]["primogems"]

    await ctx.send(f"<:primogem:967387666054254622>**{user.mention}**, you have **{primogems} primogems**!")


@client.command(help="Test function to earn primos.")
async def primo(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()

    earn = random.randint(0, 1000)

    user = ctx.author
    await ctx.send(f"You earned **{earn}** primogems.")

    users[str(user.id)]["primogems"] += earn

    await save_bank_data(users)


##################################### WISH SYSTEM #######################################

# helper functions
async def open_wish(user):
    users = await get_wish_data()

    if str(user.id) in users:
        return False

    users[str(user.id)] = {}
    users[str(user.id)]["eventBanner"] = 0
    users[str(user.id)]["weaponBanner"] = 0
    users[str(user.id)]["standardBanner"] = 0

    await save_wish_data(users)

    return True


async def get_wish_data():
    with open("wishes.json", "r") as f:
        users = json.load(f)

    return users


async def save_wish_data(users):
    with open("wishes.json", "w") as f:
        json.dump(users, f)


@client.command(help="Tells you how many wishes you have on each banner.")
async def wishes(ctx):
    await open_wish(ctx.author)

    users = await get_wish_data()

    user = ctx.author
    event_banner = users[str(user.id)]["eventBanner"]
    weapon_banner = users[str(user.id)]["weaponBanner"]
    standard_banner = users[str(user.id)]["standardBanner"]

    embed = discord.Embed(title=f"{ctx.author.name}'s wish amount", color=discord.Color.red())
    embed.add_field(name="Event Banner Wishes", value=event_banner)
    embed.add_field(name="Weapon Banner Wishes", value=weapon_banner)
    embed.add_field(name="Standard Banner Wishes", value=standard_banner)
    await ctx.send(embed=embed)

    return True


@client.command(help="Wish on Event Banner!")
async def eventwish(ctx):
    await open_wish(ctx.author)
    await open_account(ctx.author)

    users = await get_wish_data()
    users_balance = await get_bank_data()

    user = ctx.author

    # wish system default game system: you must have at least 160 primogems.
    if users_balance[str(user.id)]["primogems"] >= 160:

        # create first embed, for asking user how many wishes.
        embed = discord.Embed(title=f"{ctx.author.name}, how many wishes do you want to do?",
                              color=discord.Color.blue())
        embed.add_field(name="1x <:intertwined:967406033419006002>", value="160x <:primogem:967387666054254622>")
        embed.add_field(name="10x <:intertwined:967406033419006002>", value="1600x <:primogem:967387666054254622>")

        # add emoji reactions here.
        message = await ctx.send(embed=embed)

        wish = "<:intertwined:967406033419006002>"
        wish10 = "<:intertwined10:967412569696534528>"

        await message.add_reaction("<:intertwined:967406033419006002>")
        await message.add_reaction("<:intertwined10:967412569696534528>")

        def check(react, cur_user):
            return cur_user == ctx.author and str(react.emoji) in [wish, wish10]

        # get the reaction from the user
        reaction, current_user = await client.wait_for("reaction_add", timeout=600.0, check=check)

        # if the reaction is the first emoji
        if str(reaction.emoji) == wish:
            result = random.randint(0, 10)  # TODO: Change this!

            users[str(user.id)]["eventBanner"] += 1
            users_balance[str(user.id)]["primogems"] -= 160

            # create the embed
            embed = discord.Embed(title=f"{ctx.author.name}, here is your reward!", color=discord.Color.blue())
            embed.add_field(name="**You got:**", value=f"{result}")
            await message.edit(embed=embed)

            # remove emojis from embed
            await message.clear_reactions()

        # if the reaction is the 2nd emoji
        elif str(reaction.emoji) == wish10:
            # we check if the balance is bigger than 1600, so we can subtract it after, for 10 wishes
            if users_balance[str(user.id)]["primogems"] >= 1600:
                results = []

                # TODO: Doesn't work.
                for i in range(0, 10):
                    results[i] = random.randint(0, 100)  # TODO: Change this!

                users[str(user.id)]["eventBanner"] += 10
                users_balance[str(user.id)]["primogems"] -= 1600

                # create the embed
                embed = discord.Embed(title=f"{ctx.author.name}, here is your reward!", color=discord.Color.blue())
                for i in range(0, 10):
                    embed.add_field(name="**You got:**", value=f"{results[i]}")
                await message.edit(embed=embed)

                # remove emojis from embed
                await message.clear_reactions()

            else:
                embed = discord.Embed(title=f"{ctx.author.name}, you do not have enough primogems!",
                                      color=discord.Color.blue())
                await message.edit(embed=embed)
    else:
        embed = discord.Embed(title=f"{ctx.author.name}, you do not have enough primogems!", color=discord.Color.blue())
        await ctx.send(embed=embed)
        return False

    await save_wish_data(users)
    await save_bank_data(users_balance)

    return True


##################################### WEAPON SYSTEM #######################################
# helper functions
async def open_weapons(user):
    users = await get_weapon_data()

    if str(user.id) in users:
        return False

    users[str(user.id)] = {}
    users[str(user.id)]["Swords"] = {}
    users[str(user.id)]["Claymores"] = {}
    users[str(user.id)]["Catalysts"] = {}
    users[str(user.id)]["Polearms"] = {}
    users[str(user.id)]["Bows"] = {}

    await save_weapon_data(users)

    return True


async def get_weapon_data():
    with open("weapons.json", "r") as f:
        users = json.load(f)

    return users


async def save_weapon_data(users):
    with open("weapon.json", "w") as f:
        json.dump(users, f)


@client.command(help="Tester function for swords.")
async def add_sword(ctx, sword):
    weapons = get_weapon_data()


client.run('OTY3MTA4OTM5NTc5NzkzNDU4.YmLgYw.QKqZP37Ujjub7kiwwVWS5Ep4ieA')
