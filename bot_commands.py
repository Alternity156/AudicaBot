import asyncio
import datetime
import os
import discord
import time
import json
import glob

from discord.ext import commands
from zipfile import ZipFile

from audica_leaderboards import leaderboards_api, friend_codes, user_list
from custom_embeds import make_leaderboards_embed, make_leaderboards_help_embed, make_songid_embed, make_helplinks_embed, make_top20_autoupdate_embed, make_myscores_embed, make_compare_embed, make_compare_mps_embed
from tools import parse_leaderboards_args, message_logger, customs_database, custom_song, unknown_leaderboard_ids

api = None

bot_owner_id = 296722207059738626 # My Discord ID

client = commands.Bot(command_prefix=".")
client.owner_id = bot_owner_id

servers_to_operate = ["Audica Modding Group", "Test"]
channel_to_operate = "leaderboards"
top20_channel = "leaderboards-top20"
test_server = ["Test"]

leaderboards_command_cooldown = 5
songidlist_command_cooldown = 30
helplinks_command_cooldown = 30
myscores_command_cooldown = 10
compare_command_cooldown = 10
rename_command_cooldown = 5
edit_leaderboard_cooldown = 10
delete_custom_command_cooldown = 60

cooldown_emoji = '\U0001F504'
approved_emoji = "\U00002705"
rejected_emoji = "\U0000274C"

## Audica folders
audica_folder = "AUDICA"
audica_custom_songs_folder = audica_folder + os.sep + "CUSTOMS"
audica_ost_folder = audica_folder + os.sep + "OST"

if not os.path.exists(audica_folder):
    os.makedirs(audica_folder)
    
async def process_custom_song(message):
    database = customs_database()
    database.load()
    for attachment in message.attachments:
        if str(attachment.url)[-7:] == ".audica":
            filename = str(attachment.url).split(os.sep)[-1]
            file_path = audica_custom_songs_folder + os.sep + filename
            try:
                found = False
                for song in database.song_list:
                    if song["filename"] == filename:
                        found = True
                if found == False:
                    if os.path.isfile(file_path) == False:
                        message_logger("CUSTOMS DATABASE", "Downloading " + filename + "...")
                        await attachment.save(file_path)
                        message_logger("CUSTOMS DATABASE", "Download finished!")
                        song = custom_song(file_path)
                        song.filename = filename
                        song.uploader = message.author.id
                        song.download_url = str(attachment.url)
                        song.upload_time = str(message.created_at)
                        m = message.content
                        if "\n" in m:
                            for line in m.split("\n"):
                                if "video:" in line.lower():
                                    song.video_url = line.split("o:")[-1].replace(" ", "")
                                if song.desc_file.author == "" and "mapper:" in line.lower():
                                    song.desc_file.author = line.split(":")[-1].replace(" ", "")
                                if "leaderboard:" in line.lower():
                                    song.leaderboard_id = line.split(":")[-1].replace(" ", "")
                        else:
                            if "video:" in m.lower():
                                song.video_url = m.split("o:")[-1].replace(" ", "")
                            if song.desc_file.author == "" and "mapper:" in m.lower():
                                song.desc_file.author = m.split(":")[-1].replace(" ", "")
                            if "leaderboard:" in m.lower():
                                song.leaderboard_id = m.split(":")[-1].replace(" ", "")
                        if database.add(song.get_song_data()) == False:
                            await message.author.send(content="A file named \"" + filename + "\" already exists in the database. The song was not added to the database.")
                            os.remove(file_path)
                            await message.add_reaction(rejected_emoji)
                        database.save()
                        message_logger("CUSTOMS DATABASE", "Added \"" + song.desc_file.artist + " - " + song.desc_file.title + "\" authored by \"" + song.desc_file.author + "\"")
                        await message.add_reaction(approved_emoji)
                    else:
                        await message.author.send(content="A file named \"" + filename + "\" already exists in the database. The song was not added to the database.")
                        await message.add_reaction(rejected_emoji)
                else:
                    await message.author.send(content="A file named \"" + filename + "\" already exists in the database. The song was not added to the database.")
                    await message.add_reaction(rejected_emoji)
            except Exception as e:
                os.remove(file_path)
                await message.author.send(content="There was a problem processing the file \"" + filename + "\".")
                await message.add_reaction(rejected_emoji)
                print(e)
        else:
            await message.author.send(content="This channel is exclusively reserved to post audica files of finished songs.")
            await message.add_reaction(rejected_emoji)
                
