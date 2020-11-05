import os
import aiomysql
import asyncio
from dotenv import load_dotenv


class SQL_Helper():

    def __init__(self, log, loop):
        self.sql_db = None
        self.pool = None
        self.sql_cursor = None
        self.timeout = self.reset_timeout()
        self.log = log
        self.loop = loop
        self._task_timeout = self.loop.create_task(self.__timeout())
        load_dotenv()

    # TODO this is new
    async def __timeout(self):
        """
        task for timeouting the db connect
        :return: nothing
        """
        while True:
            await asyncio.sleep(1)
            self.timeout -= 1

            if self.timeout <= 0:
                self.sql_db.close()
                self.log.info(f'Reconnecting db after timeout')
                await self.reconnect()

    async def init_db(self):
        """
        initilizes the db connection
        :param loop: event loop of the bot
        :return: nothing
        """

        # TODO make pool everywhere

        self.pool = await aiomysql.create_pool(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PWD'),
            db=os.getenv('DB_NAME'),
            loop=self.loop,
            autocommit=True
        )

        self.sql_db = await aiomysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PWD'),
            db=os.getenv('DB_NAME'),
            loop=self.loop,
            autocommit=True,
            connect_timeout=None
        )
        self.log.debug(f'Database connection established')
        self.sql_cursor = await self.sql_db.cursor()
        await self.execute(
            f'CREATE TABLE IF NOT EXISTS guilds (id BIGINT UNSIGNED PRIMARY KEY, name VARCHAR(255) NOT NULL, prefix CHAR);'
        )
        self.log.debug(f'Database initialized')

    # TODO this is new
    async def reconnect(self):
        """
        reconnect the db
        :return: nothing
        """
        await self.init_db()

    # TODO this is new
    def reset_timeout(self):
        self.timeout = 600
        return self.timeout

    async def new_member(self, guild, member):
        """
        creates a new user in the db

        :param guild: discord.guild
        :param member: discord.member
        """
        await self.execute(
            f'INSERT INTO `{guild.id}` VALUES({member.id}, "{member.name}", 50, 0) ON DUPLICATE KEY UPDATE user_name = "{member.name}";')

    async def new_guild(self, guild):
        """
        creates a new guild, only needs a discord.guild object

        :param guild: discord.guild
        """
        # create new guild member table
        await self.execute(
            f'CREATE TABLE IF NOT EXISTS `{guild.id}`(id BIGINT UNSIGNED UNIQUE, user_name VARCHAR(255), coins INTEGER UNSIGNED, level INTEGER UNSIGNED);')
        # insert new guild to guilds table
        await self.execute(
            f'INSERT INTO guilds VALUES({guild.id}, "{guild.name}") ON DUPLICATE KEY UPDATE name = "{guild.name}";')

    async def update_coins(self, guild, user, add_val: int):
        """
        update the coins for a user in a guild

        :param guild: discord.guild
        :param user: discord.user
        :param add_val: int
        :return: nothing
        """
        await self.execute(f'UPDATE `{guild.id}` SET coins = coins + {add_val} WHERE id = {user.id}')

    # @params
    async def get_coins(self, ctx):
        """
        get the coins of a user, needs the message context object

        :param ctx: discord.ctx
        :return nothing
        """
        res = await self.fetchmany(
            f'SELECT coins FROM `{ctx.guild.id}` WHERE id = {ctx.author.id}', 1)
        # adding user if not exists
        if res is None:
            self.log.debug(
                f'{ctx.author.name}:{ctx.author.id} was not found in {ctx.guild.name}:{ctx.guild.id} database. Adding now with 50 coins')
            await self.new_member(ctx.guild, ctx.author)
            await ctx.send(f'Oh I do not know you yet! Here take 50 coins. Have fun! :)')
            return
        else:
            return res[0]

    async def execute(self, query: str):
        """
        executes a given query
        :param query: str
        :return: nothing
        """
        await self.sql_cursor.execute(query)
        self.log.debug(f'SQL Query executed: {query}')

        # TODO this is new
        self.reset_timeout()

    async def fetchall(self, query: str):
        """
        fetches all rows from the given query
        :param query: must be a select query
        :return: list of rows fetched
        """
        await self.execute(query)
        return await self.sql_cursor.fetchall()

    async def fetchmany(self, query: str, rows: int):
        """
        fetches given number of rows and returns them
        :param query: select query
        :param rows: number of rows to fetch
        :return: list of rows fetched
        """
        await self.execute(query)
        sql_res = None
        if rows == 1:
            sql_res = await self.sql_cursor.fetchone()
        elif rows > 1:
            sql_res = await self.sql_cursor.fetchmany(rows)
        return sql_res

    async def get_prefixes(self):
        """
        fetches the prefix for each server and returns a dictionary
        :return: dictionary
        """
        temp_dict = dict()
        rows = await self.fetchall(f'SELECT id, prefix from guilds')
        for r in rows:
            temp_dict[r[1]] = r[2]

        return temp_dict
