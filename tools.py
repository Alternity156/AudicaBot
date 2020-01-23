from zipfile import ZipFile
from mutagen.oggvorbis import OggVorbis
from collections import OrderedDict

import json
import os
import datetime
import glob
import midi
import struct
import shutil

ost_songlist = ["addictedtoamemory.audica",
                "adrenaline.audica",
                "boomboom.audica",
                "breakforme.audica",
                "collider.audica",
                "decodeme.audica",
                "destiny.audica",
                "eyeforaneye.audica",
                "gametime.audica",
                "golddust.audica",
                "highwaytooblivion_short",
                "hr8938cephei.audica",
                "ifeellove.audica",
                "iwantu.audica",
                "lazerface.audica",
                "overtime.audica",
                "perfectexceeder.audica",
                "popstars.audica",
                "predator.audica",
                "raiseyourweapon_noisia.audica",
                "resistance.audica",
                "smoke.audica",
                "splinter.audica",
                "synthesized.audica",
                "thespace.audica",
                "timeforcrime.audica",
                "tothestars.audica",
                "tutorial.audica"]
                
extras_songlist = ["highwaytooblivion_full"]

class desc():
    
    songID = ""
    moggSong = ""
    title = ""
    artist = ""
    midiFile = ""
    targetDrums = ""
    fusionSpatialized = "fusion/guns/default/drums_default_spatial.fusion"
    fusionUnspatialized = "fusion/guns/default/drums_default_sub.fusion"
    sustainSongRight = ""
    sustainSongLeft = ""
    fxSong = ""
    tempo = 0.0
    songEndEvent = ""
    highScoreEvent = ""
    songEndPitchAdjust = 0.0
    prerollSeconds = 0.0
    previewStartSeconds = 0.0
    useMidiForCues = False
    hidden = False
    offset = 0
    author = ""
        
    def load_desc_file(self, file):
        try:
            f = open(file, 'r')
        except:
            f = file
        try:
            desc_file = json.load(f)
        except:
            desc_file = json.loads(f)
        self.songID = desc_file["songID"]
        self.moggSong = desc_file["moggSong"]
        self.title = desc_file["title"]
        self.artist = desc_file["artist"]
        try:
            self.author = desc_file["author"]
        except:
            try:
                self.author = desc_file["mapper"]
            except:
                pass
        self.midiFile = desc_file["midiFile"]
        try:
            self.targetDrums = desc_file["targetDrums"]
            if self.targetDrums == "":
                self.targetDrums = "fusion/target_drums/destruct.json"
        except:
            self.fusionSpatialized = desc_file["fusionSpatialized"]
            self.targetDrums = "fusion/target_drums/destruct.json"
            try:
                self.fusionUnspatialized = desc_file["fusionUnspatialized"]
            except:
                pass
        self.sustainSongRight = desc_file["sustainSongRight"]
        self.sustainSongLeft = desc_file["sustainSongLeft"]
        self.fxSong = desc_file["fxSong"]
        try:
            self.tempo = desc_file["tempo"]
        except:
            pass
        self.songEndEvent = desc_file["songEndEvent"][25:]
        try:
            self.highScoreEvent = desc_file["highScoreEvent"][34:]
        except:
            pass
        try:
            self.songEndPitchAdjust = desc_file["songEndPitchAdjust"]
        except:
            pass
        self.prerollSeconds = desc_file["prerollSeconds"]
        try:
            self.previewStartSeconds = desc_file["previewStartSeconds"]
        except:
            pass
        self.useMidiForCues = desc_file["useMidiForCues"]
        self.hidden = desc_file["hidden"]
        try:
            self.offset = desc_file["offset"]
        except:
            pass
        try:
            f.close()
        except:
            pass
        
    def save_desc_file(self, file):
        line = "{\n"
        line = line + "\t\"songID\": " + json.dumps(self.songID) + ",\n"
        line = line + "\t\"moggSong\": " + json.dumps(self.moggSong) + ",\n"
        line = line + "\t\"title\": " + json.dumps(self.title) + ",\n"
        line = line + "\t\"artist\": " + json.dumps(self.artist) + ",\n"
        line = line + "\t\"author\": " + json.dumps(self.author) + ",\n"
        line = line + "\t\"midiFile\": " + json.dumps(self.midiFile) + ",\n"
        line = line + "\t\"targetDrums\": " + json.dumps(self.targetDrums) + ",\n"
        line = line + "\t\"sustainSongRight\": " + json.dumps(self.sustainSongRight) + ",\n"
        line = line + "\t\"sustainSongLeft\": " + json.dumps(self.sustainSongLeft) + ",\n"
        line = line + "\t\"fxSong\": " + json.dumps(self.fxSong) + ",\n"
        line = line + "\t\"songEndEvent\": " + json.dumps("event:/song_end/song_end_" + self.songEndEvent) + ",\n"
        line = line + "\t\"highScoreEvent\": " + json.dumps("event:/results/results_high_score_" + self.highScoreEvent) + ",\n"
        line = line + "\t\"songEndPitchAdjust\": " + json.dumps(self.songEndPitchAdjust) + ",\n"
        line = line + "\t\"prerollSeconds\": " + json.dumps(self.prerollSeconds) + ",\n"
        line = line + "\t\"previewStartSeconds\": " + json.dumps(self.previewStartSeconds) + ",\n"
        line = line + "\t\"useMidiForCues\": " + json.dumps(self.useMidiForCues) + ",\n"
        templine = line + "\t\"hidden\": " + json.dumps(self.hidden) + ",\n"
        if self.offset != 0:
            line = templine + ",\n"
        else:
            line = templine + "\n"
        templine = line + "\t\"offset\": " + json.dumps(self.offset)
        if self.offset != 0:
            line = templine + "\n"
        line = line + "}"
        
        f = open(file, "w")
        f.write(line)
        f.close()
        