async def scan_all_finished_songs():
    message_logger("FUNCTION", "Scanning all Audica custom songs from #finished-songs")
    messages = []
    async for message in (channel.history(limit=10000)):
        #timestamp = message.created_at
        #attachments = message.attachments
        #content = message.content
        #author = message.author
        if len(message.attachments) > 0:
            for attachment in message.attachments:
                if str(attachment.url)[-7:] == ".audica":
                    filename = str(attachment.url).split(os.sep)[-1]
                    message_logger("DOWNLOAD", "Downloading " + filename + "...")
                    await attachment.save(audica_folder + os.sep + filename)
                    message_logger("DOWNLOAD", "Download finished!")
                    messages.append(message)
                    break
    #print(messages)
    message_logger("FUNCTION", "Finished scanning Audica custom songs")

async def cooldown_reaction(m, wait_time):
    await m.add_reaction(cooldown_emoji)
    await asyncio.sleep(wait_time)
    await m.remove_reaction(cooldown_emoji, m.author)
    
async def add_friend_code(m):
    codes = friend_codes()
    codes.load()
    friend_code = m.content.split(" ")[1].replace(">", "")
    user_id = m.author.id
    found = False
    identical = False
    for code in codes.friend_codes["friend_codes"]:
        if code["discord_id"] == user_id:
            found = True
            if code["friend_code"] == friend_code:
                identical = True
    if identical == False:
        if found == True:
            codes.delete(friend_code, user_id)
        codes.add(friend_code, user_id)
        codes.save()
        return True
    return False
    
async def process_play_history_or_log(message):
    for attachment in message.attachments:
        id_list = []
        ids_edited = []
        ids_unknown = []
        if "play_history.json" in str(attachment.url):
            filename = str(attachment.url).split(os.sep)[-1]
            message_logger("CUSTOMS DATABASE", "Downloading " + filename + "...")
            await attachment.save(filename)
            message_logger("CUSTOMS DATABASE", "Download finished!")
            f = open(filename, "r")
            fjson = json.load(f)
            f.close()
            os.remove(filename)
            for item in fjson["songs"]:
                id = item["songID"]
                newest_play = 0
                for history in item["history"]:
                    if history["date"] >= 637085800000000000:
                        if history["date"] > newest_play:
                            newest_play = history["date"]
                id_list.append([id, newest_play])
            id_list_copy = id_list
            new_id_list = []
            for item in id_list:
                newest_play = 0
                id = ""
                for i in id_list_copy:
                    if item[0][:-33] == i[0][:-33]:
                        t = int(str(i[1] - 621357696000000000)[:-7])
                        if t > newest_play:
                            newest_play = t
                            id = i[0]
                new_data = [id, newest_play]
                if new_data not in new_id_list:
                    if new_data[0][:-33] != "":
                        new_id_list.append(new_data)
            id_list = new_id_list
        elif "output_log.txt" in str(attachment.url):
            filename = str(attachment.url).split(os.sep)[-1]
            message_logger("CUSTOMS DATABASE", "Downloading " + filename + "...")
            await attachment.save(filename)
            message_logger("CUSTOMS DATABASE", "Download finished!")
            lines = []
            f = open(filename, "r")
            for line in f:
                lines.append(line)
            f.close()
            os.remove(filename)
            for line in lines:
                if "Requesting leaderboard for " in line:
                    id = line.replace("Requesting leaderboard for ", "").replace("\n", "")
                    if id[:-33] != "":
                        id_found = False
                        for i in id_list:
                            if id == i[0]:
                                id_found = True
                                break
                        if id_found == False:
                            id_list.append([id, time.time()])
        if id_list != []:
            unknown_ids = []
            database = customs_database()
            database.load()
            unknown_database = unknown_leaderboard_ids()
            unknown_database.load()
            for id in id_list:
                song_found = False
                for song in database.song_list:
                    song_id = song["filename"].replace(".audica", "")
                    leaderboard_id = song["leaderboard_id"]
                    if song_id == id[0][:-33]:
                        song_found = True
                        if leaderboard_id == "":
                            database.edit_leaderboard_id(song["song_id"], id[0])
                            ids_edited.append(id[0])
                        break
                if song_found == False:
                    id_found = False
                    for item in unknown_database.leaderboard_ids:
                        if item["leaderboard_id"] == id[0]:
                            id_found = True
                            break
                    if id_found == False:
                        unknown_database.add(id[0], id[1])
                        ids_unknown.append(id[0])
            database.save()
            unknown_database.save()
        message_string = ""
        if ids_edited != []:
            message_string = "Songs that needed an ID from the file provided:\n\n"
            for item in ids_edited:
                message_string = message_string + item + "\n"
            message_string = message_string + "\n"
        if ids_unknown != []:
            message_string = message_string + "IDs that are unknown (songs not in database) that were saved for future use:\n\n"
            for item in ids_unknown:
                message_string = message_string + item + "\n"
        if message_string != "":
            await message.channel.send(content=message_string)
        else:
            if "play_history.json" in str(attachment.url):
                await message.channel.send(content="This file does not contain new IDs.")
            if "output_log.txt" in str(attachment.url):
                await message.channel.send(content="This file does not contain new IDs.")
    
