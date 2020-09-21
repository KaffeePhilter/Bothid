from discord.ext import commands
import random
import asyncio
from datetime import datetime

PERCENT_MAX = 100_00


class Gamble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # BUGGED self.bot.loop.create_task(self.__daily_coin_rain())

    # commands:
    # @commands.command        instead of @bot.command()
    # @commands.Cog.listener() instead of @bot.event()

    # TODO: find the bug in here, suspended until further investigation
    async def __daily_coin_rain(self):
        """
        Task for daily coins for all servers, so that all people can play
        """

        # LOG:
        # Task exception was never retrieved
        # future: <Task finished name='Task-1' coro=<Gamble.__daily_coin_rain() done, defined at /home/bothid/Bothid/Bothid/modules/gamble.py:18> exception=AttributeError("module 'asyncio.streams' has no attribute 'IncompleteReadError'")>
        # Traceback (most recent call last):
        #   File "/usr/local/lib/python3.8/site-packages/aiomysql/connection.py", line 598, in _read_bytes
        #     data = await self._reader.readexactly(num_bytes)
        #   File "/usr/lib64/python3.8/asyncio/streams.py", line 729, in readexactly
        #     raise self._exception
        #   File "/usr/lib64/python3.8/asyncio/selector_events.py", line 836, in _read_ready__data_received
        #     data = self._sock.recv(self.max_size)
        # ConnectionResetError: [Errno 104] Connection reset by peer
        #
        # During handling of the above exception, another exception occurred:
        #
        # Traceback (most recent call last):
        #   File "/home/bothid/Bothid/Bothid/modules/gamble.py", line 33, in __daily_coin_rain
        #     await self.bot.sql_helper.update_coins(guild, user, amount)
        #   File "/home/bothid/Bothid/Bothid/utils/sql_helper.py", line 66, in update_coins
        #     await self.execute(f'UPDATE `{guild.id}` SET coins = coins + {add_val} WHERE id = {user.id}')
        #   File "/home/bothid/Bothid/Bothid/utils/sql_helper.py", line 94, in execute
        #     await self.sql_cursor.execute(query)
        #   File "/usr/local/lib/python3.8/site-packages/aiomysql/cursors.py", line 239, in execute
        #     await self._query(query)
        #   File "/usr/local/lib/python3.8/site-packages/aiomysql/cursors.py", line 457, in _query
        #     await conn.query(q)
        #   File "/usr/local/lib/python3.8/site-packages/aiomysql/connection.py", line 428, in query
        #     await self._read_query_result(unbuffered=unbuffered)
        #   File "/usr/local/lib/python3.8/site-packages/aiomysql/connection.py", line 622, in _read_query_result
        #     await result.read()
        #   File "/usr/local/lib/python3.8/site-packages/aiomysql/connection.py", line 1105, in read
        #     first_packet = await self.connection._read_packet()
        #   File "/usr/local/lib/python3.8/site-packages/aiomysql/connection.py", line 561, in _read_packet
        #     packet_header = await self._read_bytes(4)
        #   File "/usr/local/lib/python3.8/site-packages/aiomysql/connection.py", line 599, in _read_bytes
        #     except asyncio.streams.IncompleteReadError as e:
        # AttributeError: module 'asyncio.streams' has no attribute 'IncompleteReadError'
        # Command raised an exception: AttributeError: 'NoneType' object has no attribute 'id'
        # Command raised an exception: AttributeError: module 'asyncio.streams' has no attribute 'IncompleteReadError'

        await self.bot.wait_until_ready()
        self.bot.log.debug(f'TASK "daily coin rain": started Task')
        while not self.bot.is_closed():
            sec = self.bot.time_to_next_day() + 5
            self.bot.log.debug(f'TASK "daily coin rain": sleeping until next day: {sec}sec')
            await asyncio.sleep(sec)
            self.bot.log.info(f'Issuing coinrain for all servers...')
            for guild in self.bot.guilds:
                amount = random.randint(50, 1000)
                # TODO server messages
                for user in guild.members:
                    await self.bot.sql_helper.update_coins(guild, user, amount)
                self.bot.log.info(f'Daily coinrain for Guild {guild.name}:{guild.id} with {amount} coins')
            self.bot.log.info(f'Daily Coinrain finished')

    @commands.command(name='coinrain', hidden=True)
    @commands.has_permissions(administrator=True)
    async def coinrain(self, ctx, amount: int = 0):
        who = ""
        if ctx.message.mentions:
            if len(ctx.message.mentions) > 1:
                for user in ctx.message.mentions:
                    await self.bot.sql_helper.update_coins(ctx.guild, user, amount)
                    who += f'{user.name}, '
            else:
                user = ctx.message.mentions[0]
                await self.bot.sql_helper.update_coins(ctx.guild, ctx.author, amount)
                who = f'{user.name}'

        else:
            for user in ctx.guild.members:
                await self.bot.sql_helper.update_coins(ctx.guild, user, amount)
            who = "the whole server"

        self.bot.log.info(
            f'{ctx.author.name}:{ctx.author.id} issued coinrain on {ctx.guild.name}:{ctx.guild.id} for {who}')
        await ctx.send(f'it rained {amount} coins on {who}')

    @commands.command(name='gamble', help='gamble some coins in form of "gamble [coins]"')
    async def gamble(self, ctx, bet: int = 0):
        """
        lets a user gamble with some coins
        :param ctx: message.context object
        :param bet: number of coins
        :return: nothing
        """
        if bet <= 0:
            await ctx.send(f'{bet} is not a valid coin number')
            return

        member_coins = await self.bot.sql_helper.get_coins(ctx)

        if member_coins < bet:
            await ctx.send("Not enough coins")
            return

        # EV = 1,25 https://rechneronline.de/durchschnitt/erwartungswert.php
        win_factor = 0
        rand_result = random.randint(0, 10000)

        # 5500 for 0
        if rand_result <= 1:
            win_factor = 100
        elif rand_result <= 24:
            win_factor = 25
        elif rand_result <= 125:
            win_factor = 10
        elif rand_result <= 250:
            win_factor = 5
        elif rand_result <= 1100:
            win_factor = 3
        elif rand_result <= 3000:
            win_factor = 2

        won_coins = (win_factor * bet) - bet
        member_coins += won_coins

        await self.bot.sql_helper.update_coins(ctx.guild, ctx.author, won_coins)

        if won_coins <= 0:
            await ctx.send("More luck next time!")
            return
        else:
            await ctx.send(f'You won {won_coins} coins!')
            return

    @commands.command(name='roll', help='Bet on a number')
    async def roll(self, ctx, bet_number: int):

        # TODO build a roll game
        response = random.randrange(0, 100)
        await ctx.send(response)

    @commands.command(name='coinflip', help='bet on a coinflip. !coinflip <heads | tails> <bet coins>')
    async def coinflip(self, ctx, side, bet: int):
        flip_res = random.choice(('heads', 'tails'))
        if side != ('heads' or 'tails') or bet <= 0:
            await ctx.send(f'no valid bet')

        member_coins = await self.bot.sql_helper.get_coins(ctx)

        if member_coins < bet:
            await ctx.send("Not enough coins")
            return

        if flip_res == side:
            self.bot.sql_helper.update_coins()
            msg = f'{flip_res}! You won {bet * 2} coins!'
        else:
            msg = f'{flip_res}! You lost.. choose better next time!'

        await ctx.send(msg)

    @commands.command(name='coins', help='Get your coins')
    async def coins(self, ctx):
        coins = await self.bot.sql_helper.get_coins(ctx)
        await ctx.send(f'You got {coins} coins')

    @commands.command(name='top', help='get the top X banks with "top [X]"')
    async def top(self, ctx, rank: int = 10):
        if rank <= 0 or rank > ctx.guild.member_count:
            return

        send = ""
        sql_result = await self.bot.sql_helper.fetchall(
            f'SELECT user_name, coins FROM `{ctx.guild.id}` ORDER BY coins DESC LIMIT {rank}')

        for i, row in enumerate(sql_result, 1):
            send += f'{i}. {row[0]} with {row[1]} coins\n'

        await ctx.send(send)


def setup(bot):
    bot.add_cog(Gamble(bot))
