import os
import aiomysql
from dotenv import load_dotenv


class SQL_Helper():
    def __init__(self, log):
        self.sql_db = None
        self.sql_cursor = None
        self.log = log
        load_dotenv()

    async def init_db(self, loop):
        self.sql_db = await aiomysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PWD'),
            db=os.getenv('DB_NAME'),
            loop=loop,
            autocommit=True
        )
        self.log.debug(f'Database connection established')
        self.sql_cursor = await self.sql_db.cursor()
        await self.execute(
            f'CREATE TABLE IF NOT EXISTS guilds (id BIGINT UNSIGNED PRIMARY KEY, name VARCHAR(255) NOT NULL );'
        )
        self.log.debug(f'Database initialized')

    async def new_member(self, guild, member):
        await self.execute(
            f'INSERT INTO {guild.id} VALUES({member.id}, "{member.name}", 50, 0) ON DUPLICATE KEY UPDATE user_name = "{member.name}";')

    async def new_guild(self, guild):
        # create new guild member table
        await self.execute(
            f'CREATE TABLE IF NOT EXISTS `{guild.id}`(id BIGINT UNSIGNED UNIQUE, user_name VARCHAR(255), coins INTEGER UNSIGNED, level INTEGER UNSIGNED);')
        # insert new guild to guilds table
        await self.execute(
            f'INSERT INTO guilds VALUES({guild.id}, "{guild.name}") ON DUPLICATE KEY UPDATE name = "{guild.name}";')

    async def update_coins(self, guild, user, add_val: int):
        await self.execute(f'UPDATE `{guild.id}` SET coins = coins + {add_val} WHERE id = {user.id}')

    async def get_coins(self, ctx):
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
        await self.sql_cursor.execute(query)
        self.log.debug(f'SQL Query executed: {query}')

    async def fetchall(self, query: str):
        await self.execute(query)
        return await self.sql_cursor.fetchall()

    async def fetchmany(self, query: str, rows: int):
        await self.execute(query)
        sql_res = None
        if rows == 1:
            sql_res = await self.sql_cursor.fetchone()
        elif rows > 1:
            sql_res = await self.sql_cursor.fetchmany(rows)
        return sql_res
