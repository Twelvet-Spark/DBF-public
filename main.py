""" main.py
Bot creators Twine#3224, Riiza Tensely#6971
"""

import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import configs.config as conf
import modules.db as db
import modules.extensions as ext
import os
import logging

load_dotenv("./configs/.env")

bot = commands.Bot(intents=discord.Intents.all())

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG) # Do not allow DEBUG messages through
handler = logging.FileHandler(filename="bot.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("{asctime}: {levelname}: {name}: {message}", style="{"))
logger.addHandler(handler)

async def main():
    ext.loadAllExt(bot)
    await bot.start(os.getenv("TOKEN"))

asyncio.get_event_loop().run_until_complete(main())