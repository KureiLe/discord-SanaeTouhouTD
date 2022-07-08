import disnake
from disnake.ext import commands
from disnake.ext.commands import has_permissions, MissingPermissions
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

# Commands
@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Game(name="Touhou TD"), status="prefix = s!")
    print("I am online")

@bot.event
async def on_message(message):
    if message.channel.id == RPchannel_ID:
        if message.author.id == bot.user.id:  
            # Having 3 and in a bool doenst work for some reason
            if message.content != "Lady Suwako only allow Admins to use this command." and message.content !=  "Please insert a link for the proof!":
                if message.content != f"I'm sorry, but Lady Kanako forbids anyone from doing this command in this channel. Do it in <#{RPchannel_ID}> instead.":
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
                    # If theres 4 or more X reaction
                    if count >= 4:
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







@bot.command()
async def help(ctx):
    if not ctx.channel.id == RPchannel_ID:
        embed=disnake.Embed(title="Commands (Prefix = s!)", color=0x4fe64c)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/988442510026235914/994600993574637689/d74ca0dcdcea3cd99cb9a93bb2a670ff.png")
        embed.add_field(name="/reportbug", value="Report bug (need link as proof", inline=False)
        embed.add_field(name="s!bugs or /bugs", value="View list of bugs sorted from most ✅", inline=False)
        embed.add_field(name="s!delreport or /delreport (only visible for admins)", value="Delete report (argumment has to be the report message ID, find it or look for it in the s!bugs command)", inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"I'm sorry, but Lady Kanako forbids anyone from doing this command in this channel. Do it in <#{RPchannel_ID}> instead.")

@bot.slash_command(description="Isn't it self explanatory")
async def help(inter):
    if not inter.channel.id == RPchannel_ID:
        embed=disnake.Embed(title="Commands (Prefix = s!)", color=0x4fe64c)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/988442510026235914/994600993574637689/d74ca0dcdcea3cd99cb9a93bb2a670ff.png")
        embed.add_field(name="/reportbug", value="Report bug (need link as proof)", inline=False)
        embed.add_field(name="s!bugs or /bugs", value="View list of bugs sorted from most ✅", inline=False)
        embed.add_field(name="s!delreport or /delreport (only visible for admins)", value="Delete report (argumment has to be the report message ID, find it or look for it in the s!bugs command)", inline=True)
        await inter.response.send_message(embed=embed)
    else:
        await inter.response.send_message(f"I'm sorry, but Lady Kanako forbids anyone from doing this command in this channel. Do it in <#{RPchannel_ID}> instead.")







@bot.slash_command(description="Report a bug")
async def reportbug(inter, bug: str, proof: str):
    if inter.channel_id == RPchannel_ID:
        # Get time
        now = datetime.now()
        current_time = now.strftime("%d %b %H:%M:%S")

        # Check if proof is acceptable
        if not validators.url(proof):
            await inter.response.send_message("Please insert a link for the proof!")
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
        await inter.response.send_message(f"I'm sorry, but Lady Kanako forbids anyone from doing this command in this channel. Do it in <#{RPchannel_ID}> instead.")







@bot.command()
async def bugs(ctx):
    # Get channels
    DBchannel = bot.get_channel(DBchannel_ID)
    DBchannel2 = bot.get_channel(DBchannel2_ID)

    # Put DB2 data to array
    DB2data = []
    async for message in DBchannel2.history(limit=None):
        message_data = json.loads(message.content.replace("'", '"'))
        append_data = {"sortby": message_data["reactions"], "data": message_data}
        DB2data.append(append_data)

    # Sort the array
    DB2data_sorted = sorted(DB2data, key=lambda i: i["sortby"], reverse=True)

    #put in array
    embed=disnake.Embed(title="Bug Reports", description="From most reactions to least", color=0x4fe64c)
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/988442510026235914/994600993574637689/d74ca0dcdcea3cd99cb9a93bb2a670ff.png")
    for data in DB2data_sorted:
        dataDB2 = data["data"]
        # get database content from database1
        dataDB1_message = await DBchannel.fetch_message(dataDB2["databaseMSG_ID"])
        dataDB1 = json.loads(dataDB1_message.content.replace("'", '"'))
        # Gather info and boom assemble
        thebug = dataDB1["bug"]
        thereaction = dataDB2["reactions"]
        thetime = dataDB1["time"]
        thereportid = dataDB2["reportMSG_ID"]
        theproof = dataDB1["proof"]
        embed.add_field(name=f"Title: {thebug} ({thereaction} reactions)\nTime reported: {thetime} (GMT+7)", value=f"Report_id: {thereportid}\nProof: {theproof}", inline=False)
    await ctx.send(embed=embed)

