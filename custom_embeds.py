import discord
import datetime
import locale
import json

from tools import calculate_stars
from audica_leaderboards import friend_codes

locale.setlocale(locale.LC_ALL, '')

gs_emoji = "<:gs:601299867565817856>"
expert_emoji = "<:expert:601299842865692692>"
advanced_emoji = "<:advanced:601299833197953035>"
standard_emoji = "<:moderate:601299823097937931>"
beginner_emoji = "<:begin:601299853242531852>"

fc_emoji = "<:fc:601465998469627965>"
fc_glow_emoji = "<:fc_glow:601466011878686720>"
hundread_emoji = "\U0001F4AF"
blank_emoji = "<:blank:631071395400515584>"
blank2_emoji = "<:blank:601468345090441405>"

steam_logo_emoji = "<:steam:601254903091953684>"
steam_logo_2_emoji = "<:steam2:602219518323851305>"
oculus_logo_emoji = "<:oculus:601254668558925835>"
viveport_logo_emoji = "<:viveport:601254695964639232>"
psvr_logo_emoji = "<:psvr:631062200114610206>"

hmx_logo_emoji = "<:hmx:601261184070582278>"
audica_logo_emoji = "<:audica:601294897269571604>"

twitch_logo_emoji = "<:twitch_logo:621157988551622660>"
mixer_logo_emoji = "<:mixer_logo:631127739142766641>"
mixer_logo2_emoji = "<:mixer:652426318612529162>"

mapper1_emoji = "<:mapper1:616497259701338145>"
mapper2_emoji = "<:mapper2:616497297680760843>"

up_arrow_emoji = '\U00002B06'
down_arrow_emoji = '\U00002B07'
new_emoji = '\U0001f195'

PepeHands_emoji = "<:PepeHands:602300555825512479>"
Pog_emoji = "<:Pog:602968670301454339>"

max_user_characters = 18
max_songid_characters = 20

def make_mixer_embed(stream):
    streamer_name = stream["user"]["username"]
    stream_url = "https://mixer.com/" + streamer_name
    stream_status = stream["name"]
    stream_thumbnail = stream["thumbnail"]["url"]
    stream_logo = stream["user"]["avatarUrl"]
    stream_viewers = stream["type"]["viewersCurrent"]
    embed = discord.Embed(
        title = mixer_logo2_emoji + " Mixer Audica Stream",
        description = stream_status,
        url = stream_url
    )
    embed.set_author(name=streamer_name, url=stream_url, icon_url=stream_logo)
    embed.set_image(url=stream_thumbnail)
    embed.add_field(name="Viewers", value=stream_viewers)
    return embed

def make_twitch_embed(stream, user_data):
    streamer_name = user_data["login"]
    stream_url = "https://twitch.tv/" + streamer_name
    stream_status = stream["title"]
    stream_thumbnail = stream["thumbnail_url"].replace("{width}", "320").replace("{height}", "180")
    stream_logo = user_data["profile_image_url"]
    stream_viewers = stream["viewer_count"]
    embed = discord.Embed(
        title = twitch_logo_emoji + " Twitch Audica Stream",
        description = stream_status,
        url = stream_url
    )
    embed.set_author(name=streamer_name, url=stream_url, icon_url=stream_logo)
    embed.set_image(url=stream_thumbnail)
    embed.add_field(name="Viewers", value=stream_viewers)
    return embed
    
