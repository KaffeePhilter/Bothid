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
            "CREATE TABLE IF NOT EXISTS %s (id BIGINT UNSIGNED UNIQUE, user_name VARCHAR(64), coins INTEGER UNSIGNED);" % guild.name)
        # insert new guild to guilds table
        self.bot.sql_cursor.execute("INSERT INTO guilds VALUES(%d, %s);" % (guild.id, guild.name))

        # add all users in this guild to its table
        for member in guild.members:
            self.bot.sql_cursor.execute("INSERT INTO %s VALUES(%d, %s, 50);" % (guild.name, member.id, member.name))

    @commands.command(name='dbrefresh', hidden=True)
    @commands.has_role('admin')
    async def dbrefresh(self, ctx):
        guild = ctx.guild

        # create new guild member table
        self.bot.sql_cursor.execute(
            "CREATE TABLE IF NOT EXISTS %s (id BIGINT UNSIGNED UNIQUE, user_name VARCHAR(64), coins INT UNSIGNED);" % guild.name)
        # add all users in this guild to its table
        for _member in guild.members:
            self.bot.sql_cursor.execute("INSERT INTO %s VALUES(%d, '%s', 50);" % (guild.name, _member.id, _member.name))

        await ctx.send("database refreshed")

def setup(bot):
    bot.add_cog(Default(bot))