@client.event
async def on_message(m):
    if str(m.guild) in servers_to_operate:
        if str(m.channel) == "finished-songs":
            if len(m.attachments) > 0:
                processed_messages = []
                try:
                    f = open("finished-songs-processed-messages.txt", "r")
                    for line in f:
                        processed_messages.append(line.replace("\n", ""))
                    f.close()
                except:
                    print("finished-songs-processed-messages.txt does not exist")
                if str(m.id) not in processed_messages:
                    await process_custom_song(m)
                    processed_messages.append(str(m.id))
                f = open("finished-songs-processed-messages.txt", "w")
                for line in processed_messages:
                    f.write(line + "\n")
                f.close()
            else:
                await m.author.send(content="This channel is exclusively reserved to post audica files of finished songs.")
        if str(m.channel) == "audica-friend-codes":
            if "<audica_friend_code " in m.content:
                result = await add_friend_code(m)
                if result == True:
                    await m.add_reaction(approved_emoji)
        if str(m.channel) == "leaderboards":
            if len(m.attachments) > 0:
                await process_play_history_or_log(m)
    #if str(m.channel.type) == "private":
        #print(m.content)
    await client.process_commands(m)
    
@client.event
async def on_ready():
    message_logger("COMMANDS BOT", "Connected to Discord.")
    message_logger("COMMANDS BOT", "Ready to execute commands.")
    for channel in client.get_all_channels():
        if str(channel.guild) in servers_to_operate:
            if str(channel) == "audica-friend-codes":
                async for message in (channel.history(limit=10000)):
                    if "<audica_friend_code " in message.content:
                        result = await add_friend_code(message)
                        if result == True:
                            await message.add_reaction(approved_emoji)
                            await asyncio.sleep(0.25)
            elif str(channel) == "finished-songs":
                async for message in (channel.history(limit=10000)):
                    if len(message.attachments) > 0:
                        processed_messages = []
                        try:
                            f = open("finished-songs-processed-messages.txt", "r")
                            for line in f:
                                processed_messages.append(line.replace("\n", ""))
                            f.close()
                        except:
                            print("finished-songs-processed-messages.txt does not exist")
                        if str(message.id) not in processed_messages:
                            await process_custom_song(message)
                            processed_messages.append(str(message.id))
                        f = open("finished-songs-processed-messages.txt", "w")
                        for line in processed_messages:
                            f.write(line + "\n")
                        f.close()
            
@client.command()
async def test(ctx):
    if str(ctx.guild) in test_server:
        print(await client.is_owner(ctx.message.author))
        await ctx.send(content=rejected_emoji)
        
@client.command()
@commands.cooldown(1, rename_command_cooldown, commands.BucketType.user)
async def wipeleaderboardids(ctx):
    if await client.is_owner(ctx.message.author):
        database = customs_database()
        database.load()
        database.wipe_leaderboard_ids()
        database.save()
        await ctx.send(content="Wiped all leaderboard IDs for custom songs.")
        
@client.command()
@commands.cooldown(1, rename_command_cooldown, commands.BucketType.user)
async def rename(ctx, name):
    if await client.is_owner(ctx.message.author):
        await client.user.edit(username=name)
        
@client.command()
@commands.cooldown(1, rename_command_cooldown, commands.BucketType.user)
async def update_avatar(ctx):
    if await client.is_owner(ctx.message.author):
        with open("avatar.png", "rb") as f:
            await client.user.edit(avatar=f.read())
            
