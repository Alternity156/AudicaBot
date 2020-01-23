import asyncio
import datetime
import os
import discord
import time
import json
import glob
import queue

from discord.ext import commands
from zipfile import ZipFile
from threading import Thread

from audica_leaderboards import leaderboards_api, friend_codes, user_list
from custom_embeds import make_leaderboards_embed, make_leaderboards_help_embed, make_songid_embed, make_helplinks_embed, make_top20_autoupdate_embed, make_myscores_embed, make_compare_embed, make_twitch_embed, make_compare_mps_embed
from tools import parse_leaderboards_args, message_logger, customs_database, custom_song, unknown_leaderboard_ids

global running

running = False

api = None

bot_owner_id = 296722207059738626 # My Discord ID

client = commands.Bot(command_prefix=".")
client.owner_id = bot_owner_id

servers_to_operate = ["Audica Modding Group", "Test"]
test_server = ["Test"]

async def cache_song_leaderboard(song, current_page=1):
        
    stop_running = False

    if not os.path.exists(api.leaderboards_cache_folder + os.sep + song):
        os.makedirs(api.leaderboards_cache_folder + os.sep + song)
        
    starting_page = current_page
    total_pages = current_page

    while(stop_running == False):
        req = api.request_song_leaderboard(song, page=str(current_page))
        if req == False:
            print("Error requesting page " + str(current_page) + " of " + str(total_pages) + " for the song " + song)
        else:
            reqjson = json.loads(req)
            total_pages = reqjson["leaderboard"]["total_pages"]
            if req == "page does not exist":
                stop_running = True
            else:
                f = open(api.leaderboards_cache_folder + os.sep + song + os.sep + str(current_page) + ".json", "w")
                f.write(req)
                f.close()
                if total_pages == 0:
                    current_page = 0
                    api.update_state(song, current_page, total_pages, start_time=True, custom=True)
                if current_page == 1:
                    api.update_state(song, current_page, total_pages, start_time=True, custom=True)
                    if total_pages == current_page:
                        api.update_state(song, current_page, total_pages, finish_time=True, custom=True)
                elif total_pages == current_page:
                    api.update_state(song, current_page, total_pages, finish_time=True, custom=True)
                else:
                    api.update_state(song, current_page, total_pages, custom=True)
            if current_page == total_pages:
                stop_running = True
                message_logger("CUSTOMS LEADERBOARDS", "[SONG \"" + song[:-33] + "\"] Page "+ str(current_page) + " of " + str(total_pages) + " saved. " + \
                                str(api.requests_left) + " of " + str(api.requests_per_hour) + " requests left.")
                message_logger("CUSTOMS LEADERBOARDS", "[SONG \"" + song[:-33] + "\"] Song cache saving and user data update is starting.")
                wait_time = api.find_optimal_wait_time(minimum_time=api.seconds_per_requests_customs)
                await asyncio.sleep(wait_time)
                return api.save_song_cache_to_database(song, custom=True)
            elif current_page == 0:
                stop_running = True
                message_logger("CUSTOMS LEADERBOARDS", "[SONG \"" + song[:-33] + "\"] This leaderboard has 0 pages.")
        if stop_running == False:
            message_logger("CUSTOMS LEADERBOARDS", "[SONG \"" + song[:-33] + "\"] Page "+ str(current_page) + " of " + str(total_pages) + " saved. " + \
                           str(api.requests_left) + " of " + str(api.requests_per_hour) + " requests left.")
        if api.loop_running == False:
            stop_running = True
        current_page = current_page + 1
        wait_time = api.find_optimal_wait_time(minimum_time=api.seconds_per_requests_customs)
        await asyncio.sleep(wait_time)

async def customs_leaderboards_update():
    async def process_scores(song, scores):
        old_scores = scores[0]
        new_scores = scores[1]
        if old_scores == []:
            return
        else:
            temp_old_scores = []
            temp_new_scores = []
            for score in old_scores:
                temp = score
                temp["timestamp"] = 0
                temp_old_scores.append(temp)
            for score in new_scores:
                temp = score
                temp["timestamp"] = 0
                temp_new_scores.append(temp)
            count = 0
            if temp_old_scores != temp_new_scores:
                message_logger("CUSTOMS LEADERBOARDS", "[SONG \"" + song[0] + "\"] Found new scores.")
                for channel in client.get_all_channels():
                    if str(channel) == "leaderboards":
                        if str(channel.guild) in servers_to_operate:
                            if temp_new_scores == []:
                                await channel.send(content="Scores were wiped for " + song + " and this leaderboard is currently empty.")
                            else:
                                embed = make_top20_autoupdate_embed(song[0], temp_old_scores, temp_new_scores, custom=True, api=api)
                                await channel.send(embed=embed)
            else:
                message_logger("CUSTOMS LEADERBOARDS", "[SONG \"" + song[0] + "\"] No new scores.")
    global running
    running = True
    api.load_custom_songs()
    state = []
    state_file = api.leaderboards_cache_folder + os.sep + "state_customs.json"
    if os.path.isfile(state_file):
        f = open(state_file, "r")
        state = json.load(f)
        f.close()
        for song in api.customs:
            if song[1] != "":
                if "." not in song[1]:
                    song_found = False
                    for item in state:
                        if item["song"] == song[1]:
                            song_found = True
                            break
                    if song_found == False:
                        try:
                            scores = await cache_song_leaderboard(song[1])
                            await process_scores(song, scores)
                        except Exception as e:
                            print("Error processing custom song leaderboards for " + song[0])
                            print(e)
    else:
        for song in api.customs:
            if song[1] != "":
                try:
                    scores = await cache_song_leaderboard(song[1])
                    await process_scores(song, scores)
                    f = open(state_file, "r")
                    state = json.load(f)
                    f.close()
                except Exception as e:
                    print("Error processing custom song leaderboards for " + song[0])
                    print(e)
    for item in state:
        if item["update_finished"] == 0:
            try:
                scores = await cache_song_leaderboard(item["song"], current_page=item["current_page"] + 1)
                await process_scores(song, scores)
            except Exception as e:
                print("Error processing custom song leaderboards for " + item["song"])
                print(e)
    f = open(state_file, "r")
    state = json.load(f)
    f.close()
    lowest_time = time.time()
    song_to_update = ""
    for item in state:
        if item["update_finished"] < lowest_time:
            song_to_update = item["song"]
            lowest_time = item["update_start"]
    try:
        # que = queue.Queue()
        # t = Thread(target=api.cache_song_leaderboard, args=(song_to_update, que), kwargs={"custom": True})
        # t.start()
        # t.join()
        # scores = que.get()
        for s in api.customs:
            if s[1] == song_to_update:
                song = s
                break
        scores = await cache_song_leaderboard(song_to_update)
        await process_scores(song, scores)
    except Exception as e:
        print("Error processing custom song leaderboards for " + song[0])
        print(e)
    asyncio.ensure_future(customs_leaderboards_update())
    
@client.event
async def on_message(m):
    pass
   
@client.event
async def on_ready():
    global running
    message_logger("CUSTOMS LEADERBOARDS", "Connected to Discord.")
    if running == False:
        message_logger("CUSTOMS LEADERBOARDS", "Starting the loop...")
        asyncio.ensure_future(customs_leaderboards_update())