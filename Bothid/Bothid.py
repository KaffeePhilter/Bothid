# bothid.py
import os
import random
import discord
from discord import User
from discord.ext import commands
import sqlite3 as sql

from dotenv import load_dotenv

# Global Variables or Constants
PERCENT_MAX = 100_00
NO_PERMISSION_MSG = "you're not authorized to do this"

# Environment setup
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DB_ADDRESS = os.getenv('DB_TEST')

bot = commands.Bot(command_prefix='!')


# SQL DB
sql_connect = sql.connect('database/bothid.db')
sql_cursor = sql_connect.cursor()

# HOW TO SQL COMMAND WITH SQLITE EXAMPLE
# sql_command = """I'm a SQL Query just like any other;"""
# cursor.execute(sql_command)
# SAVE CHANGES:
# connect.commit()
# AND CLOSE WITH
# connect.close()
# SOURCE https://www.geeksforgeeks.org/sql-using-python/


# IDEA: LEVEL for betting or gambling: e.g.
#
#

# INITIAL SQL DATABASE SETUP
sql_cursor.execute("CREATE TABLE IF NOT EXISTS guilds (id INTEGER PRIMARY KEY, name STRING NOT NULL, UNIQUE(id));")
sql_connect.commit()


@bot.event
async def on_guild_join(guild):

    # create new guild member table
    sql_cursor.execute("CREATE TABLE IF NOT EXISTS \"%s\" (id INTEGER UNIQUE, user_name STRING, coins INTEGER);" % guild.name)
    # insert new guild to guilds table
    sql_cursor.execute("INSERT INTO guilds VALUES(?, \"%s\");" % (guild.id, guild.name))

    # add all users in this guild to its table
    for member in guild.members:
        sql_cursor.execute("INSERT INTO \"%s\" VALUES(%d, \"%s\", 50);" % (guild.name, member.id, member.name))

    sql_connect.commit()


@bot.command(name='dbrefresh', hidden=True)
async def dbrefresh(ctx):
    if not ctx.message.author.guild_permissions.administrator:
        ctx.send(NO_PERMISSION_MSG)
        return

    guild = ctx.guild

    # create new guild member table
    sql_cursor.execute("CREATE TABLE IF NOT EXISTS \"%s\" (id INTEGER UNIQUE, user_name STRING, coins INTEGER);" % guild.name)
    # add all users in this guild to its table
    for member in guild.members:
        sql_cursor.execute("INSERT INTO \"%s\" VALUES(%d, \"%s\", 50);" % (str(guild.name), int(member.id), str(member.name)))

    sql_connect.commit()

    await ctx.send("database refreshed")


@bot.command(name='coinrain', hidden=True)
async def coinrain(ctx, amount: int = 0):
    if not ctx.message.author.guild_permissions.administrator:
        ctx.send(NO_PERMISSION_MSG)
        return
    if amount <= 0:
        await ctx.send("no valid amount")
        return
    if ctx.message.mentions:
        for user in ctx.message.mentions:
            sql_cursor.execute("UPDATE \"%s\" SET coins = coins + %d WHERE id = %d" % (ctx.guild.name, amount, user.id))
            sql_connect.commit()
    else:
        for user in ctx.guild.members:
            sql_cursor.execute("UPDATE \"%s\" SET coins = coins + %d WHERE id = %d" % (ctx.guild.name, amount, user.id))
            sql_connect.commit()

    await ctx.send("it rained %d coins into someones bank" % amount)


@bot.command(name='gamble')
async def gamble(ctx, commit_coins: int = 0):
    if commit_coins <= 0:
        await ctx.send(f'Not a valid coin number')
        return

    sql_cursor.execute("SELECT coins FROM \"%s\" WHERE id = %d" % (ctx.guild.name, ctx.message.author.id))
    sql_result = sql_cursor.fetchone()

    member_coins = sql_result[0]

    if member_coins < commit_coins:
        await ctx.send("Not enough coins")
        return

    # EV = 0,795 https://rechneronline.de/durchschnitt/erwartungswert.php
    # win_factor        lose , 1    , 2    , 3   , 4   , 5   , 10
    win_percentages = [50_00, 25_00, 10_00, 5_00, 2_00, 1_00, 10]
    win_factor = 0
    rand_result = random.randrange(0, PERCENT_MAX)
    if rand_result > PERCENT_MAX - win_percentages[0]:
        win_factor = 0
    elif rand_result > PERCENT_MAX - win_percentages[1]:
        win_factor = 1
    elif rand_result > PERCENT_MAX - win_percentages[2]:
        win_factor = 2
    elif rand_result <= PERCENT_MAX - win_percentages[3]:
        win_factor = 3
    elif rand_result <= PERCENT_MAX - win_percentages[4]:
        win_factor = 4
    elif rand_result <= PERCENT_MAX - win_percentages[4]:
        win_factor = 5
    elif rand_result <= PERCENT_MAX - win_percentages[5]:
        win_factor = 10

    won_coins = (win_factor * commit_coins) - commit_coins
    member_coins += won_coins
    sql_cursor.execute("UPDATE \"%s\" SET coins = %d WHERE id = %d" % (ctx.guild.name, member_coins, ctx.message.author.id))
    sql_connect.commit()

    if won_coins <= 0:
        await ctx.send("More luck next time!")
        return
    else:
        await ctx.send(f"You won %d coins!" % won_coins)
        return


@bot.command(name='roll')
async def roll(ctx):
    # TODO buildup the resulting message
    # TODO build a roll game
    response = random.randrange(0, 100)
    await ctx.send(response)


@bot.command(name='coins')
async def coins(ctx):
    sql_cursor.execute("SELECT coins FROM \"%s\" WHERE id = %d" % (ctx.guild.name, ctx.message.author.id))
    sql_result = sql_cursor.fetchone()
    await ctx.send(f"You got %d coins" % sql_result[0])


@bot.command(name='testcmd')
async def testcmd(ctx, arg1: int, arg2):
    await ctx.send(f'testcmd :: \n arg1 int: {arg1}, \n arg2: { arg2 }')


bot.run(TOKEN)