class custom_song():

    desc_file = desc()
    
    leaderboard_id = ""
    song_length = 0.0 #in seconds
    tempos = []
    low_tempo = 0
    high_tempo = 0
    
    download_url = ""
    uploader = 0
    upload_time = 0
    beginner = False
    standard = False
    advanced = False
    expert = False
    video_url = ""
    filename = ""
    estimated_expert_difficulty = 0.0
    estimated_advanced_difficulty = 0.0
    estimated_standard_difficulty = 0.0
    estimated_beginner_difficulty = 0.0
    
    def __init__(self, file):
        self.filename = file
        self.audica_file = ZipFile(file)
        
        self.desc_file.load_desc_file(self.audica_file.open("song.desc").read().decode("utf-8"))
        
        self.audica_file.extract(self.get_main_audio_filename())
        self.mogg2ogg(self.get_main_audio_filename(), self.get_main_audio_filename().replace(".mogg", ".ogg"))
        f = OggVorbis(self.get_main_audio_filename().replace(".mogg", ".ogg"))
        self.song_length = f.info.length #length in seconds
        os.remove(self.get_main_audio_filename())
        os.remove(self.get_main_audio_filename().replace(".mogg", ".ogg"))
        
        self.audica_file.extract(self.desc_file.midiFile)
        self.get_tempos_from_midi(self.desc_file.midiFile)
        self.get_difficulties()
        os.remove(self.desc_file.midiFile)

    def mogg2ogg(self, input_file, output_file):
        with open(input_file, "rb") as f:
            byte_array = f.read()
            new_bytes = byte_array[struct.unpack('<i', bytes([byte_array[4] ,byte_array[5], byte_array[6], byte_array[7]]))[0]:]
            f = open(output_file, "wb")
            f.write(new_bytes)
        f.close()
        
    def get_main_audio_filename(self):
        f = self.audica_file.open(self.desc_file.moggSong).read().decode("utf-8")
        temp_string = ""
        lines = []
        for char in f:
            temp_string = temp_string + char
            if char == "\n":
                lines.append(temp_string)
                temp_string = ""
        for line in lines:
            line = line
            if "mogg_path" in line:
                return line.replace("(mogg_path \"", "").split("\")")[0]
                
    def get_tempos_from_midi(self, midi_file):
        pattern = midi.read_midifile(midi_file)
        
        tempos = []

        for track in pattern:
            for event in track:
                if type(event) is midi.SetTempoEvent:
                    tempos.append(event.get_bpm())
        
        first_tempo = False
        
        for tempo in tempos:
            if first_tempo == False:
                first_tempo = True
                self.low_tempo = tempo
                self.high_tempo = tempo
            else:
                if tempo < self.low_tempo:
                    self.low_tempo = tempo
                elif tempo > self.high_tempo:
                    self.high_tempo = tempo
        
    def get_difficulties(self):
        if self.desc_file.useMidiForCues == False:
            for item in self.audica_file.infolist():
                if item.filename == "expert.cues":
                    if item.file_size > 599:
                        self.expert = True
                if item.filename == "advanced.cues":
                    if item.file_size > 599:
                        self.advanced = True
                if item.filename == "moderate.cues":
                    if item.file_size > 599:
                        self.standard = True
                if item.filename == "beginner.cues":
                    if item.file_size > 599:
                        self.beginner = True
        else:
            pattern = midi.read_midifile(self.desc_file.midiFile)
            for track in pattern:
                for event in track:
                    if type(event) is midi.TrackNameEvent:
                        if "Expert" in event.text:
                            self.expert = True
                        if "Hard" in event.text:
                            self.advanced = True
                        if "Normal" in event.text:
                            self.standard = True
                        if "Easy" in event.text:
                            self.beginner = True
                            
    def get_song_data(self):
        song_data = {}
        song_data["filename"] = self.filename.split(os.sep)[-1]
        song_data["song_id"] = self.desc_file.songID
        song_data["leaderboard_id"] = self.leaderboard_id
        song_data["title"] = self.desc_file.title
        song_data["artist"] = self.desc_file.artist
        song_data["drum_kit"] = self.desc_file.targetDrums.split("/")[-1].replace(".json", "")
        song_data["midi_for_cues"] = self.desc_file.useMidiForCues
        song_data["author"] = self.desc_file.author
        song_data["low_tempo"] = self.low_tempo
        song_data["high_tempo"] = self.high_tempo
        song_data["song_length"] = self.song_length
        song_data["download_url"] = self.download_url
        song_data["expert"] = self.expert
        song_data["advanced"] = self.advanced
        song_data["standard"] = self.standard
        song_data["beginner"] = self.beginner
        song_data["uploader"] = self.uploader
        song_data["upload_time"] = self.upload_time
        song_data["video_url"] = self.video_url
        return song_data
        
