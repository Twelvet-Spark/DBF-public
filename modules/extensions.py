""" MODULE extensions.py
This module contains functions for extension control like: loadAllExt, reloadAllExt
"""

import configs.config as conf
from discord.errors import ExtensionAlreadyLoaded
import os

def getExtList():
    extList = []
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            extList.append(f"cogs.{filename[:-3]}")
    conf.EXTENSIONS_LOADED = extList
    return extList

def loadAllExt(bot):
    print("\nExtension loading...")
    extList = getExtList()
    extNotLoadedList = []
    extLoadedList = []
    for extName in list(extList):
        try:
            bot.load_extension(extName)
            extLoadedList.append(extName)
            print(f"Loaded extension: {extName}")
        except ExtensionAlreadyLoaded:
            print(f"Extension already loaded: {extName}")
    for extName in extList:
        if extName not in bot.extensions.keys():
            extNotLoadedList.append(extName)
    if len(extNotLoadedList) == 0:
        print("All extensions loaded successfully\n\n")
    else:
        print(f"All extensions EXCEPT {len(extNotLoadedList)} extensions are loaded successfully\n\n")
        for extName in extNotLoadedList:
            print(f"Extension: {extName} not loaded")

def reloadAllExt(bot):
    print(f"\nExtension reloading...")
    extList = bot.extensions.keys()
    for extName in list(extList):
        bot.reload_extension(extName)
        print(f"Reloaded extension: {extName}")
    print("All extensions reloaded successfully\n\n")

def reloadExt(bot, extName):
    print(f"\nExtension reloading...")
    extList = bot.extensions.keys()
    if extName in list(extList):
        bot.reload_extension(extName)
        print(f"Reloaded extension: {extName}")

# def unloadAllExt(bot):
#     extList = bot.extensions.keys()
#     for extName in list(extList):
#         bot.unload_extension(extName)

# def loadExt(bot, extName:str):
#     extList = getExtList()
#     if (f"cogs.{extName}") in extList:
#         bot.load_extension(f"cogs.{extName}", override=True)

# def unloadExt(bot, extName:str):
#     if (f"cogs.{extName}") in list(bot.extensions.keys()):
#         bot.unload_extension(f"cogs.{extName}")
#         return "unloaded"
#     else:
#         return "not unloaded"