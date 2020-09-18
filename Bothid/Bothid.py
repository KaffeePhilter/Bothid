# bothid.py
# GENERAL
import os
import logging
from datetime import datetime

# PRIVATE
from utils import config_loader

# DISCORD
# from discord
from discord.ext import commands

# SQL
import mysql.connector as sql

from dotenv import load_dotenv

load_dotenv()


class Bothid(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = self.create_logger(f'LOG_{datetime.now().date()}')
        self.sql_db = self.connect_db()
        self.sql_cursor = self.sql_db.cursor()
        self.sql_db_init()
        self.load_modules()

    @staticmethod
    def connect_db():
        return sql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PWD'),
            database=os.getenv('DB_NAME')
        )

    def sql_db_init(self):
        self.sql_execute(
            f'CREATE TABLE IF NOT EXISTS guilds (id INTEGER PRIMARY KEY UNIQUE, name VARCHAR(255) NOT NULL );'
        )

    def sql_execute(self, query: str):
        self.sql_cursor.execute(query)
        self.log.debug(f'SQL Query executed: {query}')
        self.sql_db.commit()

    def sql_fetchall(self, query: str):
        self.sql_cursor.execute(query)
        return self.sql_cursor.fetchall()

    def sql_fetchmany(self, query: str, rows: int):
        self.sql_cursor.execute(query)
        if rows == 1:
            return self.sql_cursor.fetchone()
        elif rows > 1:
            return self.sql_cursor.fetchmany(rows)

    def load_modules(self):
        for name in config_loader.load_conf("config"):
            try:
                self.load_extension(f'modules.{name}')
            except commands.ExtensionNotFound:
                print(f"could not load {name}")

    @staticmethod
    def create_logger(file: str):
        logger = logging.getLogger(file)
        logger.setLevel(logging.DEBUG)
        path = f"logs/{file}.log"
        handler = logging.FileHandler(filename=path, encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(handler)
        return logger


bot = Bothid(command_prefix='!', owner_id=142622339434151936)

bot.run(os.getenv('DISCORD_TOKEN'))
