""" COG datecheck.py
This cog is responsible for checking your discord and server registration date.
Functions for comparing dates.
"""

import configs.config as conf
import discord
import secrets
from discord.commands import option
from discord.ext import commands
from datetime import datetime, timedelta

# TODO: Add parameter to check date with one selected user

class DateCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.inaccuracyLimit = 31

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(f"Please don't spam commands, wait {error.cooldown.get_retry_after():.2f} seconds", ephemeral=True, delete_after=5)
        else:
            raise error

    @commands.slash_command(name="compare_dates", description="Compare your registrations date with others", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], (conf.COM_COOLDOWN["per"]+15), commands.BucketType.user)
    @option(
        "inaccuracy",
        description="Range in days",
        type=int,
        required=False,
        default=0,
    )
    async def compareMyDates(self, ctx: discord.ApplicationContext, inaccuracy: int):
        await ctx.respond("Please wait, im working on it...", ephemeral=True)
        inaccuracyCreatedDatesList = []
        inaccuracyJoinedDatesList = []
        if inaccuracy != 0:
            if inaccuracy <= self.inaccuracyLimit:
                for i in range(0, inaccuracy):
                    inaccuracyCreatedDatesList.append(datetime(ctx.author.created_at.year, ctx.author.created_at.month, ctx.author.created_at.day).date() - timedelta(days=(inaccuracy-i)))
                    inaccuracyJoinedDatesList.append(datetime(ctx.author.joined_at.year, ctx.author.joined_at.month, ctx.author.joined_at.day).date() - timedelta(days=(inaccuracy-i)))
                for i in range(0, inaccuracy):
                    inaccuracyCreatedDatesList.append(datetime(ctx.author.created_at.year, ctx.author.created_at.month, ctx.author.created_at.day).date() + timedelta(days=i))
                    inaccuracyJoinedDatesList.append(datetime(ctx.author.joined_at.year, ctx.author.joined_at.month, ctx.author.joined_at.day).date() + timedelta(days=i))
            else:
                await ctx.respond(f"Please don't exceed the limit: {self.inaccuracyLimit}", ephemeral=True)
                return 0
        else:
            inaccuracyCreatedDatesList.append(ctx.author.created_at.date())
            inaccuracyJoinedDatesList.append(ctx.author.joined_at.date())
        respondText = (f"Result (range={inaccuracy}):\n")
        discordRegDate = []
        discordLenRegDate = 0
        serverRegDate = []
        serverLenRegDate = 0
        for member in list(ctx.channel.members):
            if member.id != ctx.author.id:
                if member.created_at.date() in inaccuracyCreatedDatesList:
                    if member.created_at.date() == ctx.author.created_at.date():
                        daysDifference = (F"same day as you {datetime.strftime(ctx.author.created_at.date(), '%d.%m.%Y')}!")
                    elif member.created_at.date() > ctx.author.created_at.date():
                        daysDifference = (f"later than you {datetime.strftime(ctx.author.created_at.date(), '%d.%m.%Y')} by {(member.created_at.date() - ctx.author.created_at.date()).days} days") # TODO: Change "дней" based on number
                    elif member.created_at.date() < ctx.author.created_at.date():
                        daysDifference = (f"before than you {datetime.strftime(ctx.author.created_at.date(), '%d.%m.%Y')} by {(ctx.author.created_at.date() - member.created_at.date()).days} days")
                    else:
                        daysDifference = "__error__"
                    discordRegDate.append(f"```{member.name} account created at {datetime.strftime(member.created_at.date(), '%d.%m.%Y')}, {daysDifference}```")
                if member.joined_at.date() in inaccuracyJoinedDatesList:
                    if member.joined_at.date() == ctx.author.joined_at.date():
                        daysDifference = (f"same day as you {datetime.strftime(ctx.author.joined_at.date(), '%d.%m.%Y')}!")
                    elif member.joined_at.date() > ctx.author.joined_at.date():
                        daysDifference = (f"later than you {datetime.strftime(ctx.author.joined_at.date(), '%d.%m.%Y')} by {(member.joined_at.date() - ctx.author.joined_at.date()).days} days") # TODO: Change "дней" based on number
                    elif member.joined_at.date() < ctx.author.joined_at.date():
                        daysDifference = (f"before than you {datetime.strftime(ctx.author.joined_at.date(), '%d.%m.%Y')} by {(ctx.author.joined_at.date() - member.joined_at.date()).days} days")
                    else:
                        daysDifference = "__error__"
                    serverRegDate.append(f"```{member.name} enter server at {datetime.strftime(member.joined_at.date(), '%d.%m.%Y')}, {daysDifference}```")
        # Check logic
        discordLenRegDate = len(discordRegDate)
        serverLenRegDate = len(serverRegDate)
        # Check for discord registration date
        if discordLenRegDate != 0:
            if inaccuracy == 0:
                respondText += (f"You have similar registration date ({ctx.author.created_at.date()}) with {discordLenRegDate} user")
            else:
                respondText += (f"In range from {ctx.author.created_at.date()-timedelta(inaccuracy)} to {ctx.author.created_at.date()+timedelta(inaccuracy)} you have similar registration date with {discordLenRegDate} user:\n")
            respondText += (' '.join(discordRegDate))
        else:
            if inaccuracy == 0:
                respondText += (f"No one has reg date like yours - {ctx.author.created_at.date()}\n")
            else:
                respondText += (f"No one has reg date like yours in range from {ctx.author.created_at.date()-timedelta(inaccuracy)} to {ctx.author.created_at.date()+timedelta(inaccuracy)}\n")
        # Check for server enter date
        if serverLenRegDate != 0:
            if inaccuracy == 0:
                respondText += (f"\nWith you at {ctx.author.joined_at.date()} has been joined {serverLenRegDate} user")
            else:
                respondText += (f"\nIn range from {ctx.author.joined_at.date()-timedelta(inaccuracy)} to {ctx.author.joined_at.date()+timedelta(inaccuracy)}, {serverLenRegDate} users has joined with you:\n")
            respondText += (' '.join(serverRegDate))
        else:
            if inaccuracy == 0:
                respondText += (f"No one has join date like yours {ctx.author.joined_at.date()}, тоже нету.")
            else:
                respondText += (f"No one has join date like yours in range from {ctx.author.joined_at.date()-timedelta(inaccuracy)} по {ctx.author.joined_at.date()+timedelta(inaccuracy)}, тоже нету.")
        await ctx.interaction.edit_original_response(content=respondText)

def setup(bot):
    bot.add_cog(DateCheck(bot))