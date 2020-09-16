from discord.ext import commands
import random

PERCENT_MAX = 100_00


class Gamble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # commands:
    # @commands.command        instead of @bot.command()
    # @commands.Cog.listener() instead of @bot.event()

    @commands.command(name='coinrain', hidden=True)
    @commands.has_role('admin')
    async def coinrain(self, ctx, amount: int = 0):
        if ctx.message.mentions:
            for user in ctx.message.mentions:
                self.bot.sql_execute(
                    "UPDATE %s SET coins = coins + %d WHERE id = %d" % (ctx.guild.name, amount, user.id)
                )
        else:
            for user in ctx.guild.members:
                self.bot.sql_execute(
                    "UPDATE %s SET coins = coins + %d WHERE id = %d" % (ctx.guild.name, amount, user.id)
                )

        await ctx.send("it rained %d coins into someones bank" % amount)

    @commands.command(name='gamble', help='gamble some coins in form of "gamble [coins]"')
    async def gamble(self, ctx, commit_coins: int = 0):
        if commit_coins <= 0:
            await ctx.send(f'Not a valid coin number')
            return

        sql_result = self.bot.sql_fetchmany(
            "SELECT coins FROM %s WHERE id = %d" % (ctx.guild.name, ctx.message.author.id), 1
            )

        member_coins = sql_result[0]

        if member_coins < commit_coins:
            await ctx.send("Not enough coins")
            return

        # EV = 0,795 https://rechneronline.de/durchschnitt/erwartungswert.php
        # win_factor       lose , 1    , 2    , 3   , 4   , 5   , 10
        win_percentages = [50_00, 25_00, 10_00, 5_00, 2_00, 1_00, 10]
        win_factor = 0
        rand_result = random.randint(0, PERCENT_MAX)
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

        self.bot.sql_execute(
            "UPDATE %s SET coins = %d WHERE id = %d" % (ctx.guild.name, member_coins, ctx.message.author.id)
        )

        if won_coins <= 0:
            await ctx.send("More luck next time!")
            return
        else:
            await ctx.send(f"You won %d coins!" % won_coins)
            return

    @commands.command(name='roll', help='WIP')
    async def roll(self, ctx):
        # TODO buildup the resulting message
        # TODO build a roll game
        response = random.randrange(0, 100)
        await ctx.send(response)

    @commands.command(name='coins', help='Get your coins')
    async def coins(self, ctx):
        sql_result = self.bot.sql_execute(
            "SELECT coins FROM %s WHERE id = %d" % (ctx.guild.name, ctx.message.author.id),
            1
        )

        await ctx.send(f"You got %d coins" % sql_result[0])

    @commands.command(name='top', help='get the top X banks with "top [X]"')
    async def top(self, ctx, rank: int = 10):
        if rank <= 0 or rank > ctx.guild.member_count:
            return

        sql_result = self.bot.sql_fetchall(
            "SELECT user_name, coins FROM %s ORDER BY coins DESC LIMIT %d" % (ctx.guild.name, rank)
        )
        send = ""

        i = 1
        for row in sql_result:
            send += str(i) + ". " + row[0] + " with " + str(row[1]) + "\n"
            i += 1

        await ctx.send(send)


def setup(bot):
    bot.add_cog(Gamble(bot))