@bot.slash_command(description="Get bug reports")
async def bugs(inter):
    if not inter.channel_id == RPchannel_ID:
        # Get channels
        DBchannel = bot.get_channel(DBchannel_ID)
        DBchannel2 = bot.get_channel(DBchannel2_ID)

        # Put DB2 data to array
        DB2data = []
        async for message in DBchannel2.history(limit=None):
            message_data = json.loads(message.content.replace("'", '"'))
            append_data = {"sortby": message_data["reactions"], "data": message_data}
            DB2data.append(append_data)

        # Sort the array
        DB2data_sorted = sorted(DB2data, key=lambda i: i["sortby"], reverse=True)

        #put in array
        embed=disnake.Embed(title="Bug Reports", description="From most reactions to least", color=0x4fe64c)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/988442510026235914/994600993574637689/d74ca0dcdcea3cd99cb9a93bb2a670ff.png")
        for data in DB2data_sorted:
            dataDB2 = data["data"]
            # get database content from database1
            dataDB1_message = await DBchannel.fetch_message(dataDB2["databaseMSG_ID"])
            dataDB1 = json.loads(dataDB1_message.content.replace("'", '"'))
            # Gather info and boom assemble
            thebug = dataDB1["bug"]
            thereaction = dataDB2["reactions"]
            thetime = dataDB1["time"]
            thereportid = dataDB2["reportMSG_ID"]
            theproof = dataDB1["proof"]
            embed.add_field(name=f"Title: {thebug} ({thereaction} reactions)\nTime reported: {thetime} (GMT+7)", value=f"Report_id: {thereportid}\nProof: {theproof}", inline=False)
        await inter.response.send_message(embed=embed)
    else:
        await inter.response.send_message(f"I'm sorry, but Lady Kanako forbids anyone from doing this command in this channel. Do it in <#{RPchannel_ID}> instead.")






@bot.command(pass_context=True, name="delreport")
@commands.has_permissions(administrator=True)
async def delreport(ctx, message=None):
    if not ctx.channel.id == RPchannel_ID:
        if not message == None:
            # Get channels
            RPchannel = bot.get_channel(RPchannel_ID)
            DBchannel = bot.get_channel(DBchannel_ID)
            DBchannel2 = bot.get_channel(DBchannel2_ID)
            
            # Check if the ID is valid
            isExist = False
            async for ID in DBchannel2.history(limit=None):
                dataID = json.loads(ID.content.replace("'", '"'))
                if str(message) == str(dataID["reportMSG_ID"]):
                    isExist = True

            if isExist == False:
                await ctx.send("Please insert the report ID (or bug report message ID)!")
            else:
                # Get info
                async for x in DBchannel2.history(limit=None):
                    data = json.loads(x.content.replace("'", '"'))
                    if str(message) == str(data["reportMSG_ID"]):
                        # DELETE
                        RPmsg = await RPchannel.fetch_message(data["reportMSG_ID"])
                        DBmsg =  await DBchannel.fetch_message(data["databaseMSG_ID"])
                        await RPmsg.delete()
                        await DBmsg.delete()
                        await x.delete()

                        await ctx.send("Done.")
        else:
            await ctx.send("Please insert the report ID (or bug report message ID)!")
    else:
        await ctx.send(f"I'm sorry, but Lady Kanako forbids anyone from doing this command in this channel. Do it in <#{RPchannel_ID}> instead.")

@delreport.error
async def delreport_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send(f"Lady Suwako only allow Admins to use this command.")


@bot.slash_command(description="Delete report", name="delreport")
@commands.default_member_permissions(administrator=True)
async def delreport(inter, id: str):
    # Get channels
    RPchannel = bot.get_channel(RPchannel_ID)
    DBchannel = bot.get_channel(DBchannel_ID)
    DBchannel2 = bot.get_channel(DBchannel2_ID)
    
    # Check if the ID is valid
    isExist = False
    async for ID in DBchannel2.history(limit=None):
        dataID = json.loads(ID.content.replace("'", '"'))
        if str(id) == str(dataID["reportMSG_ID"]):
            isExist = True

    if isExist == False:
        await inter.response.send_message("Please insert the report ID (or bug report message ID)!")
    else:
        # Get info
        async for x in DBchannel2.history(limit=None):
            data = json.loads(x.content.replace("'", '"'))
            if str(id) == str(data["reportMSG_ID"]):
                # DELETE
                RPmsg = await RPchannel.fetch_message(data["reportMSG_ID"])
                DBmsg =  await DBchannel.fetch_message(data["databaseMSG_ID"])
                await RPmsg.delete()
                await DBmsg.delete()
                await x.delete()

                await inter.response.send_message("Done.")

bot.run(token)