#song = custom_song("AUDICA" + os.sep + "CUSTOMS" + os.sep + "poppyxtest.audica")
#print(song.get_song_data())
        
class unknown_leaderboard_ids():
    leaderboard_ids = []
    folder = "AUDICA" + os.sep + "CUSTOMS" + os.sep
    filename = "unknown_leaderboard_ids.json"
    backup_filename = "unknown_leaderboard_ids_backup.json"
    
    def add(self, leaderboard_id, timestamp):
        entry = {}
        entry["leaderboard_id"] = leaderboard_id
        entry["timestamp"] = timestamp
        self.leaderboard_ids.append(entry)
        
    def delete(self, leaderboard_id):
        temp_ids = []
        for id in self.leaderboard_ids:
            if id["leaderboard_id"] != leaderboard_id:
                temp_ids.append(id)
        self.leaderboard_id = temp_ids
    
    def load(self):
        try:
            try:
                f = open(self.folder + self.filename, "r")
                self.leaderboard_ids = json.load(f)
            except:
                f = open(self.folder + self.backup_filename, "r")
                self.leaderboard_ids = json.load(f)
            f.close()
        except:
            print("Unknown leaderboard IDs does not exist.")
        
    def save(self):
        try:
            shutil.copyfile(self.folder + self.filename, self.folder + self.backup_filename)
        except:
            pass
        with open(self.folder + self.filename, "w") as f:
            json.dump(self.leaderboard_ids, f, indent=4)