def make_compare_mps_embed(scores, user, sender, api):
    songs_string = ""
    user_string = ""
    mps_string = ""
    user_name = ""
    user_platform = user.split("_")[0]
    user_platform_emoji = ""
    user_developer = False
    user_mapper = 0
    user_mapper_emoji = ""
    mappers1 = []
    mappers2 = []
    f = open("mapper_icon1.txt", "r")
    for line in f:
        mappers1.append(line.replace("\n", ""))
    f.close()
    f = open("mapper_icon2.txt", "r")
    for line in f:
        mappers2.append(line.replace("\n", ""))
    f.close()
    for song in scores:
        if song != "all_time_leaders":
            if song["leaderboard_name"] != "all_time_totals":
                song_id = song["leaderboard_name"]
                max_score = calculate_stars(song_id, "expert", 0)[1]
                user_score = 0
                if song_id in [i[1] for i in api.customs]:
                    hash = song_id.split("_")[-1]
                    song_id = song_id.replace("_" + hash, "")
                if len(song_id) > max_songid_characters:
                    song_id = song_id[0:max_songid_characters] + "..."
                for data in song["data"]:
                    if data["platform_id"] == user:
                        user_score = int(data["score"])
                        user_developer = data["developer"]
                    user_name = data["user"]
                if user_score != max_score:
                    if user_score < max_score:
                        difference = locale.format_string("%d", max_score - user_score, grouping=True)
                        sign = "+"
                percentage = str(100 * float(user_score)/float(max_score))[0:5] + "%"
                user_string = user_string + locale.format_string("%d", user_score, grouping=True) + " (" + percentage + ")\n"
                mps_string = mps_string + locale.format_string("%d", max_score, grouping=True) + " (" + sign + str(difference) + ")\n"
                songs_string = songs_string + song_id + "\n"
    desc = "User \""
    if user_platform == "steam":
        user_platform_emoji = steam_logo_2_emoji
    elif user_platform == "oculus":
        user_platform_emoji = oculus_logo_emoji
    elif user_platform == "viveport":
        user_platform_emoji = viveport_logo_emoji
    elif user_platform == "psn":
        user_platform_emoji = psvr_logo_emoji
    desc = desc + user_platform_emoji
    if user in mappers1:
        user_mapper = 1
    elif user in mappers2:
        user_mapper = 2
    if user_developer == True:
        desc = desc + hmx_logo_emoji
    if user_mapper == 1:
        desc = desc + mapper1_emoji
    elif user_mapper == 2:
        desc = desc + mapper2_emoji
    desc = desc + user_name + "\" compared with max possible score"

    embed = discord.Embed(
        title = audica_logo_emoji + " Audica Leaderboards",
        description = desc
    )
    if len(user_name) > max_user_characters:
        user_name = user_name[0:max_user_characters] + "..."
    embed.set_author(name=sender.display_name, icon_url=sender.avatar_url)
    embed.add_field(name="Song ID " + blank_emoji, value=songs_string, inline=True)
    embed.add_field(name=user_name + " " + blank_emoji, value=user_string, inline=True)
    embed.add_field(name="Max possible score" + blank_emoji, value=mps_string, inline=True)
    return embed

