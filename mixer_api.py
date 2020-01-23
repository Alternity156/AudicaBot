import requests
import sys
import json

class mixer_api():

    clientid = "YOUR_MIXED_CLIENT_ID"

    game_search = "Audica"
    game_id = 0
    
    base_url = "https://mixer.com/api/v1/"
    game_id_search_url = "types?query="
    game_search_url = "channels?where=typeId:eq:"
    
    file_name = "live_mixer_streams.json"
    
    live_streams = []
    
    def __init__(self):

        self.s = requests.Session()
        self.s.headers.update({'Client-ID': self.clientid})
        self.get_game_id(self.game_search)
        self.load_live_streams()
        
    def get_game_id(self, game_name):

        response = self.s.get(self.base_url + self.game_id_search_url + game_name)

        for item in response.json():
            if item["name"] == self.game_search:
                self.game_id = item["id"]
        
    def get_streams(self):

        response = self.s.get(self.base_url + self.game_search_url + str(self.game_id))
        streams = []
        for stream in response.json():
            streams.append(stream)
        return streams

        return response.json()
        

    def update_live_streams(self):
        current_live_streams = self.get_streams()
        streams_list = []
        new_streams_list = []
        for stream in current_live_streams:
            user_id = stream["user"]["username"]
            found = False
            for s in self.live_streams:
                if s["user"]["username"] == user_id:
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
            
# api = mixer_api()
# print(api.update_live_streams())