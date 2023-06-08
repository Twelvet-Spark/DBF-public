""" COG admincommand.py
This cog contains admin commands.
"""
# dasdasd
import os
import sys

import discord
from discord.commands import option
from discord.ext import commands

import configs.config as conf
import modules.db as db
import modules.extensions as extControl

# Make use of the admin roles and thier permissions

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(f"Please don't spam commands, wait {error.cooldown.get_retry_after():.2f} seconds", ephemeral=True, delete_after=5)
        else:
            raise error

    # TODO: move roles check to other module
    def checkRoles(self, authorRoles):
        for role in authorRoles:
            if role.id in conf.ADMIN_COMMANDS_ROLES:
                return True
        return False

    @commands.slash_command(name="ping", description="Latency check", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], conf.COM_COOLDOWN["per"], commands.BucketType.user)
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond(f"-pong! `{int(self.bot.latency*1000)} ms`.")

    @commands.slash_command(name="loadext_all", description="Load all extensions", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], conf.COM_COOLDOWN["per"], commands.BucketType.user)
    async def loadAllExt(self, ctx: discord.ApplicationContext):
        if ctx.author.id in conf.CREATORS_IDS or ctx.author.id == ctx.guild.owner_id:
            extControl.loadAllExt(self.bot)
            await ctx.respond("[ Extensions are loaded successfully ]", ephemeral=True)
        else:
            await ctx.respond(f"You don't have privileges for this command", ephemeral=True)

    @commands.slash_command(name="reloadext_all", description="Reload all extensions", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], conf.COM_COOLDOWN["per"], commands.BucketType.user)
    async def reloadAllExt(self, ctx: discord.ApplicationContext):
        if ctx.author.id in conf.CREATORS_IDS or ctx.author.id == ctx.guild.owner_id:
            extControl.reloadAllExt(self.bot)
            await ctx.respond("[ Extensions are reloaded successfully ]", ephemeral=True)
        else:
            await ctx.respond(f"You don't have privileges for this command", ephemeral=True)

    @commands.slash_command(name="reloadext", description="Reload selected extension", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], conf.COM_COOLDOWN["per"], commands.BucketType.user)
    @option(
        "ext_name",
        description="Extension name",
        required=True,
        choices=conf.EXTENSIONS_LOADED
    )
    async def reloadExt(self, ctx: discord.ApplicationContext, ext_name: str):
        if ctx.author.id in conf.CREATORS_IDS or ctx.author.id == ctx.guild.owner_id:
            try:
                extControl.reloadExt(self.bot, ext_name)
                await ctx.respond(f"[ Extension {ext_name} reloaded successfully ]", ephemeral=True)
            except Exception as e:
                print(e)
                await ctx.respond(f"[ Extension {ext_name} failed to reload ]\n {e}", ephemeral=True)
        else:
            await ctx.respond(f"You don't have privileges for this command", ephemeral=True)

    @commands.slash_command(name="shutdown", description="Send to sleep", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], conf.COM_COOLDOWN["per"], commands.BucketType.user)
    async def shutdown(self, ctx: discord.ApplicationContext):
        if ctx.author.id in conf.CREATORS_IDS or ctx.author.id == ctx.guild.owner_id:
            await ctx.respond("Going to sleep...")
            await self.bot.close()
        else:
            await ctx.respond(f"You don't have privileges for this command", ephemeral=True)

    @commands.slash_command(name="restart", description="Restart", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], conf.COM_COOLDOWN["per"], commands.BucketType.user)
    async def restart(self, ctx: discord.ApplicationContext):
        if ctx.author.id in conf.CREATORS_IDS or ctx.author.id == ctx.guild.owner_id:
            await ctx.respond("Restarting now...")
            print("\n\nRestarting now...\n\n")
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            await ctx.respond(f"You don't have privileges for this command", ephemeral=True)

    @commands.slash_command(name="extcomm", description="Show commands and extensions loaded", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], conf.COM_COOLDOWN["per"], commands.BucketType.user)
    async def extcomm(self, ctx: discord.ApplicationContext):
        if ctx.author.id in conf.CREATORS_IDS or ctx.author.id == ctx.guild.owner_id:
            extList = ""
            cogList = ""
            commList = ""
            for ext in self.bot.extensions.keys():
                extList += f"{ext}, "
            for comm in self.bot.all_commands.values():
                commList += f"{comm}, "
            for cog in self.bot.cogs.keys():
                cogList += f"{cog}, "
            await ctx.respond(f"[ Extestions: {extList} ]\n[ Commands: {commList} ]\n[ Cogs: {cogList} ]", ephemeral=True)
        else:
            await ctx.respond("[ Permission denied ]", ephemeral=True)
            return

    @commands.slash_command(name="logs", description="Send log file to dm", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], conf.COM_COOLDOWN["per"], commands.BucketType.user)
    async def logs(self, ctx: discord.ApplicationContext):
        if ctx.author.id in conf.CREATORS_IDS or ctx.author.id == ctx.guild.owner_id:
            # Check if bot can dm user using .send with None content.
            try:
                await ctx.author.send(None)
            except discord.Forbidden:
                await ctx.respond("Can't send you dm, please check your server settings", ephemeral=True, delete_after=30)
                return
            except discord.HTTPException as ex:
                if ex.status == 400:
                    await ctx.respond(f"Sending log file...", ephemeral=True, delete_after=30)
                else:
                    raise ex
            await ctx.author.send(file=discord.File(f"bot.log"))
        else:
            await ctx.respond(f"You don't have privileges for this command", ephemeral=True)

    @commands.slash_command(name="db", description="Send db file to dm", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], conf.COM_COOLDOWN["per"], commands.BucketType.user)
    async def db(self, ctx: discord.ApplicationContext):
        if ctx.author.id in conf.CREATORS_IDS or ctx.author.id == ctx.guild.owner_id:
            # Check if bot can dm user using .send with None content.
            try:
                await ctx.author.send(None)
            except discord.Forbidden:
                await ctx.respond("Can't send you dm, please check your server settings", ephemeral=True, delete_after=30)
                return
            except discord.HTTPException as ex:
                if ex.status == 400:
                    await ctx.respond(f"Sending db file...", ephemeral=True, delete_after=30)
                else:
                    raise ex
            await ctx.author.send(file=discord.File(conf.DB_PATH))
        else:
            await ctx.respond(f"You don't have privileges for this command", ephemeral=True)

def setup(bot):
    bot.add_cog(AdminCommands(bot))
