import requests
import time
import os
import json
import datetime
import shutil
import glob
import asyncio

from urllib import request, parse
from threading import Thread
from tools import message_logger, ost_songlist, extras_songlist, customs_database, make_custom_sort, calculate_stars

class leaderboards_api():

    requests_per_hour = 2000
    seconds_per_requests = 4
    seconds_per_requests_customs = 4.5
    requests_left = 2000
    
    leaderboards_cache_folder = "LEADERBOARDS_CACHE"
    leaderboards_database_folder = "LEADERBOARDS_DATABASE"
    customs_leaderboards_folder = "LEADERBOARDS_DATABASE" + os.sep + "CUSTOMS"

    audica_leaderboards_api_key = "X-API-KEY YOUR_AUDICA_LEADERBOARDS_API_KEY"
    base_url = "https://audica-api.hmxwebservices.com"
    leaderboards_list_url = "/public/1/leaderboards/"
    leaderboard_base_url = "/public/1/leaderboard/"

    headers = {
               'content-type': "application/json",
               'Authorization': audica_leaderboards_api_key
              }

    ##search options

    platforms = ["global", "steam", "oculus", "viveport", "psn"]
    difficulties = ["all", "beginner", "moderate", "advanced", "expert"]
    page_size_min = "1"
    page_size_max = "25"
    
    ost = ["addictedtoamemory", 
           "adrenaline", 
           "boomboom", 
           "breakforme", 
           "collider", 
           "destiny",
           "gametime",
           "golddust",
           "hr8938cephei",
           "ifeellove",
           "iwantu",
           "lazerface",
           "overtime",
           "perfectexceeder",
           "popstars",
           "predator",
           "raiseyourweapon_noisia",
           "resistance",
           "smoke",
           "splinter",
           "synthesized",
           "thespace",
           "timeforcrime",
           "tothestars",
           "highwaytooblivion_short",
           "highwaytooblivion_full",
           "decodeme",
           "eyeforaneye"]
           
    global_songs = ["addictedtoamemory", 
                    "adrenaline", 
                    "boomboom", 
                    "breakforme", 
                    "collider", 
                    "destiny",
                    "gametime",
                    "golddust",
                    "hr8938cephei",
                    "ifeellove",
                    "iwantu",
                    "lazerface",
                    "overtime",
                    "perfectexceeder",
                    "popstars",
                    "predator",
                    "raiseyourweapon_noisia",
                    "resistance",
                    "smoke",
                    "splinter",
                    "synthesized",
                    "thespace",
                    "timeforcrime",
                    "tothestars",
                    "highwaytooblivion_short",
                    "decodeme",
                    "eyeforaneye"]
           
    extra_songs = []
    dlc = []
    psn_exclusives = []
    
    songs_json = []
           
    customs = []
           
    loop_running = False
    
    log = []
    users_to_check = []
    
    def __init__(self):
        if not os.path.exists(self.leaderboards_cache_folder):
            os.makedirs(self.leaderboards_cache_folder)
            
        if not os.path.exists(self.leaderboards_database_folder):
            os.makedirs(self.leaderboards_database_folder)

        self.get_songs()
            
        self.load_custom_songs()
        
    def get_songs(self):
        self.ost = []
        self.global_songs = []
        self.extra_songs = []
        self.dlc = []
        
        song_list = self.request_leaderboards_list()
        rjson = json.loads(song_list)
        self.songs_json = rjson
        for song in rjson:
            s = rjson[song]
            if song == "exitwounds" or song == "funkycomputer" or song == "reedsofmitatrush" or song == "weallbecome":
                self.psn_exclusives.append(song)
            elif song != "all_time_leaders" and song != "all_time_totals":
                if s["dlc"] == True:
                    self.dlc.append(song)
                elif s["record_global_total"] == False:
                    self.extra_songs.append(song)
                else:
                    self.global_songs.append(song)
                self.ost.append(song)
            
    def load_custom_songs(self):
        self.customs = []
        database = customs_database()
        database.load()
        for song in database.song_list:
            self.customs.append([song["filename"].replace(".audica", ""), song["leaderboard_id"]])
            
    def post_request(self, leaderboards_list, users_list, difficulty="all", platform="global"):
        post_data = {"leaderboards": leaderboards_list,
                     "difficulty": difficulty,
                     "platform": platform,
                     "users": users_list}
        self.log_request("post")
        r = requests.post(self.base_url + self.leaderboard_base_url, headers=self.headers, json=post_data)
        
        return r.json()
        
    def get_leaderboard_stats(self):
        users = user_list()
        users.load()
        
        max_possible_global_score = 0
        ost_song_ammount = len(self.global_songs)
        extras_song_ammount = len(self.extra_songs)
        dlc_song_ammount = len(self.dlc)
        psn_exclusives_ammount = len(self.psn_exclusives)
        custom_song_ammount = len(self.customs)
        total_song_ammount = ost_song_ammount + extras_song_ammount + custom_song_ammount + dlc_song_ammount + psn_exclusives_ammount
        player_ammount = len(users.users["users"])
        top_global_player_name = ""
        top_global_player_platform = ""
        top_global_player_platform_id = ""
        top_global_player_score = 0
        top_global_player_developer = False
        
        f = open(self.leaderboards_cache_folder + os.sep + "globaltop20.json")
        fjson = json.load(f)
        f.close()
        for score in fjson:
            if score["rank"] == 1:
                top_global_player_name = score["user"]
                top_global_player_platform = score["platform"]
                top_global_player_platform_id = score["platform_id"]
                top_global_player_score = int(score["score"])
                top_global_player_developer = score["developer"]
                break
        for song in self.global_songs:
            max_possible_global_score = max_possible_global_score + calculate_stars(song, "expert", 0)[1]
            
        print(max_possible_global_score)
        print(ost_song_ammount)
        print(extras_song_ammount)
        print(dlc_song_ammount)
        print(psn_exclusives_ammount)
        print(custom_song_ammount)
        print(total_song_ammount)
        print(top_global_player_name)
        print(top_global_player_platform)
        print(top_global_player_platform_id)
        print(top_global_player_score)
        print(top_global_player_developer)
        
    def search_database_for_song(self, song, user="", top20=False, platform="all", difficulty="all", harmonix=False):
        try:
            files = [f for f in glob.glob(self.leaderboards_database_folder + os.sep + "**/*.json", recursive=True)]
            found = False
            for f in files:
                if song.lower() == f.lower().split(os.sep)[-1:][0][:-5]:
                    found = True
                    song = f.split(os.sep)[-1:][0]
                    break
            if found == False:
                for f in files:
                    if song.lower() in f.lower():
                        song = f.split(os.sep)[-1:][0]
                        break
        except:
            files = [f for f in glob.glob(self.customs_leaderboards_folder + os.sep + "**/*.json", recursive=True)]
            found = False
            for f in files:
                if song.lower() == f.lower().split(os.sep)[-1:][0][:-5]:
                    found = True
                    song = f.split(os.sep)[-1:][0]
                    break
            if found == False:
                for f in files:
                    if song.lower() in f.lower():
                        song = f.split(os.sep)[-1:][0]
                        break
        try:
            database_file = self.leaderboards_database_folder + os.sep + song
            f = open(database_file, "r")
        except:
            database_file = self.customs_leaderboards_folder + os.sep + song
            f = open(database_file, "r")
        song = song[:-5]
        database_json = json.load(f)
        f.close()
        tempscores = []
        scores = []
        count = 0
        if harmonix == True:
            for score in database_json:
                if score["developer"] == True:
                    tempscores.append(score)
            database_json = tempscores
        if platform != "all":
            for score in database_json:
                if platform == "steam":
                    if score["platform"] == "steam":
                        tempscores.append(score)
                elif platform == "oculus":
                    if score["platform"] == "oculus":
                        tempscores.append(score)
                elif platform == "viveport":
                    if score["platform"] == "viveport":
                        tempscores.append(score)
            database_json = tempscores
        if difficulty != "all":
            for score in database_json:
                if difficulty == "beginner":
                    if score["difficulty"] == "beginner":
                        tempscores.append(score)
                elif difficulty == "moderate" or difficulty == "standart" or difficulty == "standard":
                    if score["difficulty"] == "moderate":
                        tempscores.append(score)
                elif difficulty == "advanced":
                    if score["difficulty"] == "advanced":
                        tempscores.append(score)
                elif difficulty == "expert":
                    if score["difficulty"] == "expert":
                        tempscores.append(score)
            database_json = tempscores
        if user == "":
            for score in database_json:
                scores.append(score)
                count = count + 1
                if count >= 20:
                    break
        else:
            temp_scores = []
            user_index = 0
            user_scores = []
            for score in database_json:
                if user.lower() in score["user"].lower():
                    user_index = count
                    count = 0
                    break
                count = count + 1
            for score in database_json:
                if count >= user_index - 9 and count <= user_index + 10:
                    user_scores.append(score)
                elif count >= user_index + 10 and len(user_scores) <= 20:
                    user_scores.append(score)
                if len(user_scores) == 20:
                    scores = user_scores
                    count = 0
                    break
                count = count + 1
        return scores
            
    def update_state(self, song, page, total_pages, start_time=False, finish_time=False, custom=False):
        def make_new_stats():
            temp = {}
            if start_time == True:
                temp["update_start"] = time.time()
            else:
                temp["update_start"] = 0
            temp["current_page"] = page
            temp["total_pages"] = total_pages
            if finish_time == True:
                temp["update_finished"] = time.time()
            else:
                temp["update_finished"] = 0
            temp["song"] = song
            temp["priority"] = 1
            return temp
        state = []
        if custom == False:
            state_file = self.leaderboards_cache_folder + os.sep + "state.json"
        elif custom == True:
            state_file = self.leaderboards_cache_folder + os.sep + "state_customs.json"
        if os.path.isfile(state_file):
            f = open(state_file, "r")
            state = json.load(f)
            f.close()
            song_found = False
            for item in state:
                if item["song"] == song:
                    if start_time == True:
                        item["update_start"] = time.time()
                        item["update_finished"] = 0
                    elif finish_time == True:
                        item["update_finished"] = time.time()
                    item["current_page"] = page
                    item["total_pages"] = total_pages
                    song_found = True
            if song_found == False:
                state.append(make_new_stats())
        else:
            state.append(make_new_stats())
        with open(state_file, "w") as f:
            json.dump(state, f, sort_keys=True, indent=4)
            
    def log_request(self, type):
        log_file = self.leaderboards_cache_folder + os.sep + "requests.log"
        temp_list = []
        try:
            if os.path.isfile(log_file):
                #f = open(log_file, "r")
                #fjson = json.load(f)
                #f.close()
                #for item in fjson:
                for item in self.log:
                    time_difference = time.time() - item["time"]
                    if time_difference < 3600:
                        temp_list.append(item)
        except:
            message_logger("LEADERBOARDS API", "Request log corrupted, starting a new one...")
        log = {}
        log["type"] = type
        log["time"] = time.time()
        temp_list.append(log)
        
        self.log = temp_list
        
        #with open(log_file, "w") as f:
            #json.dump(temp_list, f, sort_keys=True, indent=4)
            
    def find_optimal_wait_time(self, minimum_time=18.25):
        #log_file = self.leaderboards_cache_folder + os.sep + "requests.log"
        last_hour_ammount = 0
        current_time = time.time()
        first_log_time = current_time
        #f = open(log_file, "r")
        #fjson = json.load(f)
        #f.close()
        fjson = self.log
        for item in fjson:
            last_hour_ammount = last_hour_ammount + 1
            if item["time"] < first_log_time:
                first_log_time = item["time"]
            if last_hour_ammount >= self.requests_per_hour:
                break
        time_difference = current_time - first_log_time
        requests_left = self.requests_per_hour - last_hour_ammount
        if last_hour_ammount >= self.requests_per_hour:
            wait_time = 300.0
        elif current_time == first_log_time:
            wait_time = minimum_time
        elif time_difference >= 3600:
            wait_time = minimum_time
        else:
            time_left = 3600 - time_difference
            time_left_in_minutes = time_left / 60
            ammount_per_minute =  requests_left / time_left_in_minutes
            wait_time_temp = 60 / ammount_per_minute
            if wait_time_temp >= minimum_time:
                wait_time = wait_time_temp
            else:
                wait_time = minimum_time
        self.requests_left = requests_left
        return wait_time
            
    def request_leaderboards_list(self):
        r = requests.get(self.base_url + self.leaderboards_list_url, headers=self.headers)
        self.log_request("list")
        f = open(self.leaderboards_cache_folder + os.sep + "leaderboards_list.json", "w")
        f.write(r.text)
        f.close()
        rjson = json.loads(r.text)
        #temp_ost = []
        # for item in rjson:
            # if item != "all_time_leaders":
                # temp_ost.append(str(item))
        # self.ost = temp_ost
        return r.text

    def request_all_time_leaders(self, platform="global", difficulty="all"):
        r = requests.get(self.base_url + self.leaderboard_base_url + "all_time_leaders/?platform=" + platform + "&difficulty=" + difficulty, headers=self.headers)
        self.log_request("global")
        try:
            rjson = json.loads(r.text)
        except:
            return False
        try:
            if rjson["error"] == "invalid page number":
                return "page does not exist"
            else:
                print(rjson["error"])
        except:
            return r.text

    def request_song_leaderboard(self, song, platform="global", difficulty="all", page="1", page_size="25"):
        r = requests.get(self.base_url + self.leaderboard_base_url + song + "/?platform=" + platform + "&difficulty=" + difficulty + "&page=" + page + "&page_size=" + page_size, headers=self.headers)
        self.log_request(song)
        try:
            rjson = json.loads(r.text)
        except:
            return False
        try:
            if rjson["error"] == "invalid page number":
                return "page does not exist"
            else:
                print(rjson["error"])
        except:
            return r.text
            
    def cache_song_leaderboard(self, song, current_page=1, custom=False):
        
        stop_running = False

        if not os.path.exists(self.leaderboards_cache_folder + os.sep + song):
            os.makedirs(self.leaderboards_cache_folder + os.sep + song)
            
        starting_page = current_page
        total_pages = current_page

        while(stop_running == False):
            req = self.request_song_leaderboard(song, page=str(current_page))
            if req == False:
                print("Error requesting page " + str(current_page) + " of " + str(total_pages) + " for the song " + song)
            else:
                reqjson = json.loads(req)
                total_pages = reqjson["leaderboard"]["total_pages"]
                if req == "page does not exist":
                    stop_running = True
                else:
                    f = open(self.leaderboards_cache_folder + os.sep + song + os.sep + str(current_page) + ".json", "w")
                    f.write(req)
                    f.close()
                    if total_pages == 0:
                        current_page = 0
                        if custom == True:
                            self.update_state(song, current_page, total_pages, start_time=True, custom=True)
                        else:
                            self.update_state(song, current_page, total_pages, start_time=True)
                    if current_page == 1:
                        if custom == True:
                            self.update_state(song, current_page, total_pages, start_time=True, custom=True)
                        else:
                            self.update_state(song, current_page, total_pages, start_time=True)
                        if total_pages == current_page:
                            if custom == True:
                                self.update_state(song, current_page, total_pages, finish_time=True, custom=True)
                            else:
                                self.update_state(song, current_page, total_pages, finish_time=True)
                    elif total_pages == current_page:
                        if custom == True:
                            self.update_state(song, current_page, total_pages, finish_time=True, custom=True)
                        else:
                            self.update_state(song, current_page, total_pages, finish_time=True)
                    else:
                        if custom == True:
                            self.update_state(song, current_page, total_pages, custom=True)
                        else:
                            self.update_state(song, current_page, total_pages)
                if current_page == total_pages:
                    stop_running = True
                    message_logger("LEADERBOARDS API", "[SONG \"" + song + "\"] Page "+ str(current_page) + " of " + str(total_pages) + " saved. " + \
                                   str(self.requests_left) + " of " + str(self.requests_per_hour) + " requests left.")
                    if custom == False:
                        message_logger("LEADERBOARDS API", "[SONG \"" + song + "\"] Song cache saving and user data update is starting.")
                        self.save_song_cache_to_database(song)
                    else:
                        message_logger("LEADERBOARDS API", "[SONG \"" + song + "\"] Song cache saving is starting.")
                        wait_time = self.find_optimal_wait_time(minimum_time=self.seconds_per_requests_customs)
                        time.sleep(wait_time)
                        return self.save_song_cache_to_database(song, custom=True)
                elif current_page == 0:
                    stop_running = True
                    message_logger("LEADERBOARDS API", "[SONG \"" + song + "\"] This leaderboard has 0 pages.")
            if stop_running == False:
                message_logger("LEADERBOARDS API", "[SONG \"" + song + "\"] Page "+ str(current_page) + " of " + str(total_pages) + " saved. " + \
                               str(self.requests_left) + " of " + str(self.requests_per_hour) + " requests left.")
            if self.loop_running == False:
                stop_running = True
            current_page = current_page + 1
            if custom == False:
                wait_time = self.find_optimal_wait_time(minimum_time=self.seconds_per_requests)
                time.sleep(wait_time)
            elif custom == True:
                wait_time = self.find_optimal_wait_time(minimum_time=self.seconds_per_requests_customs)
                time.sleep(wait_time)
                
    def sort_scores(self, scores):
        sort = make_custom_sort([['developer', 'difficulty', 'fullcombo', 'percent', 'platform', 'platform_id', 'rank', 'score', 'timestamp', 'user']])
        scoresSorted = sort(scores)
        return scoresSorted
            
    def save_song_cache_to_database(self, song, custom=False):
        if custom == True:
            song_file = self.leaderboards_database_folder + os.sep + "CUSTOMS" + os.sep + song + ".json"
        else:
            song_file = self.leaderboards_database_folder + os.sep + song + ".json"
        cache_folder = self.leaderboards_cache_folder + os.sep + song
        cache_files = [f for f in os.listdir(cache_folder) if os.path.isfile(os.path.join(cache_folder, f))]
        temp = []
        songjson = []
        oldjson = []
        if custom == True:
            try:
                f = open(song_file, "r")
                temp = json.load(f)
                f.close()
                for item in temp:
                    oldjson.append(self.sort_scores(item))
            except:
                pass
        if custom == False:
            users = user_list()
            users.load()
        new_users = 0
        changed_users = 0
        for file in cache_files:
            file_name = cache_folder + os.sep + file
            f = open(file_name, "r")
            fjson = json.load(f)
            f.close()
            for entry in fjson["leaderboard"]["data"]:
                for e in entry:
                    e["timestamp"] = os.stat(file_name).st_mtime
                    songjson.append(self.sort_scores(e))
                    platform_id = e["platform_id"]
                    if custom == False:
                        database_name = users.get_name(platform_id)
                        if database_name == None:
                            users.add(e["user"], e["platform_id"], e["developer"])
                            new_users = new_users + 1
                        else:
                            if database_name != e["user"]:
                                users.change_name(e["user"], e["platform_id"], e["developer"])
                                changed_users = changed_users + 1
                    else:
                        temp = self.users_to_check
                        for item in temp:
                            found = False
                            if item["platform_id"] == platform_id:
                                found = True
                            if found == False:
                                self.users_to_check.append(users_to_check)
        songjsonsorted = sorted(songjson, key=lambda k: k["rank"])
        with open(song_file, "w") as f:
            json.dump(songjsonsorted, f, sort_keys=True, indent=4)
        shutil.rmtree(cache_folder)
        if custom == False:
            message_logger("LEADERBOARDS API", "[SONG \"" + song + "\"] Leaderboard database saved!")
        else:
            message_logger("CUSTOMS LEADERBOARDS", "[SONG \"" + song[:-33] + "\"] Leaderboard database saved!")
        if custom == False:
            for e in self.users_to_check:
                database_name = users.get_name(e["platform_id"])
                if database_name == None:
                    users.add(e["user"], e["platform_id"], e["developer"])
                    new_users = new_users + 1
                else:
                    if database_name != e["user"]:
                        users.change_name(e["user"], e["platform_id"], e["developer"])
                        changed_users = changed_users + 1
            self.users_to_check = []
            users_string = "[SONG \"" + song + "\"]"
            users.save()
            if new_users > 0:
                users_string =  users_string + " " + str(new_users) + " new users has been added to the user list."
            if changed_users > 0:
                users_string = users_string + " " + str(changed_users) + " users has changed their name."
            users_string = users_string + " There are " + str(len(users.users["users"])) + " users."
        if custom == True:
            return oldjson, songjsonsorted
        else:
            message_logger("LEADERBOARDS API", users_string)
            
    def update_loop(self):
        self.loop_running = True
        state = []
        state_file = self.leaderboards_cache_folder + os.sep + "state.json"
        if os.path.isfile(state_file):
            f = open(state_file, "r")
            state = json.load(f)
            f.close()
            for song in self.ost:
                if song != "all_time_leaders" and song != "all_time_totals":
                    song_found = False
                    for item in state:
                        if item["song"] == song:
                            song_found = True
                            break
                    if song_found == False:
                        self.cache_song_leaderboard(song)
        else:
            for song in self.ost:
                if song != "all_time_leaders" and song != "all_time_totals":
                    self.cache_song_leaderboard(song)
                    f = open(state_file, "r")
                    state = json.load(f)
                    f.close()
        for item in state:
            if item["update_finished"] == 0:
                self.cache_song_leaderboard(item["song"], current_page=item["current_page"] + 1)
        while (self.loop_running == True):
            if self.loop_running == False:
                break
            else:
                f = open(state_file, "r")
                state = json.load(f)
                f.close()
                lowest_time = time.time()
                song_to_update = ""
                for item in state:
                    if item["update_finished"] < lowest_time:
                        song_to_update = item["song"]
                        lowest_time = item["update_start"]
                self.cache_song_leaderboard(song_to_update)
                
