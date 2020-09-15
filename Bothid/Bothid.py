# bothid.py
import os
import random
import discord
from discord.ext import commands

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, MetaData, Table

from dotenv import load_dotenv

# Global Variables or Constants
PERCENT_MAX = 100_00

# Environment setup
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DB_ADDRESS = os.getenv('DB_TEST')

bot = commands.Bot(command_prefix='!')


# SQL DB
DBEngine = create_engine(DB_ADDRESS)
Base = declarative_base()
meta = MetaData()


# User Table
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (self.name, self.fullname, self.nickname)


# Guilds Table
class Guilds(Base):
    __tablename__ = 'guilds'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_count = Column(Integer)

    def __repr__(self):
        return "<User(name='%s', users='%d')>" % (self.name, self.user_count)


# Bot events


@bot.event
async def on_guild_join(guild):

    guild_table = Table(str(guild), meta,
                        Column('user_id', Integer, primary_key=True),
                        Column('user_name', String),
                        Column('coins', Integer)
                        )
    meta.create_all(DBEngine)

    class Guild(Base):
        def __init__(self, user_name, coins):
            self.user_name = user_name
            self.coins = coins

        def __repr__(self):
            return "<User('%s', '%d')>" % (self.user_name, self.coins)


@bot.command(name='roll')
async def roll(ctx):
    # TODO buildup the resulting message
    # TODO build a roll game
    response = random.randrange(0, 100)
    await ctx.send(response)


@bot.command(name='gamble')
async def gamble(ctx, commit_coins: int = 0):
    if commit_coins == 0:
        await ctx.send(f'Not a valid coin number')
        return
    else:

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


@bot.command(name='testcmd')
async def testcmd(ctx, arg1: int, arg2):
    await ctx.send(f'testcmd :: \n arg1 int: {arg1}, \n arg2: { arg2 }')


bot.run(TOKEN)
