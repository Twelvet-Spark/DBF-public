""" COG birthdayreminder.py
This cog contains commands to set/get user birthday,
function for reminding other users in chat about birthdays.
"""

import secrets
import discord
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from discord.commands import option
import configs.config as conf
import modules.db as db

# TODO: Optional year argument
# TODO: Rework how set_birthday() command actually check if there is already user in df, just in case.
# TODO: Rework updating birtdayUsersList in 1 day, update it every hour to catch new data, and just remove users that been annouced or not, and then annouce new users.

class BirthdayReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.isBirthdayAnnounced = False
        self.bdUsersList = []
        self.dateTime = datetime.now().date() - timedelta(days=1)
        self.checkBirthdays.start()

    def cog_unload(self):
        self.checkBirthdays.cancel()

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(f"Please don't spam commands, wait {error.cooldown.get_retry_after():.2f} seconds", ephemeral=True, delete_after=5)
        else:
            raise error

    def updateBDUsersList(self):
        self.dateTime = datetime.now().date()
        df = db.readRecords('dict')
        self.bdUsersList.clear()
        for user in df:
            if user["birthday"][:-5] == datetime.strftime(datetime.now().date(), "%d.%m.%Y")[:-5]:
                self.bdUsersList.append(user)

    # TODO: Optimize self.bdUsersList update, because it's updating every time checkBirthdays called, it's bad.
    # Should be another function that would check if today datetime.now() self.birthdayUsers been updated, if not then update it and check bool variable set True for datetime.now()
    # TODO: How to check if user birthday was already mentioned???? Even with reloading and shutdowns??
    @tasks.loop(hours=1)
    async def checkBirthdays(self):
        if datetime.now().date() > self.dateTime:
            self.isBirthdayAnnounced = False
            self.updateBDUsersList()
        bdChannel = self.bot.get_channel(conf.BIRTHDAY_CHANNEL_ID)
        if self.isBirthdayAnnounced == False:
            if len(self.bdUsersList) == 0:
                print("No birthdays today")
            elif len(self.bdUsersList) == 1:
                userAge = int(datetime.now().year) - int(self.bdUsersList[0]['birthday'][-4:])
                await bdChannel.send(f"@everyone\nHappy {userAge} birthday <@{self.bdUsersList[0]['id']}>!")
            elif len(self.bdUsersList) > 1:
                usersIdsFormatted = []
                for user in self.bdUsersList:
                    userAge = int(datetime.now().year) - int(user['birthday'][-4:])
                    usersIdsFormatted.append(f"\n<@{user['id']}> now {userAge}")
                await bdChannel.send(f"@everyone\nToday we have few birthdays!{'; '.join(usersIdsFormatted)}.")
            self.isBirthdayAnnounced = True

    @checkBirthdays.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    @commands.slash_command(name="show_all_birthdays", description="Show all bitrhdays", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], conf.COM_COOLDOWN["per"], commands.BucketType.user)
    async def showAllBirthdays(self, ctx: discord.ApplicationContext):
        await ctx.respond(f"{db.readRecords()}")

    @commands.slash_command(name="set_birthday", description="Write down your birthday", guild_ids=conf.GUILD_ID)
    @commands.cooldown(conf.COM_COOLDOWN["rate"], conf.COM_COOLDOWN["per"], commands.BucketType.user)
    @option(
        "day",
        description="Day",
        required=True
    )
    @option(
        "month",
        description="Mounth",
        required=True
    )
    @option(
        "year",
        description="Year",
        required=True
    )
    async def setBirthday(self, ctx: discord.ApplicationContext, day: int, month: int, year: int):
        # Check date format before actions
        if (0 < day <= 31) and (0 < month <= 12) and ((datetime.now().year-200) < year <= (datetime.now().year)):
            strDay = ''
            strMonth = ''
            if day < 10: strDay = (f'0{day}')
            else: strDay = (f'{day}')
            if month < 10: strMonth = (f'0{month}')
            else: strMonth = (f'{month}')
            writeStatus = db.createRecord(ctx.author.id, ctx.author.name, (f"{strDay}.{strMonth}.{year}"))
            if (writeStatus == 1):
                await ctx.respond(f"Successfully wrote down!", ephemeral=True)
            else:
                db.updateRecord(ctx.author.id, ctx.author.name, birthday=(f"{strDay}.{strMonth}.{year}"))
                await ctx.respond(f"Successefully updated!", ephemeral=True)
        else:
            await ctx.respond(f"Something wrong with the date, please check your date and try again", ephemeral=True)

def setup(bot):
    bot.add_cog(BirthdayReminder(bot))