class user_list():
    users = {"users": []}
    filename = "user_list.json"
    backup = "user_list_backup.json"
    
    mappers1 = []
    mappers2 = []
    
    def __init__(self):
        f = open("mapper_icon1.txt", "r")
        for line in f:
            self.mappers1.append(line.replace("\n", ""))
        f.close()
        f = open("mapper_icon2.txt", "r")
        for line in f:
            self.mappers2.append(line.replace("\n", ""))
        f.close()
        
    def get_mappers(self):
        mappers = []
        for user in self.users["users"]:
            if user["mapper"] != 0:
                mappers.append(user)
        return mappers
    
    def get_developers(self):
        developers = []
        for user in self.users["users"]:
            if user["developer"] == True:
                developers.append(user)
        return developers
                
    def get_steam_users(self):
        steam_users = []
        for user in self.users["users"]:
            if user["platform"] == "steam":
                steam_users.append(user)
        return steam_users
        
    def get_oculus_users(self):
        oculus_users = []
        for user in self.users["users"]:
            if user["platform"] == "oculus":
                oculus_users.append(user)
        return oculus_users
        
    def get_viveport_users(self):
        viveport_users = []
        for user in self.users["users"]:
            if user["platform"] == "viveport":
                viveport_users.append(user)
        return viveport_users
    
    def add(self, user_name, platform_id, developer):
        user = {}
        user["name"] = user_name
        user["platform_id"] = platform_id
        user["developer"] = developer
        if platform_id in self.mappers1:
            user["mapper"] = 1
        elif platform_id in self.mappers2:
            user["mapper"] = 2
        else:
            user["mapper"] = 0
        self.users["users"].append(user)
        
    def get_id(self, user_name):
        for c in self.users["users"]:
            if c["name"] == user_name:
                return c["platform_id"]
                
    def get_name(self, platform_id):
        for c in self.users["users"]:
            if c["platform_id"] == platform_id:
                return c["name"]
                
    def change_name(self, user_name, platform_id, developer):
        temp_dict = {"users": []}
        for c in self.users["users"]:
            if c["platform_id"] == platform_id:
                continue
            temp_dict["users"].append(c)
        self.users = temp_dict
        self.add(user_name, platform_id, developer)
                
    def load(self):
        try:
            try:
                f = open(self.filename, "r")
                self.users = json.load(f)
            except:
                f = open(self.backup, "r")
                self.users = json.load(f)
            f.close()
        except:
            print("User list does not exist.")
        
    def save(self):
        shutil.copyfile(self.filename, self.backup)
        with open(self.filename, "w") as f:
            json.dump(self.users, f, indent=4)
                
