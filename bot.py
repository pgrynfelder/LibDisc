from urllib.parse import urlparse
import discord
import asyncio
from discord.ext import commands, tasks
import scraper

from utils import settings, log

client = commands.Bot(command_prefix='>')
messages_queue = asyncio.Queue()
scrap = scraper.Scraper()


@client.event
async def on_ready():
    guild = client.get_guild(settings.GUILD_ID)
    if guild:
        log.info(f'{client.user} is connected to {guild.name}, {guild.id}')
    else:
        raise Exception("Desired guild not connected, turning off.")
    await client.change_presence(activity=discord.Game(name=settings.STATUS))
    get_messages.start()
    post_messages.start()
    log.info("Bot started")


@client.command(name='off', help='Turns the bot off')
@commands.has_role('Admin')
async def turn_off(context):
    log.info("Turning off.")
    await context.send("Turning off.")
    await client.close()
    exit()


@client.command(name='clean', help='Deletes specified number of messages')
@commands.has_role('Admin')
async def clean(context, count: int):
    await context.channel.purge(limit=count)


@client.command(name='fetch', help='Fetch message with specified link')
@commands.has_role('Admin')
async def fetch(context, query: str):
    if not query.isnumeric:
        # Assume it's a valid URL structured like so: https://synergia.librus.pl/wiadomosci/1/5/2179753/f0
        query = urlparse(query).path.split('/')[3]
    async with context.typing():
        scrap.login()
        try:
            msg = scrap.fetch_message(query)
        except scraper.MessageNotFoundException as e:
            await context.send(str(e))
            return
        sent = await context.send(str(msg))
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
    guild = client.get_guild(settings.GUILD_ID)
    cnt = 0
    while not messages_queue.empty():
        msg = await messages_queue.get()
        channel = discord.utils.get(guild.channels, name=msg.channel)
        sent = await channel.send(str(msg))
        await sent.pin()
        cnt += 1
    if cnt:
        log.info(f"Posted {cnt} messages")


if __name__ == "__main__":
    client.run(settings.TOKEN)