def make_compare_embed(scores, user1, user2, user1_name, user2_name, sender, api):
    songs_string = ""
    user1_string = ""
    user2_string = ""
    user1_platform = user1.split("_")[0]
    user2_platform = user2.split("_")[0]
    user1_platform_emoji = ""
    user2_platform_emoji = ""
    user1_developer = False
    user2_developer = False
    user1_mapper = 0
    user2_mapper = 0
    user1_mapper_emoji = ""
    user2_mapper_emoji = ""
    mappers1 = []
    mappers2 = []
    f = open("mapper_icon1.txt", "r")
    for line in f:
        mappers1.append(line.replace("\n", ""))
    f.close()
    f = open("mapper_icon2.txt", "r")
    for line in f:
        mappers2.append(line.replace("\n", ""))
    f.close()
    for song in scores:
        if song != "all_time_leaders":
            if song["leaderboard_name"] != "all_time_totals":
                user1_score = 0
                user2_score = 0
                song_id = song["leaderboard_name"]
                if song_id in [i[1] for i in api.customs]:
                    hash = song_id.split("_")[-1]
                    song_id = song_id.replace("_" + hash, "")
                if len(song_id) > max_songid_characters:
                    song_id = song_id[0:max_songid_characters] + "..."
                for data in song["data"]:
                    if data["platform_id"] == user1:
                        user1_score = int(data["score"])
                        user1_developer = data["developer"]
                    if data["platform_id"] == user2:
                        user2_score = int(data["score"])
                        user2_developer = data["developer"]
                if user1_score != user2_score:
                    if user1_score > user2_score:
                        difference = locale.format_string("%d", user1_score - user2_score, grouping=True)
                        sign = "+"
                    else:
                        difference = locale.format_string("%d", user2_score - user1_score, grouping=True)
                        sign = "-"
                if sign == "+":
                    user1_string = user1_string + locale.format_string("%d", user1_score, grouping=True) + " (" + sign + str(difference) + ")\n"
                    user2_string = user2_string + locale.format_string("%d", user2_score, grouping=True) + "\n"
                elif sign == "-":
                    sign = "+"
                    user1_string = user1_string + locale.format_string("%d", user1_score, grouping=True) + "\n"
                    user2_string = user2_string + locale.format_string("%d", user2_score, grouping=True) + " (" + sign + str(difference) + ")\n"
                songs_string = songs_string + song_id + "\n"
    desc = "User \""
    if user1_platform == "steam":
        user1_platform_emoji = steam_logo_2_emoji
    elif user1_platform == "oculus":
        user1_platform_emoji = oculus_logo_emoji
    elif user1_platform == "viveport":
        user1_platform_emoji = viveport_logo_emoji
    elif user1_platform == "psn":
        user1_platform_emoji = psvr_logo_emoji
    desc = desc + user1_platform_emoji
    if user1 in mappers1:
        user1_mapper = 1
    elif user1 in mappers2:
        user1_mapper = 2
    if user1_developer == True:
        desc = desc + hmx_logo_emoji
    if user1_mapper == 1:
        desc = desc + mapper1_emoji
    elif user1_mapper == 2:
        desc = desc + mapper2_emoji
    desc = desc + user1_name + "\" compared with user \""
    if user2_platform == "steam":
        user2_platform_emoji = steam_logo_2_emoji
    elif user2_platform == "oculus":
        user2_platform_emoji = oculus_logo_emoji
    elif user2_platform == "viveport":
        user2_platform_emoji = viveport_logo_emoji
    elif user2_platform == "psn":
        user2_platform_emoji = psvr_logo_emoji
    desc = desc + user2_platform_emoji
    if user2 in mappers1:
        user2_mapper = 1
    elif user2 in mappers2:
        user2_mapper = 2
    if user2_developer == True:
        desc = desc + hmx_logo_emoji
    if user2_mapper == 1:
        desc = desc + mapper1_emoji
    elif user2_mapper == 2:
        desc = desc + mapper2_emoji
    desc = desc + user2_name + "\""
    embed = discord.Embed(
        title = audica_logo_emoji + " Audica Leaderboards",
        description = desc
    )
    if len(user1_name) > max_user_characters:
        user1_name = user1_name[0:max_user_characters] + "..."
    if len(user2_name) > max_user_characters:
        user2_name = user2_name[0:max_user_characters] + "..."
    embed.set_author(name=sender.display_name, icon_url=sender.avatar_url)
    embed.add_field(name="Song ID " + blank_emoji, value=songs_string, inline=True)
    embed.add_field(name=user1_name + " " + blank_emoji, value=user1_string, inline=True)
    embed.add_field(name=user2_name + " " + blank_emoji, value=user2_string, inline=True)
    return embed


