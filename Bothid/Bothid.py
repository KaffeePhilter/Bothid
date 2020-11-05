# bothid.py
# GENERAL
import asyncio
import logging
import os
from datetime import datetime, timedelta

# SQL
import aiomysql
# DISCORD
from discord.ext import commands
from dotenv import load_dotenv

# PRIVATE
from utils import config_loader, sql_helper

load_dotenv()


async def determine_prefix(bot, message):
    guild = message.guild
    if guild:
        return bot.prefixes.get(guild.id, ['!', '?'])
    else:
        return ['!', '?']


class Bothid(commands.Bot):

    def __init__(self, *args, **kwargs):
        self.sql_cursor = None
        self.sql_db = None
        super().__init__(*args, **kwargs)
        self.log = self.create_logger(f'LOG_{datetime.now().date()}')
        self.log.info(f'Bot is starting..')
        self.load_modules()
        self._task = self.loop.create_task(self.__log())
        self.sql_helper = sql_helper.SQL_Helper(self.log, self.loop)
        self.prefixes = {}

    @commands.command(name='setprefix', administrator=True)
    @commands.guild_only()
    async def setprefix(self, ctx, *, prefix=""):
        if prefix is None:
            return
        self.prefixes[ctx.guild.id] = prefix

        ctx.send(f'command prefix changed to "{prefix}"')

    @commands.Cog.listener()
    async def on_ready(self):
        await self.sql_helper.init_db()
        self.prefixes = self.sql_helper.get_prefixes()
        self.log.info(f'Bot started')

    def cog_unload(self):
        self._task.cancel()

    def reload_modules(self):
        for name in config_loader.load_conf("config"):
            try:
                self.reload_extension(f'modules.{name}')
                self.log.debug(f'{name} module loaded')
            except commands.ExtensionNotFound:
                self.log.error(f'could not load {name}')

    def load_modules(self):
        for name in config_loader.load_conf("config"):
            try:
                self.load_extension(f'modules.{name}')
                self.log.debug(f'{name} module loaded')
            except commands.ExtensionNotFound:
                self.log.error(f'could not load {name}')

    async def __log(self):
        await self.wait_until_ready()
        self.log.debug(f'TASK "new log": started Task')
        while not self.is_closed():
            sec = self.time_to_next_day()
            self.log.debug(f'TASK "new log": sleeping until next day: {sec}sec')
            await asyncio.sleep(sec)
            self.log = self.create_logger(f'LOG_{datetime.now().date()}')

    @staticmethod
    def time_to_next_day():
        now = datetime.now()
        clean = now + timedelta(days=1)
        goal_time = clean.replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = now
        time_diff = (goal_time - start_time).seconds
        return time_diff

    @staticmethod
    def create_logger(file: str):
        logger = logging.getLogger(file)
        logger.setLevel(logging.DEBUG)
        path = f"logs/{file}.log"
        handler = logging.FileHandler(filename=path, encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(handler)
        return logger


bot = Bothid(command_prefix=determine_prefix, owner_id=142622339434151936)

bot.run(os.getenv('DISCORD_TOKEN'))
