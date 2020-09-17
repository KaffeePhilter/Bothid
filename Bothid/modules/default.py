from discord.ext import commands


class Default(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have permission to use this command')
        else:
            print(error)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        # create new guild member table
        self.bot.sql_cursor.execute(
            f'CREATE TABLE IF NOT EXISTS {guild.id}(id BIGINT UNSIGNED UNIQUE, user_name VARCHAR(64), coins INTEGER UNSIGNED);')
        # insert new guild to guilds table
        self.bot.sql_cursor.execute(f'INSERT INTO guilds VALUES({guild.id}, {guild.name});')

        # add all users in this guild to its table
        for member in guild.members:
            self.bot.sql_cursor.execute(f'INSERT INTO {guild.id} VALUES({member.id}, {member.name}, 50);')

    @commands.command(name='dbrefresh', hidden=True)
    @commands.has_role('admin')
    async def dbrefresh(self, ctx):
        await self.on_guild_join(ctx.guild)
        await ctx.send("database refreshed")


def setup(bot):
    bot.add_cog(Default(bot))