def make_myscores_embed(scores, sender, api, all_songs, total_score):
    max_score = 0
    ranks_string = ""
    songs_string = ""
    scores_string = ""
    platform = ""
    platform_emoji = ""
    platform_id = ""
    user_name = ""
    developer = False
    mapper = 0
    mappers1 = []
    mappers2 = []
    f = open("mapper_icon1.txt", "r")
    for line in f:
        mappers1.append(line.replace("\n", ""))
    f.close()
    f = open("mapper_icon2.txt", "r")
    for line in f:
        mappers2.append(line.replace("\n", ""))
    f.close()
    for song in [i["leaderboard_name"] for i in all_songs]:
        max_score = max_score + calculate_stars(song, "expert", 0)[1]
    for song in scores:
        if song != "all_time_leaders":
            if song["leaderboard_name"] != "all_time_totals":
                try:
                    stars = calculate_stars(song["leaderboard_name"], song["data"][0]["difficulty"], song["data"][0]["score"])
                    if song["data"][0]["difficulty"] == "expert":
                        if stars[0] == 6:
                            stars_emoji = gs_emoji
                            stars[0] = 5
                        else:
                            stars_emoji = expert_emoji
                    elif song["data"][0]["difficulty"] == "advanced":
                        stars_emoji = advanced_emoji
                    elif song["data"][0]["difficulty"] == "moderate":
                        stars_emoji = standard_emoji
                    elif song["data"][0]["difficulty"] == "beginner":
                        stars_emoji = beginner_emoji
                    platform = song["data"][0]["platform"]
                    platform_id = song["data"][0]["platform_id"]
                    stars_string = "`" + str(stars[0]) + "x`" + stars_emoji + " "
                    if song["data"][0]["developer"] == True:
                        developer = True
                    user_name = song["data"][0]["user"]
                    if song["data"][0]["full_combo"] == True:
                        songs_string = songs_string + fc_emoji + " "
                    elif song["data"][0]["percent"] == 100.0:
                        songs_string = songs_string + hundread_emoji + " "
                    else:
                        songs_string = songs_string + blank_emoji + " "
                    song_id = song["leaderboard_name"]
                    if song_id in [i[1] for i in api.customs]:
                        hash = song_id.split("_")[-1]
                        song_id = song_id.replace("_" + hash, "")
                    if len(song_id) > max_songid_characters:
                        song_id = song_id[0:max_songid_characters] + "..."
                    songs_string = songs_string + "`" + song_id + "`\n"
                    ranks_string = ranks_string + "`" + str(song["data"][0]["rank"]) + "`" + blank_emoji +  "\n"
                    scores_string = scores_string + stars_string + locale.format_string("%d", int(song["data"][0]["score"]), grouping=True) + "\n"
                except:
                    pass
    if platform == "steam":
        platform_emoji = steam_logo_2_emoji
    elif platform == "oculus":
        platform_emoji = oculus_logo_emoji
    elif platform == "viveport":
        platform_emoji = viveport_logo_emoji
    elif platform == "psn":
        platform_emoji = psvr_logo_emoji
    if platform_id in mappers1:
        mapper = 1
    elif platform_id in mappers2:
        mapper = 2
    desc = "Request for user \"" + platform_emoji
    if developer == True:
        desc = desc + hmx_logo_emoji
    if mapper == 1:
        desc = desc + mapper1_emoji
    elif mapper == 2:
        desc = desc + mapper2_emoji
    desc = desc + " " + user_name + "\"\nMax possible score: " + locale.format_string("%d", int(max_score), grouping=True) + "\nTotal score: " + locale.format_string("%d", int(total_score), grouping=True)
    embed = discord.Embed(
        title = audica_logo_emoji + " Audica Leaderboards",
        description = desc
    )
    embed.set_author(name=sender.display_name, icon_url=sender.avatar_url)
    embed.add_field(name="Song ID " + blank_emoji, value=songs_string, inline=True)
    embed.add_field(name="Rank " + blank_emoji, value=ranks_string, inline=True)
    embed.add_field(name="Score " + blank_emoji, value=scores_string, inline=True)
    return embed