class customs_database():

    song_list = []
    
    folder = "AUDICA" + os.sep + "CUSTOMS" + os.sep
    filename = "customs_database.json"
    backup_filename = "customs_database_backup.json"
    
    def add(self, song):
        for s in self.song_list:
            if s["song_id"] == song["song_id"]:
                return False
        self.song_list.append(song)
        
    def delete(self, song_id):
        temp_songs = []
        for s in self.song_list:
            if s["song_id"] != song_id:
                temp_songs.append(s)
        self.song_list = temp_songs
        
    def get_song(self, song_id):
        for s in self.song_list:
            if s["song_id"] == song_id:
                return s
        return False
    
    def get_song_with_filename(self, filename):
        for s in self.song_list:
            if s["filename"] == filename:
                return s
        return False
        
    def wipe_leaderboard_ids(self):
        temp_songs = []
        for s in self.song_list:
            s["leaderboard_id"] = ""
            temp_songs.append(s)
        self.song_list = temp_songs
                
    def edit_leaderboard_id(self, song_id, leaderboard_id):
        temp_songs = []
        for s in self.song_list:
            if s["song_id"] == song_id:
                s["leaderboard_id"] = leaderboard_id
            temp_songs.append(s)
        self.song_list = temp_songs
                
    def load(self):
        try:
            try:
                f = open(self.folder + self.filename, "r")
                self.song_list = json.load(f)
            except:
                f = open(self.folder + self.backup_filename, "r")
                self.song_list = json.load(f)
            f.close()
        except:
            print("Customs database does not exist.")
        
    def save(self):
        try:
            shutil.copyfile(self.folder + self.filename, self.folder + self.backup_filename)
        except:
            pass
        with open(self.folder + self.filename, "w") as f:
            json.dump(self.song_list, f, indent=4)
    
def get_tempos_from_midi(midi_file):
    pattern = midi.read_midifile(midi_file)
    
    tempos = []

    for track in pattern:
        for event in track:
            if type(event) is midi.SetTempoEvent:
                tempos.append(event.get_bpm())
    return tempos
    
def mogg2ogg(input_file, output_file):
    with open(input_file, "rb") as f:
        bytes = f.read()
        new_bytes = bytes[struct.unpack('<i', bytes[4] + bytes[5] + bytes[6] + bytes[7])[0]:]
        f = open(output_file, "wb")
        f.write(new_bytes)
    f.close()

def message_logger(type, message):
    log_message = "[" + str(datetime.datetime.now()).split(".")[0] + "][" + type + "] " + message
    if os.path.isfile("log.txt"):
        with open("log.txt", "a") as myfile:
            myfile.write(log_message + "\n")
    else:
        with open("log.txt", "w") as myfile:
            myfile.write(log_message + "\n")
    print(log_message)
    
def parse_leaderboards_args(args):
    songid_arg_name = ['-s', "--songid"]
    platform_arg_name = ["-p", "--platform"]
    user_arg_name = ["-u", "--user"]
    difficulty_arg_name = ["-d", "--difficulty"]
    harmonix_arg_name = ["-hmx", "--harmonix"]
    
    parsed_args = {}
    args_copy = args
    index = 0
    
    for arg in args:
        if arg == songid_arg_name[0] or arg == songid_arg_name[1]:
            parsed_args["songid"] = args_copy[index + 1]
        if arg == platform_arg_name[0] or arg == platform_arg_name[1]:
            parsed_args["platform"] = args_copy[index + 1]
        if arg == user_arg_name[0] or arg == user_arg_name[1]:
            parsed_args["user"] = args_copy[index + 1]
        if arg == difficulty_arg_name[0] or arg == difficulty_arg_name[1]:
            parsed_args["difficulty"] = args_copy[index + 1]
        if arg == harmonix_arg_name[0] or arg == harmonix_arg_name[1]:
            parsed_args["harmonix"] = True
        index = index + 1
        
    try:
        parsed_args["songid"]
    except:
        parsed_args["songid"] = ""
    try:
        parsed_args["user"]
    except:
        parsed_args["user"] = ""
    try:
        parsed_args["platform"]
    except:
        parsed_args["platform"] = "all"
    try:
        parsed_args["difficulty"]
    except:
        parsed_args["difficulty"] = "all"
    try:
        parsed_args["harmonix"]
    except:
        parsed_args["harmonix"] = False
        
    if parsed_args["songid"] == "" and parsed_args["user" == ""]:
        return False
    else:
        return parsed_args
        