@client.command()
@commands.cooldown(1, delete_custom_command_cooldown, commands.BucketType.user)
async def delete_song(ctx, *args):
    user_id = ctx.author.id
    sender = ctx.message.author
    database = customs_database()
    database.load()
    found = False
    message_logger("COMMAND", ".delete_song command requested by " + sender.display_name)
    for song in database.song_list:
        if song["filename"] == args[0] or song["song_id"] == args[0]:
            found = True
            if user_id == song["uploader"] or await client.is_owner(ctx.author):
                database.delete(song["song_id"])
                database.save()
                os.remove(audica_custom_songs_folder + os.sep + song["filename"])
                await ctx.send(content="`" + song["song_id"] + "` successfully deleted.")
                message_logger("COMMAND", song["song_id"] + "deleted.")
            else:
                await ctx.send(content="You do not have permission to delete `" + song["song_id"] + "`.")
                message_logger("COMMAND", "Does not have permission to delete.")
            break
    if found == False:
        await ctx.send(content="Did not find a song with `" + args[0] + "` as either song_id or filename. Please specify the exact filename or song_id of the song to delete.")
        message_logger("COMMAND", "Song not found.")
            
@client.command()
@commands.cooldown(1, helplinks_command_cooldown, commands.BucketType.user)
async def helplinks(ctx):
    if str(ctx.guild) in servers_to_operate:
        sender = ctx.message.author
        message_logger("COMMAND", ".helplinks command requested by " + sender.display_name)
        m = await ctx.send(embed=make_helplinks_embed(sender))
        client.loop.create_task(cooldown_reaction(m, helplinks_command_cooldown))
            
@client.command()
@commands.cooldown(1, songidlist_command_cooldown, commands.BucketType.user)            
async def songidlist(ctx):
    if str(ctx.guild) in servers_to_operate:
        sender = ctx.message.author
        message_logger("COMMAND", ".songidlist command requested by " + sender.display_name)
        m = await ctx.send(embed=make_songid_embed(sender))
        client.loop.create_task(cooldown_reaction(m, songidlist_command_cooldown))
        
@client.command()
@commands.cooldown(1, edit_leaderboard_cooldown, commands.BucketType.user)
async def missing_leaderboards(ctx):
    async def do_work():
        await ctx.channel.trigger_typing()
        sender = ctx.message.author
        message_logger("COMMAND", ".missing_leaderboards command requested by " + sender.display_name)
        database = customs_database()
        database.load()
        songs = []
        for song in database.song_list:
            if song["leaderboard_id"] == "":
                songs.append(song["filename"].replace(".audica", ""))
        message_string = "Filename of songs with missing leaderboard ID:\n\n"
        for song in songs:
            message_string = message_string + song + "\n"
        m = await ctx.send(content=message_string)
        client.loop.create_task(cooldown_reaction(m, edit_leaderboard_cooldown))
    if str(ctx.guild) in  servers_to_operate:
        if str(ctx.channel) == "leaderboards":
            await do_work()
        else:
            for channel in ctx.guild.channels:
                if str(channel) == "leaderboards":
                    m = await ctx.send(content="This command only works in " + channel.mention)
                    client.loop.create_task(cooldown_reaction(m, edit_leaderboard_cooldown))
    elif ctx.channel.type == discord.ChannelType.private:
        await do_work()
        
@client.command()        
@commands.cooldown(1, edit_leaderboard_cooldown, commands.BucketType.user)
async def edit_leaderboard(ctx, *args):
    async def do_work():
        await ctx.channel.trigger_typing()
        sender = ctx.message.author
        message_logger("COMMAND", ".edit_leaderboard command requested by " + sender.display_name)
        filename = args[0] + ".audica"
        leaderboard_id = args[1]
        database = customs_database()
        database.load()
        song = database.get_song_with_filename(filename)
        song_filename = song["filename"].replace(".audica", "")
        if song == False:
            m = await ctx.send(content="Could not find the song_id in the database.")
        else:
            try:
                hash = leaderboard_id.replace(song_filename + "_", "")
            except:
                hash = leaderboard_id
            if len(hash) != 32:
                m = await ctx.send(content="Invalid leaderboard hash.")
            else:
                if len(leaderboard_id) == 32:
                    leaderboard_id = song_filename + "_" + hash
                database.edit_leaderboard_id(song_filename, leaderboard_id)
                database.save()
                m = await ctx.send(content="Song with ID \"" + song_filename + "\" was successfully edited with the leaderboard hash \"" + hash + "\".")
        client.loop.create_task(cooldown_reaction(m, edit_leaderboard_cooldown))
    if str(ctx.guild) in  servers_to_operate:
        if str(ctx.channel) == "leaderboards":
            await do_work()
        else:
            for channel in ctx.guild.channels:
                if str(channel) == "leaderboards":
                    m = await ctx.send(content="This command only works in " + channel.mention)
                    client.loop.create_task(cooldown_reaction(m, edit_leaderboard_cooldown))
    elif ctx.channel.type == discord.ChannelType.private:
        await do_work()
        