def make_leaderboards_embed(scores, sender, song, difficulty, top20=False, Global=False, ost=[], api=None, custom=False):
    max_score = 0
    ranks_string = ""
    users_string = ""
    all_scores_string = ""
    platform_id = ""
    sum_of_timestamps = 0
    ammount_of_timestamps = 0
    user_request = False
    mappers1 = []
    mappers2 = []
    f = open("mapper_icon1.txt", "r")
    for line in f:
        mappers1.append(line.replace("\n", ""))
    f.close()
    f = open("mapper_icon2.txt", "r")
    for line in f:
        mappers2.append(line.replace("\n", ""))
    f.close()
    if Global == False:
        try:
            if difficulty == "all" or difficulty == "expert":
                max_score = calculate_stars(song, "expert", 0)[1]
            elif difficulty == "advanced":
                max_score = calculate_stars(song, "advanced", 0)[1]
            elif difficulty == "moderate":
                max_score = calculate_stars(song, "moderate", 0)[1]
            elif difficulty == "beginner":
                max_score = calculate_stars(song, "beginner", 0)[1]
        except Exception as e:
            #print(e)
            for custom in api.customs:
                if song.lower() in custom[0].lower():
                    song = custom[0]
            if difficulty == "all":
                try:
                    max_score = calculate_stars(song, "expert", 0, custom=True)[1]
                except:
                    try:
                        max_score = calculate_stars(song, "advanced", 0, custom=True)[1]
                    except:
                        try:
                            max_score = calculate_stars(song, "moderate", 0, custom=True)[1]
                        except:
                            try:
                                max_score = calculate_stars(song, "beginner", 0, custom=True)[1]
                            except:
                                max_score = 0
            elif difficulty == "expert":
                max_score = calculate_stars(song, "expert", 0, custom=True)[1]
            elif difficulty == "advanced":
                max_score = calculate_stars(song, "advanced", 0, custom=True)[1]
            elif difficulty == "moderate":
                max_score = calculate_stars(song, "moderate", 0, custom=True)[1]
            elif difficulty == "beginner":
                max_score = calculate_stars(song, "beginner", 0, custom=True)[1]
    else:
        for song in ost:
            max_score = max_score + calculate_stars(song, "expert", 0)[1]
    codes = friend_codes()
    codes.load()
    for item in scores:
        if Global == False:
            try:
                stars = calculate_stars(song, item["difficulty"], int(item["score"]))
            except:
                stars = calculate_stars(song, item["difficulty"], int(item["score"]), custom=True)
            if item["difficulty"] == "expert":
                if stars[0] == 6:
                    stars_emoji = gs_emoji
                    stars[0] = 5
                else:
                    stars_emoji = expert_emoji
            elif item["difficulty"] == "advanced":
                stars_emoji = advanced_emoji
            elif item["difficulty"] == "moderate":
                stars_emoji = standard_emoji
            elif item["difficulty"] == "beginner":
                stars_emoji = beginner_emoji
        code = codes.get_code(sender.id)
        if code != None:
            platform_id = code
        if platform_id != "":
            if item["platform_id"] == platform_id:
                ranks_string = ranks_string + "**"
                users_string = users_string + "**"
                all_scores_string = all_scores_string + "**"
        elif item["user"] == sender.display_name:
            ranks_string = ranks_string + "**"
            users_string = users_string + "**"
            all_scores_string = all_scores_string + "**"
        if Global == False:
            stars_string = "`" + str(stars[0]) + "x`" + stars_emoji + " "
        if item["platform"] == "steam":
            emoji = steam_logo_2_emoji
        elif item["platform"] == "oculus":
            emoji = oculus_logo_emoji
        elif item["platform"] == "viveport":
            emoji = viveport_logo_emoji
        elif item["platform"] == "psn":
            emoji = psvr_logo_emoji
        if len(str(item["rank"])) == 1:
            ranks_string = ranks_string + emoji + "`0" + str(item["rank"]) + "`"
        else:
            ranks_string = ranks_string + emoji + "`" + str(item["rank"]) + "`"
        if item["developer"] == True:
            ranks_string = ranks_string + " " + hmx_logo_emoji
        if item["platform_id"] in mappers1:
            ranks_string = ranks_string + " " + mapper1_emoji
        elif item["platform_id"] in mappers2:
            ranks_string = ranks_string + " " + mapper2_emoji
        if len(item["user"]) > max_user_characters:
            user = "`" + item["user"][0:max_user_characters] + "...`"
        else:
            user = "`" + item["user"] + "`"
        if Global == False:
            if item["full_combo"] == True:
                if item["user"] == sender.display_name:
                    user = fc_glow_emoji + " " + user
                else:
                    user = fc_emoji + " " + user
            elif item["percent"] == 100.0:
                user = hundread_emoji + " " + user
            else:
                user = blank_emoji + " " + user
        else:
            user = blank_emoji + " " + user
        ranks_string = ranks_string + "\n"
        users_string = users_string + user + "\n"
        if Global == False:
            all_scores_string = all_scores_string + stars_string + locale.format_string("%d", int(item["score"]), grouping=True) + "\n"
        else:
            all_scores_string = all_scores_string + blank_emoji + "`" + locale.format_string("%d", int(item["score"]), grouping=True) + "`\n"
        
        if platform_id != "":
            if item["platform_id"] == platform_id:
                ranks_string = ranks_string + "**"
                users_string = users_string + "**"
                all_scores_string = all_scores_string + "**"
        elif item["user"] == sender.display_name:
            ranks_string = ranks_string + "**"
            users_string = users_string + "**"
            all_scores_string = all_scores_string + "**"
        try:
            song_names.append(item["song"])
            user_request = True
        except:
            user_request = False
        if top20 == False and Global == False:
            sum_of_timestamps = sum_of_timestamps + item["timestamp"]
            ammount_of_timestamps = ammount_of_timestamps + 1
    if user_request == False:
        if Global == True:
            song = "global"
        desc = "Request for \"" + song + "\"\nMax possible score: " + locale.format_string("%d", int(max_score), grouping=True)
    else:
        desc = "Request for \"" + song + "\""
    if top20 == False:
        timestamps_average = sum_of_timestamps / ammount_of_timestamps
        utc_timestamp_average = datetime.datetime.fromtimestamp(timestamps_average + 10800)
        embed = discord.Embed(
            title = audica_logo_emoji + " Audica Leaderboards",
            description = desc,
            timestamp = utc_timestamp_average
        )
        embed.set_footer(text="Average update time")
    else:
        embed = discord.Embed(
            title = audica_logo_emoji + " Audica Leaderboards",
            description = desc
        )
    embed.set_author(name=sender.display_name, icon_url=sender.avatar_url)
    if Global == False:
        embed.add_field(name="Rank", value=ranks_string, inline=True)
        embed.add_field(name="User", value=users_string, inline=True)
        embed.add_field(name="Score", value=all_scores_string, inline=True)
    else:
        embed.add_field(name="Rank " + blank_emoji, value=ranks_string, inline=True)
        embed.add_field(name=blank_emoji + " User", value=users_string, inline=True)
        embed.add_field(name=blank_emoji + " Score", value=all_scores_string, inline=True)
    return embed
    