def make_custom_sort(orders):
    orders = [{k: -i for (i, k) in enumerate(reversed(order), 1)} for order in orders]
    def process(stuff):
        if isinstance(stuff, dict):
            l = [(k, process(v)) for (k, v) in stuff.items()]
            keys = set(stuff)
            for order in orders:
                if keys.issuperset(order):
                    return OrderedDict(sorted(l, key=lambda x: order.get(x[0], 0)))
            return OrderedDict(sorted(l))
        if isinstance(stuff, list):
            return [process(x) for x in stuff]
        return stuff
    return process
        
def midi_to_cues(midifile, difficulty):
    
    if difficulty == "expert":
        difficulty = "Expert"
    elif difficulty == "advanced":
        difficulty = "Hard"
    elif difficulty == "moderate" or difficulty == "standard" or difficulty == "standart":
        difficulty = "Normal"
    elif difficulty == "beginner":
        difficulty = "Easy"

    pattern = midi.read_midifile(midifile)

    active_notes = []
    targets = []
    repeaters = []
    tempos = []
    targetSpeed = 1

    pattern.make_ticks_abs()
    
    skip_iteration = False

    for track in pattern:

        for event in track:
            if type(event) is midi.SetTempoEvent:
                tempo_marker = {}
                tempo_marker["tempo"] = event.get_bpm()
                tempo_marker["tick"] = event.tick
                    
                tempos.append(tempo_marker)

        handType = 0
        for event in track:
            if type(event) is midi.TrackNameEvent:
                if "RH" in event.text:
                    handType = 1
                if "LH" in event.text:
                    handType = 2
                if difficulty not in event.text:
                    skip_iteration = True
        
        if skip_iteration == True:
            skip_iteration = False
            continue

        ccs = []
        for event in track:
            if type(event) is midi.ControlChangeEvent:
                if event.get_control() == 16 or event.get_control() == 17:
                    ccs.append(event)

        for event in track:
            if type(event) is midi.NoteOnEvent:
                active_notes.append(event)
            if type(event) is midi.NoteOffEvent:
                for active_note in active_notes:
                    if active_note.get_pitch() == event.get_pitch():
                        if active_note.get_pitch() < 107:
                            target = {}

                            length = event.tick - active_note.tick
                            channel = event.channel

                            offsetX = 0
                            offsetY = 0
                            offsetZ = 0
                            for cc in ccs:
                                if abs(active_note.tick - cc.tick) <= 10:
                                    if cc.get_control() == 16:
                                       offsetX = (cc.get_value() - 64) / 64.0
                                    if cc.get_control() == 17:
                                       offsetY = (cc.get_value() - 64) / 64.0
                                    if cc.get_control() == 18:
                                       offsetZ = (cc.get_value() - 64) / 64.0
                                    if cc.get_control() == 19:
                                       offsetX += (cc.get_value() - 64)
                                    if cc.get_control() == 20:
                                       offsetY += (cc.get_value() - 64)
                                    if cc.get_control() == 21:
                                       offsetZ += (cc.get_value() - 64)

                            behavior = 0
                            if active_note.get_pitch() == 98 or active_note.get_pitch() == 99 or active_note.get_pitch() == 100 or active_note.get_pitch() == 101:
                                behavior = 6
                            elif length > 240:
                                behavior = 3
                            elif channel == 1:
                                behavior = 2
                            elif channel == 2:
                                behavior = 1
                            elif channel == 3:
                                behavior = 4
                            elif channel == 4:
                                behavior = 5

                            target["tick"] = active_note.tick
                            target["tickLength"] = length
                            target["pitch"] = active_note.get_pitch()
                            target["velocity"] = active_note.get_velocity()
                            target["gridOffset"] = {}
                            target["gridOffset"]["x"] = offsetX
                            target["gridOffset"]["y"] = offsetY
                            target["zOffset"] = offsetZ
                            target["handType"] = handType
                            target["behavior"] = behavior

                            targets.append(target)
                        else:
                            repeater = {}
                            repeater["handType"] = handType
                            repeater["tick"] = active_note.tick
                            repeater["tickLength"] = event.tick - active_note.tick
                            repeater["pitch"] = active_note.get_pitch()
                            repeater["velocity"] = active_note.get_velocity()
                            repeaters.append(repeater)
                        for i in range(len(active_notes)): 
                            if active_notes[i].get_pitch() == active_note.get_pitch(): 
                                del active_notes[i] 
                                break
                        break

    sort = make_custom_sort([['tick', 'tickLength', 'pitch', 'velocity', 'gridOffset', 'handType', 'behavior']])
    targetsSorted = sort(targets)

    cues = {}
    cues['cues'] = sorted(targetsSorted, key=lambda x: x['tick'])
    cues['repeaters'] = repeaters
    cues['tempos'] = tempos

    return cues
    
