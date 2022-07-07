import disnake
from disnake.ext import commands
from datetime import datetime
import validators
import json

# Make Bot
intents = disnake.Intents().all()
bot = commands.Bot(command_prefix="s!", intents=intents, help_command=None)

# Read config.json
token = json.load(open("config.json"))["TOKEN"]
DBchannel_ID = json.load(open("config.json"))["DatabaseChannel_ID"]
RPchannel_ID = json.load(open("config.json"))["ReportChannel_ID"]

# Whitetlisted links (for now)
WLinks = "https://"

# Commands
@bot.event
async def on_ready():
    print("I am online")

@bot.command()
async def help(ctx):
    await ctx.send("hi")

@bot.event
async def on_message(message):
    if message.channel.id == RPchannel_ID:
        if message.author.id == bot.user.id:  
            if message.content != "Proof has to be a link":
                await message.add_reaction("✅")
                await message.add_reaction("❎")
        else:
            await message.delete()

    await bot.process_commands(message)


# NOT DONE
@bot.event
async def on_raw_reaction_add(reaction):
    if reaction.channel_id == RPchannel_ID:
        channel = bot.get_channel(reation.channel_id)
        message = channel.fetch_message(reaction.message_id)
        if reaction.emoji.name == "✅":
            reacted_emoji = get(message.reactions, emoji = "✅")
            if reacted_emoji.count > 1:
                await message.delete()

@bot.slash_command(description="Report a bug")
async def reportbug(inter, bug: str, proof: str):
    # Get time
    now = datetime.now()
    current_time = now.strftime("%d %b %H:%M:%S")

    # Check if proof is acceptable
    if not validators.url(proof):
        await inter.response.send_message("Proof has to be a link")
    else:
        # Append
        data = {"reporter": inter.author.id, "time": current_time, "bug": bug, "proof": f"{proof} "}
        DBchannel = bot.get_channel(DBchannel_ID)
        await DBchannel.send(data)
        announce = await inter.response.send_message(f"""{inter.author.mention} reported a bug:
        Title: {bug}
        Proof: {proof}""")

@bot.command()
async def read(ctx):
    DBchannel = bot.get_channel(DBchannel_ID)

    data = []
    counter = 0
    async for message in DBchannel.history(limit=None):
        data.append += {"id": message.id, "content": message.content}
    
    await ctx.send(data)


bot.run(token)