""" COG feedback.py
This cog contains feedback commands for users
"""

import discord
import os
import re
from discord.ext import commands
from discord.commands import option
import configs.config as conf
from datetime import datetime
import asyncio

class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(f"Please don't spam commands, wait {error.cooldown.get_retry_after():.2f} seconds", ephemeral=True, delete_after=5)
        else:
            raise error

    @commands.slash_command(name="show_feedbacks", description="Show users feedbacks", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], (conf.COM_COOLDOWN["per"]), commands.BucketType.user)
    async def showFeedbacks(self, ctx: discord.ApplicationContext):
        await ctx.respond("Please wait im working on it...", ephemeral=True)
        respondText = "Users feedbacks:"
        userFeedbackCount = {}
        for filename in sorted(os.listdir("./feedback")):
            if int(filename.split('_')[1]) in userFeedbackCount.keys():
                userFeedbackCount[int(filename.split('_')[1])] += 1
            else:
                userFeedbackCount[int(filename.split('_')[1])] = 1
        for userID in userFeedbackCount.keys():
            respondText += (f"<@{userID}>: {userFeedbackCount[userID]} feedbacks")
        await ctx.interaction.edit_original_response(content=respondText)

    @commands.slash_command(name="feedback", description="Write a feedback", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], (conf.COM_COOLDOWN["per"]+600), commands.BucketType.user)
    @option(
        "text",
        description="Text",
        required=True
    )
    async def feedback(self, ctx: discord.ApplicationContext, text: str):
        date = datetime.now()
        with open((f'feedback/feedback_{ctx.author.id}_{date.day}-{date.month}-{date.year}_{date.hour}-{date.minute}-{date.second}.txt'), 'x', encoding="utf-8") as f:
            f.write(f'DATE: {date.day}-{date.month}-{date.year} TIME: {date.hour}-{date.minute}-{date.second}\nUSER_ID: {ctx.author.id}\nUSER_NAME: {ctx.author.name}\n\nMESSAGE_TEXT: {text}')
        await ctx.respond(f"Thank you for your feedback", ephemeral=True)

    @commands.slash_command(name="read_feedback", description="Last 5 feedbacks from user", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], (conf.COM_COOLDOWN["per"]), commands.BucketType.user)
    @option(
        "user",
        description="User",
        required=True
    )
    @option(
        "sort",
        description="Sort type",
        required=True,
        default="new first",
        choices=["new first", "old first"]
    )
    async def read_feedback(self, ctx: discord.ApplicationContext, user: discord.Member, sort: str):
        # Check if bot can dm user using .send with None content.
        try:
            await ctx.author.send(None)
        except discord.Forbidden:
            await ctx.respond("Can't send you dm, please check your server settings", ephemeral=True, delete_after=60)
            return
        except discord.HTTPException as ex:
            if ex.status == 400:
                await ctx.respond(f"You will recieve feedbacks from {user.name} in dm", ephemeral=True, delete_after=60)
            else:
                raise ex
        filenameUserID = 0
        feedbackByUserlist = []
        for filename in sorted(os.listdir("./feedback")):
            filenameUserID = int(filename.split('_')[1])
            if filenameUserID == user.id:
                feedbackByUserlist.append(filename)
        # Sort start. All feedback from user by date.
        swapped = False
        for i in range(len(feedbackByUserlist)-1):
            for j in range(0, len(feedbackByUserlist)-i-1):
                if datetime(int(re.findall(r"[0-9]+", feedbackByUserlist[j])[3]), int(re.findall(r"[0-9]+", feedbackByUserlist[j])[2]), int(re.findall(r"[0-9]+", feedbackByUserlist[j])[1])) > datetime(int(re.findall(r"[0-9]+", feedbackByUserlist[j+1])[3]), int(re.findall(r"[0-9]+", feedbackByUserlist[j+1])[2]), int(re.findall(r"[0-9]+", feedbackByUserlist[j+1])[1])):
                    swapped = True
                    feedbackByUserlist[j], feedbackByUserlist[j + 1] = feedbackByUserlist[j + 1], feedbackByUserlist[j]
            if not swapped:
                break
        # Sort end.
        if len(feedbackByUserlist) > 5:
            if sort == "old first":
                feedbackByUserlist = feedbackByUserlist[-5:]
            elif sort == "new first":
                feedbackByUserlist = feedbackByUserlist[-5:][::-1]
            else:
                await ctx.respond("Something went wrong...", ephemeral=True)
                return
        for filename in feedbackByUserlist:
            await ctx.author.send(file=discord.File(f"feedback/{filename}"))
            await asyncio.sleep(3)


def setup(bot):
    bot.add_cog(Feedback(bot))