def make_leaderboards_help_embed(sender):
    embed = discord.Embed(
        title = "Help message",
        description = "Usage: `.leaderboards [-s songid] [-u user] [-p platform] [-d difficulty] [-hmx]`\nThis function searches through the official Audica leaderboards. If you need to search for spaced words (i.e. Steam username with spaces) you can put them in quotes like this: \"multiple words\""
    )
    embed.set_author(name=sender.display_name, icon_url=sender.avatar_url)
    embed.add_field(name="`[-s songid]` or `[--songid songid]`", value="Currently a needed value. Search for a specific song.")
    embed.add_field(name="`[-u user]` or `[--user user]`", value="If specified returns scores for that user and around that user for the specified song")
    embed.add_field(name="`[-p platform]` or `[--platform platform]`", value="If specified only returns scores for that platform. Possible values are [steam, oculus, viveport].")
    embed.add_field(name="`[-d difficulty]` or `[--difficulty difficulty]`", value="If specified only returns scores for that difficulty. Cannot be used with --user. Possible values are [beginner, moderate, advanced, expert].")
    embed.add_field(name="`[-hmx]` or `[--harmonix]`", value="If that flag is specified, only returns developer scores.")
    return embed
    
def make_songid_embed(sender):
    embed = discord.Embed(
        title = "Song IDs",
        description = "This is a list of all the songid values"
    )
    embed.set_author(name=sender.display_name, icon_url=sender.avatar_url)
    embed.add_field(name="Addicted to a Memory", value="addictedtoamemory", inline=True)
    embed.add_field(name="Adrenaline", value="adrenaline", inline=True)
    embed.add_field(name="Boom Boom", value="boomboom", inline=True)
    embed.add_field(name="Break for Me", value="breakforme", inline=True)
    embed.add_field(name="Collider", value="collider", inline=True)
    embed.add_field(name="Destiny", value="destiny", inline=True)
    embed.add_field(name="Gametime", value="gametime", inline=True)
    embed.add_field(name="Gold Dust", value="golddust", inline=True)
    embed.add_field(name="HR8938 Cephei", value="hr8938cephei", inline=True)
    embed.add_field(name="I Feel Love", value="ifeellove", inline=True)
    embed.add_field(name="I Want U", value="iwantu", inline=True)
    embed.add_field(name="Lazerface", value="lazerface", inline=True)
    embed.add_field(name="Overtime", value="overtime", inline=True)
    embed.add_field(name="Perfect (Exceeder)", value="perfectexceeder", inline=True)
    embed.add_field(name="POP/STARS", value="popstars", inline=True)
    embed.add_field(name="Predator", value="predator", inline=True)
    embed.add_field(name="Raise Your Weapon (Noisia Remix)", value="raiseyourweapon_noisia", inline=True)
    embed.add_field(name="Resistance", value="resistance", inline=True)
    embed.add_field(name="Smoke", value="smoke", inline=True)
    embed.add_field(name="Splinter", value="splinter", inline=True)
    embed.add_field(name="Synthesized", value="synthesized", inline=True)
    embed.add_field(name="The Space", value="thespace", inline=True)
    embed.add_field(name="Time for Crime", value="timeforcrime", inline=True)
    embed.add_field(name="To the Stars", value="tothestars", inline=True)
    return embed