class friend_codes():

    friend_codes = {"friend_codes": []}
    
    filename = "friend_codes.json"
    backup = "friend_codes_backup.json"
    
    def add(self, code, user_id):
        friend_code = {}
        friend_code["friend_code"] = code
        friend_code["discord_id"] = user_id
        self.friend_codes["friend_codes"].append(friend_code)
        
    def delete(self, code, user_id):
        temp_dict = {"friend_codes": []}
    
        for c in self.friend_codes["friend_codes"]:
            if c["discord_id"] == user_id:
                if c["friend_code"] == code:
                    continue
            temp_dict.append(c)
        
        self.friend_codes = temp_dict
        
    def get_code(self, user_id):
        for c in self.friend_codes["friend_codes"]:
            if c["discord_id"] == user_id:
                return c["friend_code"]
                
    def get_id(self, code):
        for c in self.friend_codes["friend_codes"]:
            if c["friend_code"] == code:
                return c["discord_id"]
                
    def load(self):
        try:
            try:
                f = open(self.filename, "r")
                self.friend_codes = json.load(f)
            except:
                f = open(self.backup, "r")
                self.friend_codes = json.load(f)
            f.close()
        except:
            print("Friend code list does not exist.")
                
    def save(self):
        shutil.copyfile(self.filename, self.backup)
        with open(self.filename, "w") as f:
            json.dump(self.friend_codes, f, indent=4)
        
api = leaderboards_api()
# raw_list = api.request_leaderboards_list()
# rjson = json.loads(raw_list)
# for item in rjson:
    # print(item)
#api.post_request(["destiny", "collider"], ["steam_76561198049415849"])
#print(api.ost)
#api.update_loop()
#api.save_song_cache_to_database("golddust")
#r = requests.get(api.base_url + api.leaderboard_base_url + "all_time_totals", headers=api.headers)
#print(r.text)
# print(api.ost)
# print(api.global_songs)
# print(api.extra_songs)
# print(api.dlc)
api.get_leaderboard_stats()