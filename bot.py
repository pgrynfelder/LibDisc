import os
import random
import discord
import json
import asyncio
from discord.ext import commands, tasks
import scraper

with open("config.json", encoding="utf_8") as f:
    config = json.load(f)
    TOKEN = config["discord"]["token"]
    GUILD = config["discord"]["guild"]
    del config

bot = commands.Bot(command_prefix='>')
messages_queue = asyncio.Queue()
scrap = scraper.Scraper()

@bot.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.id == GUILD, bot.guilds)
    if guild:
        print(
        f'{bot.user} is connected to {guild.name}, {guild.id}'
    )
    else:
        raise Exception("Desired guild not connected, tunring off")
        exit()
    await bot.change_presence(activity=discord.Game(name='librus 😳😳😳 \n(not all languages supported)'))
    get_messages.start()
    post_messages.start()

@bot.command(name='off', help='Turns the bot off')
@commands.has_role('Admin')
async def turn_off(ctx):
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
    scrap.login()
    msg = scrap.fetch_message(message_id)
    sent = await ctx.channel.send(str(msg))
    await sent.pin()


@tasks.loop(minutes=15)
async def get_messages():
    print("15 minutes passed, checking for new librus messages") 
    scrap.login()
    new_messages = scrap.fetch_unread()
    print("Got " + str(len(new_messages)) + " new messages")
    for msg in new_messages:
        await messages_queue.put(msg)
    del new_messages

@tasks.loop(seconds=30)
async def post_messages():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    cnt = 0
    while not messages_queue.empty():
        msg = await messages_queue.get()
        channel = discord.utils.get(guild.channels, name=msg.channel)
        sent = await channel.send(str(msg))
        await sent.pin()
        cnt += 1
    print(f"Posted {cnt} messages")

if __name__ == "__main__":
    bot.run(TOKEN)
