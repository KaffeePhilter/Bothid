# bothid.py
# GENERAL
import os
import random
import logging
from datetime import datetime

# PRIVATE
from utils import config_loader

# DISCORD
# from discord import *
from discord.ext import commands

# SQL
import mysql.connector as sql

from dotenv import load_dotenv

load_dotenv()


class Bothid(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sql_db = self.connect_db()
        self.sql_cursor = self.sql_db.cursor()
        self.sql_db_init()
        self.load_modules()
        self.log = self.create_logger(f'LOG_{datetime.now().date()}')

    # HOW TO SQL COMMAND WITH MySQL.Connector EXAMPLE
    # sql_command = """I'm a SQL Query just like any other;"""
    # cursor.execute(sql_command)
    # SAVE CHANGES:
    # connect.commit()
    # AND CLOSE WITH
    # connect.close()
    # SOURCE https://www.geeksforgeeks.org/sql-using-python/

    @staticmethod
    def connect_db():
        return sql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PWD'),
            database=os.getenv('DB_NAME')
        )

    def sql_db_init(self):
        self.sql_execute(
            f'CREATE TABLE IF NOT EXISTS guilds (id INTEGER PRIMARY KEY UNIQUE, name VARCHAR(255) NOT NULL );'
        )

    def sql_execute(self, query: str):
        self.sql_cursor.execute(query)
        self.log.debug(f'SQL Query executed: {query}')
        self.sql_db.commit()

    def sql_fetchall(self, query: str):
        self.sql_cursor.execute(query)
        return self.sql_cursor.fetchall()

    def sql_fetchmany(self, query: str, rows: int):
        self.sql_cursor.execute(query)
        if rows == 1:
            return self.sql_cursor.fetchone()
        elif rows > 1:
            return self.sql_cursor.fetchmany(rows)

    def load_modules(self):
        for name in config_loader.load_conf("config"):
            try:
                self.load_extension(f'modules.{name}')
            except commands.ExtensionNotFound:
                print(f"could not load {name}")

    @staticmethod
    def create_logger(file: str):
        logger = logging.getLogger(file)
        logger.setLevel(logging.DEBUG)
        path = f"logs/{file}.log"
        handler = logging.FileHandler(filename=path, encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(handler)
        return logger

# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.errors.CheckFailure):
#         await ctx.send('You do not have permission to use this command')
#
#
# @bot.event
# async def on_guild_join(guild):
#
#     # create new guild member table
#     bot.sql_cursor.execute("CREATE TABLE IF NOT EXISTS %s (id BIGINT UNSIGNED UNIQUE, user_name VARCHAR(64), coins INTEGER UNSIGNED);" % guild.name)
#     # insert new guild to guilds table
#     bot.sql_cursor.execute("INSERT INTO guilds VALUES(%d, %s);" % (guild.id, guild.name))
#
#     # add all users in this guild to its table
#     for member in guild.members:
#         bot.sql_cursor.execute("INSERT INTO %s VALUES(%d, %s, 50);" % (guild.name, member.id, member.name))
#
#     bot.sql_db.commit()
#
#
# @bot.command(name='dbrefresh', hidden=True)
# @commands.has_role('admin')
# async def dbrefresh(ctx):
#     guild = ctx.guild
#
#     # create new guild member table
#     bot.sql_cursor.execute("CREATE TABLE IF NOT EXISTS %s (id BIGINT UNSIGNED UNIQUE, user_name VARCHAR(64), coins INT UNSIGNED);" % guild.name)
#     # add all users in this guild to its table
#     for _member in guild.members:
#         bot.sql_cursor.execute("INSERT INTO %s VALUES(%d, '%s', 50);" % (guild.name, _member.id, _member.name))
#         bot.sql_db.commit()
#
#     await ctx.send("database refreshed")
#
#
# @bot.command(name='coinrain', hidden=True)
# @commands.has_role('admin')
# async def coinrain(ctx, amount: int = 0):
#     if ctx.message.mentions:
#         for user in ctx.message.mentions:
#             sql_cursor.execute("UPDATE %s SET coins = coins + %d WHERE id = %d" % (ctx.guild.name, amount, user.id))
#             sql_db.commit()
#     else:
#         for user in ctx.guild.members:
#             sql_cursor.execute("UPDATE %s SET coins = coins + %d WHERE id = %d" % (ctx.guild.name, amount, user.id))
#             sql_db.commit()
#
#     await ctx.send("it rained %d coins into someones bank" % amount)
#
#
# @bot.command(name='gamble', help='gamble some coins in form of "gamble [coins]"')
# async def gamble(ctx, commit_coins: int = 0):
#     if commit_coins <= 0:
#         await ctx.send(f'Not a valid coin number')
#         return
#
#     sql_cursor.execute("SELECT coins FROM %s WHERE id = %d" % (ctx.guild.name, ctx.message.author.id))
#     sql_result = sql_cursor.fetchone()
#
#     member_coins = sql_result[0]
#
#     if member_coins < commit_coins:
#         await ctx.send("Not enough coins")
#         return
#
#     # EV = 0,795 https://rechneronline.de/durchschnitt/erwartungswert.php
#     # win_factor        lose , 1    , 2    , 3   , 4   , 5   , 10
#     win_percentages = [50_00, 25_00, 10_00, 5_00, 2_00, 1_00, 10]
#     win_factor = 0
#     rand_result = random.randrange(0, PERCENT_MAX)
#     if rand_result > PERCENT_MAX - win_percentages[0]:
#         win_factor = 0
#     elif rand_result > PERCENT_MAX - win_percentages[1]:
#         win_factor = 1
#     elif rand_result > PERCENT_MAX - win_percentages[2]:
#         win_factor = 2
#     elif rand_result <= PERCENT_MAX - win_percentages[3]:
#         win_factor = 3
#     elif rand_result <= PERCENT_MAX - win_percentages[4]:
#         win_factor = 4
#     elif rand_result <= PERCENT_MAX - win_percentages[4]:
#         win_factor = 5
#     elif rand_result <= PERCENT_MAX - win_percentages[5]:
#         win_factor = 10
#
#     won_coins = (win_factor * commit_coins) - commit_coins
#     member_coins += won_coins
#     sql_cursor.execute("UPDATE %s SET coins = %d WHERE id = %d" % (ctx.guild.name, member_coins, ctx.message.author.id))
#     sql_db.commit()
#
#     if won_coins <= 0:
#         await ctx.send("More luck next time!")
#         return
#     else:
#         await ctx.send(f"You won %d coins!" % won_coins)
#         return
#
#
# @bot.command(name='roll', help='WIP')
# async def roll(ctx):
#     # TODO buildup the resulting message
#     # TODO build a roll game
#     response = random.randrange(0, 100)
#     await ctx.send(response)
#
#
# @bot.command(name='coins', help='Get your coins')
# async def coins(ctx):
#     sql_cursor.execute("SELECT coins FROM %s WHERE id = %d" % (ctx.guild.name, ctx.message.author.id))
#     sql_result = sql_cursor.fetchone()
#     await ctx.send(f"You got %d coins" % sql_result[0])
#
#
# @bot.command(name='top', help='get the top X banks with "top [X]"')
# async def top(ctx, rank:int = 10):
#     if rank <= 0 or rank > ctx.guild.member_count:
#         return
#
#     sql_cursor.execute("SELECT user_name, coins FROM %s ORDER BY coins DESC LIMIT %d" % (ctx.guild.name, rank))
#     send = ""
#     sql_result = sql_cursor.fetchall()
#     i = 1
#     for row in sql_result:
#         send += str(i) + ". " + row[0] + " with " + str(row[1]) + "\n"
#         i += 1
#
#     await ctx.send(send)

# modules list something something module list grab from file


bot = Bothid(command_prefix='!')

bot.run(os.getenv('DISCORD_TOKEN'))
