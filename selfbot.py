import discord, logging
from discord.ext import commands, tasks

client = commands.Bot(command_prefix='-', description="Just a another selfbot", self_bot=True)
client.logger = logging.getLogger("mainlogger")
client.logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='selfbot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
client.logger.addHandler(handler)
client.logger.warning("Starting...")

client.version = "0.0.4"
client.status = "dnd"
client.status_deflaut = "dnd"
client.TOKEN = "Your token HERE"

@tasks.loop(minutes=1)
async def afk():
    if client.status == "dnd":
        await client.change_presence(status=discord.Status.dnd, afk=False)
    elif client.status == "online":
        await client.change_presence(status=discord.Status.idle, afk=False)
    elif client.status == "offline" or client.status == "invisible":
        await client.change_presence(status=discord.Status.idle, afk=False)
    elif client.status == "idle" or client.status == "afk":
        await client.change_presence(status=discord.Status.idle, afk=True)
    else: client.status = client.status_deflaut

@client.event
async def on_ready():
    client.load_extension(f"maincog")
    client.logger.warning("Started!")
    client.logger.warning(f"Logged in as {client.user} (ID: {client.user.id})")
    client.logger.warning("------")
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    afk.start()

@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        client.status = client.status_deflaut
        await client.process_commands(message)

@client.command()
async def reload(ctx):
    """Reload maincog"""
    print(f"Reloading maincog")
    try: client.reload_extension(f"maincog")
    except:
        client.load_extension(f"maincog")
        client.unload_extension(f"maincog")
    await ctx.send("Cog reloaded")
client.run(client.TOKEN)