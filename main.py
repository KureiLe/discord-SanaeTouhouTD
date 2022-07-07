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
DBchannel2_ID = json.load(open("config.json"))["DatabaseChannel2_ID"]
RPchannel_ID = json.load(open("config.json"))["ReportChannel_ID"]

# Whitetlisted links (for now)
WLinks = "https://"

# Commands
@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Streaming(name="Touhou TD", url="https://www.roblox.com/games/8316708135/touhou-tower-defense"))
    await bot.change_presence(status="prefix = s!")
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

@bot.event
async def on_raw_reaction_add(reaction):
    if reaction.channel_id == RPchannel_ID:
        # Get channel
        DBchannel = bot.get_channel(DBchannel_ID)
        DBchannel2 = bot.get_channel(DBchannel2_ID)
        channel = bot.get_channel(reaction.channel_id)
        # Get message
        message = await channel.fetch_message(reaction.message_id)
        # Self explanatory
        if reaction.emoji.name == "✅":
            for x in message.reactions:
                if "✅" in list(str(x)):
                    count = int(x.count)
                    # Get data from db2
                    async for msg in DBchannel2.history(limit=None):
                        DB2_data = json.loads(msg.content.replace("'", '"'))
                        if DB2_data["reportMSG_ID"] == reaction.message_id:
                            DB2_data["reactions"] = count
                            await msg.edit(content=str(DB2_data))

        elif reaction.emoji.name == "❎":
            for x in message.reactions:
                if "❎" in list(str(x)):
                    count = int(x.count)
                    # If theres 2 or more X reaction
                    if count >= 2:
                        # Get data from database2
                        async for msg in DBchannel2.history(limit=None):
                            # Turn it to dictionary
                            DB2_data = json.loads(msg.content.replace("'", '"'))
                            # Boom
                            if DB2_data["reportMSG_ID"] == reaction.message_id:
                                await message.delete()
                                DBDel = await DBchannel.fetch_message(DB2_data["databaseMSG_ID"])
                                await DBDel.delete()
                                await msg.delete()

        elif reaction.emoji.name != "✅" or "❎":
            await message.clear_reaction(emoji=reaction.emoji.name)

@bot.slash_command(description="Report a bug")
async def reportbug(inter, bug: str, proof: str):
    if inter.channel_id == RPchannel_ID:
        # Get time
        now = datetime.now()
        current_time = now.strftime("%d %b %H:%M:%S")

        # Check if proof is acceptable
        if not validators.url(proof):
            await inter.response.send_message("Proof has to be a link")
        else:
            # Data
            data = {"reporter": inter.author.id, "time": current_time, "bug": bug, "proof": f"{proof} "}
            # Get channel
            RPchannel = bot.get_channel(RPchannel_ID)
            DBchannel = bot.get_channel(DBchannel_ID)
            DBchannel2 = bot.get_channel(DBchannel2_ID)
            # Append database 1
            DBsend = await DBchannel.send(str(data))
            # Announce
            announce = await RPchannel.send(f"{inter.author.mention} reported a bug:\nTitle: {bug}\nProof: {proof}")
            # Append database2
            data2 = {"reportMSG_ID": announce.id, "databaseMSG_ID": DBsend.id, "reactions": 0}
            await DBchannel2.send(str(data2))
    else:
        await inter.response.send_message("Must report bug in the correct channel")

bot.run(token)