@client.command()
@commands.cooldown(1, compare_command_cooldown, commands.BucketType.user)
async def compare_max(ctx):
    async def do_work():
        await ctx.channel.trigger_typing()
        sender = ctx.message.author
        message_logger("COMMAND", ".compare command requested by " + sender.display_name)
        users = user_list()
        codes = friend_codes()
        users.load()
        codes.load()
        user = codes.get_code(sender.id)
        if user == None:
            message_logger("COMMAND", "Help message sent, error with arguments")
            for channel in ctx.guild.channels:
                if str(channel) == "audica-friend-codes":
                    m = await ctx.send(content="Friend code not found. To link your friend code post it in " + channel.mention + ".")
        else:
            try:
                request = api.post_request(api.global_songs, [user])
                pages = []
                page = []
                all_songs = []
                count = 0
                ammount = 0
                for i in request["leaderboard"]:
                    if i["data"] != []:
                        ammount = ammount + 1
                for p in request["leaderboard"]:
                    if p["data"] != []:
                        page.append(p)
                        count = count + 1
                        if count == 20 or count == 40 or count == ammount:
                            pages.append(page)
                            page = []
                m = None
                for page in pages:
                    #print(page)
                    m = await ctx.send(embed=make_compare_mps_embed(page, user, sender, api))
            except Exception as e:
                print(e)
                m = await ctx.send(content="Unexpected error with the command.")
        client.loop.create_task(cooldown_reaction(m, compare_command_cooldown))
    if str(ctx.guild) in  servers_to_operate:
        if str(ctx.channel) == "leaderboards":
            await do_work()
        else:
            for channel in ctx.guild.channels:
                if str(channel) == "leaderboards":
                    m = await ctx.send(content="This command only works in " + channel.mention)
                    client.loop.create_task(cooldown_reaction(m, compare_command_cooldown))
    elif ctx.channel.type == discord.ChannelType.private:
        await do_work()
        
@client.command()
@commands.cooldown(1, compare_command_cooldown, commands.BucketType.user)
async def compare(ctx, *args):
    async def do_work():
        await ctx.channel.trigger_typing()
        sender = ctx.message.author
        message_logger("COMMAND", ".compare command requested by " + sender.display_name)
        users = user_list()
        codes = friend_codes()
        users.load()
        codes.load()
        user1 = codes.get_code(sender.id)
        user2 = None
        if user1 == None:
            message_logger("COMMAND", "Help message sent, error with arguments")
            for channel in ctx.guild.channels:
                if str(channel) == "audica-friend-codes":
                    m = await ctx.send(content="Friend code not found. To link your friend code post it in " + channel.mention + ".")
        else:
            if "<audica_friend_code" in args[0]:
                if " " in args[0]:
                    user2 = args[0].replace("<audica_friend_code ", "").replace(">", "")
                else:
                    user2 = args[1].replace(">", "")
            elif "steam" in args[0] or "viveport" in args[0] or "oculus" in args[0]:
                user2 = args[0]
            else:
                for user in users.users["users"]:
                    if args[0] == user["name"]:
                        user2 = user["platform_id"]
                        break
                if user2 == None:
                    for user in users.users["users"]:
                        if args[0].lower() == user["name"].lower():
                            user2 = user["platform_id"]
                            break
                if user2 == None:
                    for user in users.users["users"]:
                        if args[0] in user["name"]:
                            user2 = user["platform_id"]
                            break
                if user2 == None:
                    for user in users.users["users"]:
                        if args[0].lower() in user["name"].lower():
                            user2 = user["platform_id"]
                            break
            if user2 == None:
                m = await ctx.send(content="User to compare with not found. This command needs either a part or the totality of the in-game name, the friend code or the platform id of the player to compare with.")
            else:
                try:
                    request = api.post_request(api.global_songs, [user1, user2])
                    pages = []
                    page = []
                    all_songs = []
                    count = 0
                    ammount = 0
                    for i in request["leaderboard"]:
                        if i["data"] != []:
                            ammount = ammount + 1
                    for p in request["leaderboard"]:
                        if p["data"] != []:
                            page.append(p)
                            count = count + 1
                            if count == 20 or count == 40 or count == ammount:
                                pages.append(page)
                                page = []
                    m = None
                    for page in pages:
                        #print(page)
                        m = await ctx.send(embed=make_compare_embed(page, user1, user2, users.get_name(user1), users.get_name(user2), sender, api))
                except:
                    m = await ctx.send(content="Unexpected error with the command.")
        client.loop.create_task(cooldown_reaction(m, compare_command_cooldown))
    if str(ctx.guild) in  servers_to_operate:
        if str(ctx.channel) == "leaderboards":
            await do_work()
        else:
            for channel in ctx.guild.channels:
                if str(channel) == "leaderboards":
                    m = await ctx.send(content="This command only works in " + channel.mention)
                    client.loop.create_task(cooldown_reaction(m, compare_command_cooldown))
    elif ctx.channel.type == discord.ChannelType.private:
        await do_work()
        
