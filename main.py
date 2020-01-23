import bot_commands
import bot_top20
import bot_twitch
import bot_customs
import bot_mixer
import asyncio
import time

from threading import Thread
from audica_leaderboards import leaderboards_api
from tools import message_logger

api = leaderboards_api()

BotToken = "YOUR_DISCORD_BOT_TOKEN"

def audica_leaderboards_update_loop():
    try:
        while True:
            try:
                message_logger("LEADERBOARDS API", "Automatic update of the full leaderboards is starting...")
                api.update_loop()
            except Exception as e:
                message_logger("LEADERBOARDS API", "Error, printing the error on the next line and waiting 30 seconds...")
                message_logger("LEADERBOARDS API", str(e))
                time.sleep(30)
    except:
        message_logger("LEADERBOARDS API", "Error, loop crashed unexpectedly, will restart the loop in 30 seconds...")
        message_logger("LEADERBOARDS API", str(e))
        time.sleep(30)
            
api_loop_thread = Thread(target=audica_leaderboards_update_loop)
api_loop_thread.start()

commands_bot = bot_commands.client
top20_bot = bot_top20.client
twitch_bot = bot_twitch.client
mixer_bot = bot_mixer.client
customs_bot = bot_customs.client

bot_commands.api = api
bot_top20.api = api
bot_customs.api = api

loop = asyncio.get_event_loop()
task1 = loop.create_task(commands_bot.start(BotToken))
task2 = loop.create_task(top20_bot.start(BotToken))
task3 = loop.create_task(twitch_bot.start(BotToken))
task4 = loop.create_task(customs_bot.start(BotToken))
task5 = loop.create_task(mixer_bot.start(BotToken))
gathered = asyncio.gather(task1, task2, task3, task4, task5, loop=loop)

loop.run_until_complete(gathered)