import asyncio
import datetime
import os
import discord
import time
import json
import glob

from discord.ext import commands

from custom_embeds import make_mixer_embed
from tools import message_logger
from mixer_api import mixer_api

global running 

running = False

bot_owner_id = 296722207059738626 # My Discord ID

client = commands.Bot(command_prefix=".")
client.owner_id = bot_owner_id

servers_to_operate = ["Audica Modding Group", "Test"]
test_server = ["Test"]

approved_emoji = "\U00002705"
offline_emoji = "\U0001F6D1"
    
async def audica_mixer_streams_loop():
    global running
    running = True
    all_channels = client.get_all_channels()
    try:
        ttv_api = mixer_api()
        new_streams = ttv_api.update_live_streams()
        all_streams = ttv_api.live_streams
        if new_streams != []:
            for channel in all_channels:
                if str(channel) == "audica-streams":
                    if str(channel.guild) in servers_to_operate:
                        for stream in new_streams:
                            await channel.send(embed=make_mixer_embed(stream))
        for channel in all_channels:
            if str(channel) == "audica-streams":
                async for message in (channel.history(limit=10)):
                    #print(message)
                    if message.author.id == client.user.id:
                        try:
                            streamer_name = message.embeds[0].author.name
                            streamer_found = False
                            for stream in all_streams:
                                if "Mixer" == str(message.embeds[0].title.split(" ")[1]):
                                    if streamer_name == stream["user"]["username"]:
                                        streamer_found = True
                            if "Mixer" == str(message.embeds[0].title.split(" ")[1]):
                                if streamer_found == False:
                                    await message.add_reaction(offline_emoji)
                        except Exception as e:
                            print(e)
        log_string = "New live streams: "
        for stream in new_streams:
            log_string = log_string + "\"" + stream["user"]["username"] + "\" "
        if new_streams != []:
            message_logger("mixer LOOP", log_string)
        else:
            message_logger("mixer LOOP", "No new Audica streams.")
        await asyncio.sleep(150)
    except Exception as e:
        message_logger("mixer LOOP", "Loop crashed, printing error on next line and restarting in 30 seconds...")
        message_logger("mixer LOOP", str(e))
        await asyncio.sleep(150)
    asyncio.ensure_future(audica_mixer_streams_loop())
    
@client.event
async def on_message(m):
    pass
   
@client.event
async def on_ready():
    global running
    message_logger("mixer LOOP", "Connected to Discord.")
    if running == False:
        message_logger("mixer LOOP", "Starting the loop...")
        asyncio.ensure_future(audica_mixer_streams_loop())
    