import discord
from discord.ext import commands


class Default(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.CheckFailure):
            self.bot.log.warn(
                f'{ctx.author.name}:{ctx.author.id} on {ctx.guild.name}:{ctx.guild.id} tried to use: "{ctx.message.content}"')
            await ctx.send('You do not have permission to use this command')
        else:
            print(error)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.sql_helper.new_guild(guild)
        # add all users in this guild to its table
        for member in guild.members:
            await self.bot.sql_helper.new_member(guild, member)

    @commands.command(name='dbrefresh', hidden=True)
    @commands.has_permissions(administrator=True)
    async def dbrefresh(self, ctx):
        self.bot.log.warn(f'{ctx.author.name}:{ctx.author.id} issued dbrefresh command')
        await self.on_guild_join(ctx.guild)
        await ctx.send("database refreshed")

    @commands.command(name='reload_modules', hidden=True)
    @commands.is_owner()
    async def reload_modules(self, ctx):
        self.bot.log.warn(f'{ctx.author.name}:{ctx.author.id} issued reload_modules command')
        if ctx.guild is None:
            self.bot.reload_modules()
            await ctx.send(f'modules reloaded')


def setup(bot):
    bot.add_cog(Default(bot))
