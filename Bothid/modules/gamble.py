from discord.ext import commands
import random
import asyncio
from datetime import datetime

PERCENT_MAX = 100_00


class Gamble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.__daily_coin_rain())

    # commands:
    # @commands.command        instead of @bot.command()
    # @commands.Cog.listener() instead of @bot.event()

    async def add_user_to_db(self, user, guild, coins):
        self.bot.log.debug(
            f'{user.name}:{user.id} was not found in {guild.name}:{guild.id} database. Adding now with {coins} coins')
        await self.bot.sql_execute(
            f'INSERT INTO `{guild.id}` VALUES({user.id}, "{user.name}", {coins}, 0) ON DUPLICATE KEY UPDATE user_name = "{user.name}";')

    async def __daily_coin_rain(self):
        await self.bot.wait_until_ready()
        self.bot.log.debug(f'TASK "daily coin rain": started Task')
        while not self.bot.is_closed():
            sec = self.bot.time_to_next_day() + 300
            self.bot.log.debug(f'TASK "daily coin rain": sleeping until next day: {sec}sec')
            await asyncio.sleep(sec)
            self.bot.log.info(f'Issuing coinrain for all servers...')
            for guild in self.bot.guilds:
                amount = random.randint(50, 1000)
                for user in guild.members:
                    await self.bot.sql_execute(f'UPDATE `{guild.id}` SET coins = coins + {amount} WHERE id = {user.id}')
                self.bot.log.info(f'Daily coinrain for Guild {guild.name}:{guild.id} with {amount} coins')
            self.bot.log.info(f'Daily Coinrain finished')

    @commands.command(name='coinrain', hidden=True)
    @commands.has_permissions(administrator=True)
    async def coinrain(self, ctx, amount: int = 0):
        who = ""
        if ctx.message.mentions:
            if len(ctx.message.mentions) > 1:
                for user in ctx.message.mentions:
                    await self.bot.sql_execute(
                        f'UPDATE `{ctx.guild.id}` SET coins = coins + {amount} WHERE id = {user.id}')
                    who += f'{user.name}, '
            else:
                user = ctx.message.mentions[0]
                await self.bot.sql_execute(f'UPDATE `{ctx.guild.id}` SET coins = coins + {amount} WHERE id = {user.id}')
                who = f'{user.name}'

        else:
            for user in ctx.guild.members:
                await self.bot.sql_execute(f'UPDATE `{ctx.guild.id}` SET coins = coins + {amount} WHERE id = {user.id}')
            who = "the whole server"

        self.bot.log.info(
            f'{ctx.author.name}:{ctx.author.id} issued coinrain on {ctx.guild.name}:{ctx.guild.id} for {who}')
        await ctx.send(f'it rained {amount} coins on {who}')

    @commands.command(name='gamble', help='gamble some coins in form of "gamble [coins]"')
    async def gamble(self, ctx, commit_coins: int = 0):
        if commit_coins <= 0:
            await ctx.send(f'{commit_coins} is not a valid coin number')
            return

        sql_result = await self.bot.sql_fetchmany(f'SELECT coins FROM `{ctx.guild.id}` WHERE id = {ctx.author.id}', 1)

        if sql_result is None:
            await self.add_user_to_db(ctx.author, ctx.guild, commit_coins % 51)
            ctx.send(f'Oh I could not find you. Giving you {commit_coins % 51} coins. Have fun! :)')
            return

        member_coins = sql_result[0]

        if member_coins < commit_coins:
            await ctx.send("Not enough coins")
            return

        # EV = 0,795 https://rechneronline.de/durchschnitt/erwartungswert.php
        # win_factor       lose, 1   , 2   , 5  , 10 , 25, 100
        win_percentages = [5000, 2500, 1000, 500, 100, 10, 1]
        win_factor = 0
        rand_result = random.randint(0, 10000)
        if rand_result < win_percentages[6]:
            win_factor = 100
        elif rand_result < win_percentages[5]:
            win_factor = 25
        elif rand_result < win_percentages[4]:
            win_factor = 10
        elif rand_result < win_percentages[3]:
            win_factor = 5
        elif rand_result < win_percentages[2]:
            win_factor = 3
        elif rand_result < win_percentages[1]:
            win_factor = 2
        elif rand_result < win_percentages[0]:
            win_factor = 1

        won_coins = (win_factor * commit_coins) - commit_coins
        member_coins += won_coins

        await self.bot.sql_execute(f'UPDATE `{ctx.guild.id}` SET coins = {member_coins} WHERE id = {ctx.author.id}')

        if won_coins <= 0:
            await ctx.send("More luck next time!")
            return
        else:
            await ctx.send(f'You won {won_coins} coins!')
            return

    @commands.command(name='roll', help='WIP')
    async def roll(self, ctx):
        # TODO buildup the resulting message
        # TODO build a roll game
        response = random.randrange(0, 100)
        await ctx.send(response)

    @commands.command(name='coins', help='Get your coins')
    async def coins(self, ctx):
        sql_result = await self.bot.sql_fetchmany(
            f'SELECT coins FROM `{ctx.guild.id}` WHERE id = {ctx.author.id}', 1)

        if sql_result is None:
            await self.add_user_to_db(ctx.author, ctx.guild, 50)
            ctx.send(f'Oh I could not find you. Giving you {50} coins. Have fun! :)')
            return

        await ctx.send(f'You got {sql_result[0]} coins')

    @commands.command(name='top', help='get the top X banks with "top [X]"')
    async def top(self, ctx, rank: int = 10):
        if rank <= 0 or rank > ctx.guild.member_count:
            return

        send = ""
        sql_result = await self.bot.sql_fetchall(
            f'SELECT user_name, coins FROM `{ctx.guild.id}` ORDER BY coins DESC LIMIT {rank}')

        for i, row in enumerate(sql_result, 1):
            send += f'{i}. {row[0]} with {row[1]} coins\n'

        await ctx.send(send)


def setup(bot):
    bot.add_cog(Gamble(bot))
