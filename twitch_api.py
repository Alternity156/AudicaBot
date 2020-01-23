import requests
import time
import os
import json
import datetime
import shutil
import glob

from urllib import request, parse

class twitch_api():
    
    twitch_api_key = "YOUR_TWITCH_API_KEY"
    base_url = "https://api.twitch.tv/helix"
    search_streams_url = "/streams"
    search_games_url = "/games"
    search_users_url = "/users"

    headers = {
               'Accept': "application/vnd.twitch.tv.v5+json",
               'Client-ID': twitch_api_key
              }
              
    live_streams = []
    
    audica_game_id = 0
    
    file_name = "live_twitch_streams.json"
    
    def __init__(self):
        self.get_audica_game_id()
        self.load_live_streams()
              
    def get_audica_streams(self):
        r = requests.get(self.base_url + self.search_streams_url + "?game_id=" + self.audica_game_id, headers=self.headers)
        rjson = json.loads(r.text)
        streams = []
        for stream in rjson["data"]:
            found = False
            for s in streams:
                if stream["id"] == s["id"]:
                    found = True
            if found == False:
                streams.append(stream)
        return streams
        
    def get_audica_game_id(self):
        r = requests.get(self.base_url + self.search_games_url + "?name=Audica", headers=self.headers)
        rjson = json.loads(r.text)
        self.audica_game_id = rjson["data"][0]["id"]
        
    def get_user(self, id):
        r = requests.get(self.base_url + self.search_users_url + "?id=" + str(id), headers=self.headers)
        rjson = json.loads(r.text)
        return rjson
        
    def update_live_streams(self):
        current_live_streams = self.get_audica_streams()
        streams_list = []
        new_streams_list = []
        for stream in current_live_streams:
            user_id = stream["user_id"]
            found = False
            for s in self.live_streams:
                if s["user_id"] == user_id:
                    found = True
            if found == False:
                new_streams_list.append(stream)
            streams_list.append(stream)
        self.live_streams = streams_list
        self.save_live_streams()
        return new_streams_list
        
    def load_live_streams(self):
        try:
            f = open(self.file_name, "r")
            self.live_streams = json.load(f)
            f.close()
        except:
            print("\"" + self.file_name + "\" does not exist.")
        
    def save_live_streams(self):
        with open(self.file_name, "w") as f:
            json.dump(self.live_streams, f, indent=4)
        
    
#api = twitch_api()
# api.load_live_streams()
#while True:
    #print(api.get_audica_streams())
    #time.sleep(30)