def make_helplinks_embed(sender):
    embed = discord.Embed(
        title = "Help links"
    )
    f = open("help_link_list.json", "r")
    fjson = json.load(f)
    f.close()
    embed.set_author(name=sender.display_name, icon_url=sender.avatar_url)
    toolsname = "Tools"
    docsname = "Documents"
    toolsvalue = ""
    docsvalue = ""
    for item in fjson:
        if item["type"] == "Tool":
            toolsvalue = toolsvalue + "[" + item["name"] + "](" + item["link"] + ") " + item["description"] + "\n"
        elif item["type"] == "Documents":
            docsvalue = docsvalue + "[" + item["name"] + "](" + item["link"] + ") " + item["description"] + "\n"
    embed.add_field(name=toolsname, value=toolsvalue)
    embed.add_field(name=docsname, value=docsvalue)
    return embed
    
def make_top20_autoupdate_embed(song, old_scores, new_scores, custom=False, api=None):
    #if song != "global":
        #max_score = calculate_stars(song, "expert", 0)[1]
    #else:
    max_score = 0
    ranks_string = ""
    users_string = ""
    all_scores_string = ""
    scores_to_show = []
    mappers1 = []
    mappers2 = []
    f = open("mapper_icon1.txt", "r")
    for line in f:
        mappers1.append(line.replace("\n", ""))
    f.close()
    f = open("mapper_icon2.txt", "r")
    for line in f:
        mappers2.append(line.replace("\n", ""))
    f.close()
    for score in new_scores:
        if score not in old_scores:
            scores_to_show.append(score)
            if len(scores_to_show) >= 20:
                break
    for score in scores_to_show:
        if song != "global":
            if custom == False:
                stars = calculate_stars(song, score["difficulty"], int(score["score"]))
            else:
                stars = None
                for s in api.customs:
                    if song == s[0]:
                        stars = calculate_stars(s[0], score["difficulty"], int(score["score"]), custom=True)
            if score["difficulty"] == "expert":
                if stars[0] == 6:
                    stars_emoji = gs_emoji
                    stars[0] = 5
                else:
                    stars_emoji = expert_emoji
            elif score["difficulty"] == "advanced":
                stars_emoji = advanced_emoji
            elif score["difficulty"] == "moderate":
                stars_emoji = standard_emoji
            elif score["difficulty"] == "beginner":
                stars_emoji = beginner_emoji
            stars_string = "`" + str(stars[0]) + "x`" + stars_emoji + " "
        else:
            stars_strings = blank_emoji
        if score["platform"] == "steam":
            emoji = steam_logo_2_emoji
        elif score["platform"] == "oculus":
            emoji = oculus_logo_emoji
        elif score["platform"] == "viveport":
            emoji = viveport_logo_emoji
        elif item["platform"] == "psn":
            emoji = psvr_logo_emoji
        if len(str(score["rank"])) == 1:
            ranks_string = ranks_string + emoji + " `0" + str(score["rank"]) + "`"
        else:
            ranks_string = ranks_string + emoji + " `" + str(score["rank"]) + "`"
        user_found = False
        for s in old_scores:
            if s["platform_id"] == score["platform_id"]:
                user_found = True
                if s["rank"] < score["rank"]:
                    difference = score["rank"] - s["rank"]
                    sign = "-"
                    ranks_string = ranks_string + " " + down_arrow_emoji
                    if s["rank"] == 1:
                        ranks_string = ranks_string + " " + PepeHands_emoji
                elif s["rank"] > score["rank"]:
                    difference = s["rank"] - score["rank"]
                    sign = "+"
                    ranks_string = ranks_string + " " + up_arrow_emoji + "(" + sign + str(difference) + ")"
                    if score["rank"] == 1:
                        ranks_string = ranks_string + " " + Pog_emoji
        if user_found == False:
            ranks_string = ranks_string + " " + new_emoji
            if score["rank"] == 1:
                ranks_string = ranks_string + " " + Pog_emoji
        if score["developer"] == True:
            ranks_string = ranks_string + " " + hmx_logo_emoji
        if score["platform_id"] in mappers1:
            ranks_string = ranks_string + " " + mapper1_emoji
        elif score["platform_id"] in mappers2:
            ranks_string = ranks_string + " " + mapper2_emoji
        if len(score["user"]) > max_user_characters:
            user = "`" + score["user"][0:max_user_characters] + "`..."
        else:
            user = "`" + score["user"] + "`"
        if song != "global":
            if score["full_combo"] == True:
                user = fc_emoji + " " + user
            elif score["percent"] == 100.0:
                user = hundread_emoji + " " + user
            else:
                user = blank_emoji + " " + user
        else:
            user = blank_emoji + " " + user
        if song != "global":
            all_scores_string = all_scores_string + stars_string + locale.format_string("%d", int(score["score"]), grouping=True)
        else:
            all_scores_string = all_scores_string + blank_emoji + locale.format_string("%d", int(score["score"]), grouping=True)
        for s in old_scores:
            if s["user"] == score["user"]:
                if s["score"] < score["score"]:
                    difference = locale.format_string("%d", int(score["score"] - s["score"]), grouping=True)
                    sign = "+"
                    all_scores_string = all_scores_string + " (" + sign + str(difference) + ")"
        ranks_string = ranks_string + "\n"
        users_string = users_string + user + "\n"
        all_scores_string = all_scores_string + "\n"
    desc = "New activity for \"" + song + "\"" + "\n"
    for score in old_scores:
        user_found = False
        for s in new_scores:
            if score["user"] == s["user"]:
                user_found = True
        if custom == False:
            if user_found == False:
                desc = desc + "User \"" + score["user"] + "\" has left the top 20 " + PepeHands_emoji + "\n"
    embed = discord.Embed(
        title = audica_logo_emoji + " Audica Leaderboards",
        description = desc
    )
    if song != "global":
        embed.add_field(name="Rank", value=ranks_string, inline=True)
        embed.add_field(name="User", value=users_string, inline=True)
        embed.add_field(name="Score", value=all_scores_string, inline=True)
    else:
        embed.add_field(name="Rank " + blank_emoji, value=ranks_string, inline=True)
        embed.add_field(name=blank_emoji + " User", value=users_string, inline=True)
        embed.add_field(name=blank_emoji + " Score", value=all_scores_string, inline=True)
    return(embed)