def calculate_stars(song, difficulty, score, custom=False):
    ost_folder = "AUDICA" + os.sep + "OST"
    customs_folder = "AUDICA" + os.sep + "CUSTOMS"
    if custom == False:
        files = [f for f in glob.glob(ost_folder + os.sep + "**/*.audica", recursive=True)]
    else:
        files = [f for f in glob.glob(customs_folder + os.sep + "**/*.audica", recursive=True)]
    found = False
    for f in files:
        if song.lower() + ".audica" == f.lower().split(os.sep)[-1:][0]:
            song = f.split(os.sep)[-1:][0]
            found = True
            break
    if found == False:
        for f in files:
            if song.lower() in f.lower():
                song = f.split(os.sep)[-1:][0]
                break
    if custom == False:
        audica_file = ost_folder + os.sep + song
    else:
        audica_file = customs_folder + os.sep + song
    zf = ZipFile(audica_file)
    if custom == True:
        song = custom_song(audica_file)
        if song.desc_file.useMidiForCues == False:
            f = zf.open(difficulty + ".cues")
            fjson = json.loads(f.read().decode("utf-8"))
            f.close()
        else:
            for item in zf.namelist():
                if ".mid" in item:
                    zf.extract(item)
                    fjson = midi_to_cues(item, difficulty)
                    os.remove(item)
                    break
    else:
        f = zf.open(difficulty + ".cues")
        fjson = json.loads(f.read().decode("utf-8"))
        f.close()
    max_score = 0
    streak = 0
    for cue in fjson["cues"]:
        base_score = 0
        if cue["behavior"] == 0 or cue["behavior"] == 1 or cue["behavior"] == 2 or cue["behavior"] == 4 or cue["behavior"] == 6:
            base_score = 2000
        elif cue["behavior"] == 3:
            base_score = 3000
        elif cue["behavior"] == 5:
            base_score = 125
        if cue["behavior"] != 5:
            streak = streak + 1
        if streak > 29:
            final_score = base_score * 4
            max_score = max_score + final_score
        elif streak > 19:
            final_score = base_score * 3
            max_score = max_score + final_score
        elif streak > 9:
            final_score = base_score * 2
            max_score = max_score + final_score
        else:
            max_score = max_score + base_score
    percentage = 100.0 * score/max_score
    stars = 0 
    if percentage >= 90 and difficulty == "expert": # 90.2 maybe?
        stars = 6
    elif percentage >= 63.5:
        stars = 5
    elif percentage >= 42.5:
        stars = 4
    elif percentage >= 26.5:
        stars = 3
    elif percentage >= 10:
        stars = 2
    else:
        stars = 1
    return [stars, max_score]