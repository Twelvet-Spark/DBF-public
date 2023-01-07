""" COG default.py
Example of cog, that handle on_ready event.
"""

from discord.ext import commands

class Default(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} online!")

def setup(bot):
    bot.add_cog(Default(bot))