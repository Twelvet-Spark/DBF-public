""" COG interactions.py
This cog contains user interactions.
"""

import configs.config as conf
import discord
from discord.commands import option
from discord.ext import commands, tasks
from datetime import datetime
import random
import secrets

# TODO: Create functionality to send .gif on hugs, kiss
# TODO: Add special interaction if user trying to kiss Felly, and maybe other bots
# TODO: Fix spelling error in kiss when user trying to kiss himself

class Interactions(commands.Cog):
    """ HOW TO FORMAT:
        {0} is authorUser
        {1} is targetUser
        {2} is randomUser
    """
    def __init__(self, bot):
        self.bot = bot
        self.hugList = ["{0} hugs {1}"]
        self.randomFact = ["random fact about {0}"]
        self.time = datetime
        self.updateTimeSeed.start()

    def cog_unload(self):
        self.updateTimeSeed.cancel()

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(f"Please don't spam commands, wait {error.cooldown.get_retry_after():.2f} seconds", ephemeral=True, delete_after=5)
        else:
            raise error

    @tasks.loop(hours=12)
    async def updateTimeSeed(self):
        self.time = datetime.now()
        print(f"Seed time changed to: {self.time}")

    @updateTimeSeed.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    def getUserSeed(self, userId):
        userSeed = (int(self.time.strftime("%Y%m%d%H%M%S")) + userId)
        return userSeed

    @commands.slash_command(name="hug", description="Hug user", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], conf.COM_COOLDOWN["per"], commands.BucketType.user)
    async def hug(self, ctx: discord.ApplicationContext, target_user: discord.Member):
        if target_user.id == ctx.author.id:
            await ctx.respond(f"{ctx.author.mention} is selfhugging")
        else:
            randomUser = None
            while randomUser == None or randomUser == ctx.author or randomUser == target_user: # TODO: May have optimization problem
                randomUser = secrets.choice(ctx.channel.members)
            respondText = (secrets.choice(self.hugList)).format(ctx.author.mention, target_user.mention, randomUser.mention)
            await ctx.respond(f"{respondText}")

    @commands.slash_command(name="fact", description="Daily fact about user", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], conf.COM_COOLDOWN["per"], commands.BucketType.user)
    async def fact(self, ctx: discord.ApplicationContext, user: discord.Member):
        random.seed(self.getUserSeed(user.id))
        await ctx.respond(f"{user.mention} {random.choice(self.randomFact)}")

def setup(bot):
    bot.add_cog(Interactions(bot))