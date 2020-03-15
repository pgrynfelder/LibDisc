import os
import random
import discord
from discord.ext import commands, tasks

import scraper

with open("config.json", encoding="utf_8") as f:
    config = json.load(f)
    TOKEN = config["discord"]["token"]
    GUILD = config["discord"]["token"]
    del config;

bot = commands.Bot(command_prefix='>')

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds,name=GUILD)
    print(
        f'{bot.user} is connected to {guild.name}, {guild.id}'
    )
    await bot.change_presence(activity=discord.Game(name='librus 😳😳😳'))

@bot.task


@bot.command(name='off', help='Turns the bot off')
@commands.has_role('Admin')
async def turn_off(ctx):
    await ctx.send("Turning off.")
    await bot.close()
    exit()

bot.run(TOKEN)