@client.command()
@commands.cooldown(1, myscores_command_cooldown, commands.BucketType.user)
async def myscores(ctx):
    async def do_work():
        await ctx.channel.trigger_typing()
        sender = ctx.message.author
        message_logger("COMMAND", ".myscores command requested by " + sender.display_name)
        if ctx.message.content == ".myscores":
            codes = friend_codes()
            codes.load()
            code = codes.get_code(ctx.author.id)
            if code == None:
                message_logger("COMMAND", "Help message sent, error with arguments")
                for channel in ctx.guild.channels:
                    if str(channel) == "audica-friend-codes":
                        m = await ctx.send(content="Friend code not found. To link your friend code post it in " + channel.mention + ".")
                        client.loop.create_task(cooldown_reaction(m, myscores_command_cooldown))
            else:
                request = api.post_request(api.global_songs, [code])
                pages = []
                page = []
                all_songs = []
                count = 0
                ammount = 0
                total_score = 0
                for i in request["leaderboard"]:
                    if i["data"] != []:
                        if i["leaderboard_name"] != "all_time_leaders":
                            if i["leaderboard_name"] != "all_time_totals":
                                ammount = ammount + 1
                for p in request["leaderboard"]:
                    if p["leaderboard_name"] != "all_time_leaders":
                        if p["leaderboard_name"] != "all_time_totals":
                            if p["data"] != []:
                                page.append(p)
                                count = count + 1
                                print(count)
                                total_score = total_score + p["data"][0]["score"]
                                if count == 20 or count == 40 or count == ammount:
                                    pages.append(page)
                                    page = []
                for page in pages:
                    for data in page:
                        all_songs.append(data)
                m = None
                for page in pages:
                    m = await ctx.send(embed=make_myscores_embed(page, sender, api, all_songs, total_score))
                    await asyncio.sleep(0.1)
                client.loop.create_task(cooldown_reaction(m, myscores_command_cooldown))
    if str(ctx.guild) in  servers_to_operate:
        if str(ctx.channel) == "leaderboards":
            await do_work()
        else:
            for channel in ctx.guild.channels:
                if str(channel) == "leaderboards":
                    m = await ctx.send(content="This command only works in " + channel.mention)
                    client.loop.create_task(cooldown_reaction(m, myscores_command_cooldown))
    elif ctx.channel.type == discord.ChannelType.private:
        await do_work()

