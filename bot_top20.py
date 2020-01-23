import asyncio
import datetime
import os
import discord
import time
import json
import glob

from discord.ext import commands
from zipfile import ZipFile
from threading import Thread

from audica_leaderboards import leaderboards_api, friend_codes, user_list
from custom_embeds import make_leaderboards_embed, make_leaderboards_help_embed, make_songid_embed, make_helplinks_embed, make_top20_autoupdate_embed, make_myscores_embed, make_compare_embed, make_twitch_embed, make_compare_mps_embed
from tools import parse_leaderboards_args, message_logger, customs_database, custom_song, unknown_leaderboard_ids
from twitch_api import twitch_api

global running

running = False

api = None

bot_owner_id = 296722207059738626 # My Discord ID

client = commands.Bot(command_prefix=".")
client.owner_id = bot_owner_id

servers_to_operate = ["Audica Modding Group", "Test"]
channel_to_operate = "leaderboards-top20"
channel_extra_songs = "leaderboards"
test_server = ["Test"]

## Audica folders
audica_folder = "AUDICA"
audica_custom_songs_folder = audica_folder + os.sep + "CUSTOMS"
audica_ost_folder = audica_folder + os.sep + "OST"

async def audica_top20_update_loop():
    global running
    running = True
    message_logger("TOP20 UPDATE LOOP", "Loop started.")
    try:
        def save_json(filename, rjson):
            f = open(filename, "w")
            json.dump(rjson, f, sort_keys=True, indent=4)
            f.close()
        try:
            for song in api.ost:
                if song != "all_time_leaders" and song != "all_time_totals":
                    request = api.request_song_leaderboard(song, platform="global", difficulty="all", page="1", page_size="20")
                    rjson = json.loads(request)
                    filename = api.leaderboards_cache_folder + os.sep + song + "top20.json"
                    if os.path.isfile(filename):
                        f = open(filename, "r")
                        fjson = json.load(f)
                        f.close()
                        old_scores = fjson
                        new_scores = []
                        for item in rjson["leaderboard"]["data"]:
                            item = item[0]
                            new_scores.append(item)
                        if old_scores != new_scores:
                            message_logger("TOP20 UPDATE LOOP", "[SONG \"" + song + "\"] Found new scores.")
                            channel_to_post = ""
                            if song in api.global_songs:
                                channel_to_post = channel_to_operate
                            else:
                                channel_to_post = channel_extra_songs
                            for channel in client.get_all_channels():
                                if str(channel) == channel_to_post:
                                    if str(channel.guild) in servers_to_operate:
                                        if new_scores == []:
                                            await channel.send(content="Scores were wiped for " + song + " and this leaderboard is currently empty.")
                                        else:
                                            await channel.send(embed=make_top20_autoupdate_embed(song, old_scores, new_scores))
                            save_json(filename, new_scores)
                        else:
                            message_logger("TOP20 UPDATE LOOP", "[SONG \"" + song + "\"] No new scores.")
                    else:
                        message_logger("TOP20 UPDATE LOOP", "[SONG \"" + song + "\"] Leaderboards not found, saving current data...")
                        data = []
                        for item in rjson["leaderboard"]["data"]:
                            item = item[0]
                            data.append(item)
                        save_json(filename, data)
                    await asyncio.sleep(api.find_optimal_wait_time(minimum_time=(300.0/len(api.ost) + 1)-1))
        except Exception as e:
            print("problem top20-1")
            print(e)
            await asyncio.sleep(api.find_optimal_wait_time(minimum_time=(300.0/len(api.ost) + 1)-1))
        try:
            request = api.request_song_leaderboard("all_time_leaders", page_size="20")
            #request = api.request_all_time_leaders()
            rjson = json.loads(request)
            filename = api.leaderboards_cache_folder + os.sep + "globaltop20.json"
            song = "global"
            if os.path.isfile(filename):
                f = open(filename, "r")
                fjson = json.load(f)
                f.close()
                old_scores = fjson
                new_scores = []
                for item in rjson["leaderboard"]["data"]:
                    item = item[0]
                    new_scores.append(item)
                if old_scores != new_scores:
                    message_logger("TOP20 UPDATE LOOP", "[SONG \"" + song + "\"] Found new scores.")
                    for channel in client.get_all_channels():
                        if str(channel) == channel_to_operate:
                            if str(channel.guild) in servers_to_operate:
                                if new_scores == []:
                                    await channel.send(content="Scores were wiped for " + song + " and this leaderboard is currently empty.")
                                else:
                                    await channel.send(embed=make_top20_autoupdate_embed(song, old_scores, new_scores))
                    save_json(filename, new_scores)
                else:
                    message_logger("TOP20 UPDATE LOOP", "[SONG \"" + song + "\"] No new scores.")
            else:
                message_logger("TOP20 UPDATE LOOP", "[SONG \"" + song + "\"] Leaderboards not found, saving current data...")
                data = []
                for item in rjson["leaderboard"]["data"]:
                    item = item[0]
                    data.append(item)
                save_json(filename, data)
            await asyncio.sleep(api.find_optimal_wait_time(minimum_time=(300.0/len(api.ost))))
        except Exception as e:
            print("problem top20-2")
            print(e)
            await asyncio.sleep(api.find_optimal_wait_time(minimum_time=(300.0/len(api.ost))))
        message_logger("TOP20 UPDATE LOOP", "Loop finished, going back to first song...")
    except Exception as e:
        message_logger("TOP20 UPDATE LOOP", "Loop crashed, should restart in 30 seconds...")
        print(e)
        await asyncio.sleep(30)
    top20_update_running = False
    client.loop.create_task(audica_top20_update_loop())
    
@client.event
async def on_message(m):
    pass
    
@client.event
async def on_ready():
    global running
    message_logger("TOP20 UPDATE BOT", "Connected to Discord.")
    if running == False:
        message_logger("TOP20 UPDATE BOT", "Starting update loop...")
        await audica_top20_update_loop()