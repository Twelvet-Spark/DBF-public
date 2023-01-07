""" COG backupdb.py
This cog call db.backupDB() every X time.
X is days, hours, min, sec.
"""

from discord.ext import commands, tasks
import configs.config as conf
import modules.db as db

class BackupDB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.callBackupDB.start()
    
    def cog_unload(self):
        self.callBackupDB.cancel()

    @tasks.loop(hours=2) # Set timeout for backup
    async def callBackupDB(self):
        db.backupDB(conf.DB_PATH)

    @callBackupDB.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(BackupDB(bot))