@client.command(name='leaderboards', description='Retrieve leaderboards data')
@commands.cooldown(1, leaderboards_command_cooldown, commands.BucketType.user)
async def leaderboards(ctx, *args):
    async def do_work():
        await ctx.channel.trigger_typing()
        sender = ctx.message.author
        message_logger("COMMAND", ".leaderboards command requested by " + sender.display_name)
        if ctx.message.content == ".leaderboards":
            m = await ctx.send(embed=make_leaderboards_help_embed(sender))
            message_logger("COMMAND", "Help message sent, no arguments given")
            client.loop.create_task(cooldown_reaction(m, leaderboards_command_cooldown))
        else:
            try:
                parameters = parse_leaderboards_args(args)
                if parameters == False:
                    m = await ctx.send(embed=make_leaderboards_help_embed(sender))
                    message_logger("COMMAND", "Help message sent, error with arguments")
                    client.loop.create_task(cooldown_reaction(m, leaderboards_command_cooldown))
                    return
                songid = parameters["songid"]
                platform = parameters["platform"]
                difficulty = parameters["difficulty"]
                user = parameters["user"]
                harmonix = parameters["harmonix"]
                results = api.search_database_for_song(songid, user=user, top20=False, platform=platform, difficulty=difficulty, harmonix=harmonix)
                m = await ctx.send(embed=make_leaderboards_embed(results, sender, songid, difficulty, api=api))
                message_logger("COMMAND", "Search successful. songid=" + songid + ", user=" + user + ", platform=" + platform + ", difficulty=" + difficulty + ", harmonix=" + str(harmonix))
                client.loop.create_task(cooldown_reaction(m, leaderboards_command_cooldown))
            except Exception as e:
                print(e)
                m = await ctx.send(embed=make_leaderboards_help_embed(sender))
                message_logger("COMMAND", "Help message sent, error with arguments")
                client.loop.create_task(cooldown_reaction(m, leaderboards_command_cooldown))
    if str(ctx.guild) in servers_to_operate:
        if str(ctx.channel) == "leaderboards":
            await do_work()
        else:
            for channel in ctx.guild.channels:
                if str(channel) == "leaderboards":
                    await ctx.send(content="This command only works in " + channel.mention)
    elif ctx.channel.type == discord.ChannelType.private:
        await do_work()

@client.command()
@commands.cooldown(1, leaderboards_command_cooldown, commands.BucketType.user)
async def top20(ctx):
    async def do_work():
        if str(ctx.message.content) == ".top20":
            await ctx.channel.trigger_typing()
            sender = ctx.message.author
            message_logger("COMMAND", ".top20 command requested by " + sender.display_name)
            try:
                song = "global"
                f = open(api.leaderboards_cache_folder + os.sep + song + "top20.json")
                fjson = json.load(f)
                f.close()
                m = await ctx.send(embed=make_leaderboards_embed(fjson, sender, song, "all", top20=True, Global=True, ost=api.global_songs))
                message_logger("COMMAND", "Search successful. songid=" + song)
                client.loop.create_task(cooldown_reaction(m, leaderboards_command_cooldown))
            except Exception as e:
                print(e)
                message_logger("COMMAND", "Help message sent, error with arguments")
                #client.loop.create_task(cooldown_reaction(m, leaderboards_command_cooldown))
        else:
            await ctx.channel.trigger_typing()
            sender = ctx.message.author
            message_logger("COMMAND", ".top20 command requested by " + sender.display_name)
            try:
                song = str(ctx.message.content).split(" ", 1)[1]
                files = [f for f in glob.glob(api.leaderboards_cache_folder + os.sep + "**/*.json", recursive=True)]
                found = False
                for f in files:
                    if song.lower() == f.lower().split(os.sep)[-1:][0][:-10]:
                        found = True
                        song = f.split(os.sep)[-1:][0][:-10]
                        break
                if found == False:
                    for f in files:
                        if song.lower() in f.lower():
                            song = f.split(os.sep)[-1:][0][:-10]
                            break
                f = open(api.leaderboards_cache_folder + os.sep + song + "top20.json")
                fjson = json.load(f)
                f.close()
                m = await ctx.send(embed=make_leaderboards_embed(fjson, sender, song, "all", top20=True))
                message_logger("COMMAND", "Search successful. songid=" + song)
                client.loop.create_task(cooldown_reaction(m, leaderboards_command_cooldown))
            except Exception as e:
                print(e)
                message_logger("COMMAND", "Help message sent, error with arguments")
                #client.loop.create_task(cooldown_reaction(m, leaderboards_command_cooldown))
    if str(ctx.guild) in servers_to_operate:
        if str(ctx.channel) == top20_channel:
            await do_work()
        else:
            for channel in ctx.guild.channels:
                if str(channel) == top20_channel:
                    await ctx.send(content="This command only works in " + channel.mention)
    elif ctx.channel.type == discord.ChannelType.private:
        await do_work()