import os
import random
import discord
import json
import asyncio
import logging
import sys
from discord.ext import commands, tasks
import scraper

with open("config.json", encoding="utf_8") as f:
    config = json.load(f)
    TOKEN = config["discord"]["token"]
    GUILD = config["discord"]["guild"]
    GUILD_ID = config["discord"]["guildid"]
    del config

bot = commands.Bot(command_prefix='>')
messages_queue = asyncio.Queue()
scrap = scraper.Scraper()

log = logging.getLogger()
log.setLevel(logging.INFO)
handler_stdout = logging.StreamHandler(sys.stdout)
log.addHandler(handler_stdout)
handler_file = logging.handlers.RotatingFileHandler("libdisc.log", mode='a', maxBytes=5*1024*1024, backupCount=2)
log.addHandler(handler_file)


@bot.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    if guild:
        log.info(
            f'{bot.user} is connected to {guild.name}, {guild.id}'
        )
    else:
        raise Exception("Desired guild not connected, turning off")
        exit()
    await bot.change_presence(activity=discord.Game(name='librus 😳😳😳 \n(not all languages supported)'))
    get_messages.start()
    post_messages.start()
    print("Bot started")


@bot.command(name='off', help='Turns the bot off')
@commands.has_role('Admin')
async def turn_off(ctx):
    log.info("Turning off")
    await ctx.send("Turning off.")
    await bot.close()
    exit()


@bot.command(name='clean', help='Deletes specified number of messages')
@commands.has_role('Admin')
async def clean(ctx, cnt: int):
    await ctx.channel.purge(limit=cnt)


@bot.command(name='fetch', help='Fetch message with specified link')
@commands.has_role('Admin')
async def fetch(ctx, message_id: str):
    async with ctx.typing():
        scrap.login()
        msg = scrap.fetch_message(message_id)
        sent = await ctx.channel.send(str(msg))
        await sent.pin()


@tasks.loop(minutes=15)
async def get_messages():
    log.info("15 minutes passed, checking for new librus messages")
    scrap.login()
    new_messages = scrap.fetch_unread()
    log.info("Got " + str(len(new_messages)) + " new messages")
    for msg in new_messages:
        await messages_queue.put(msg)
    del new_messages


@tasks.loop(seconds=30)
async def post_messages():
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    cnt = 0
    while not messages_queue.empty():
        msg = await messages_queue.get()
        channel = discord.utils.get(guild.channels, name=msg.channel)
        sent = await channel.send(str(msg))
        await sent.pin()
        cnt += 1
    if cnt: log.info(f"Posted {cnt} messages")

if __name__ == "__main__":
    bot.run(TOKEN)
