import discord
import boto3
import os
import re
import requests
import json
import time

from utils import get_secret
from discord.errors import ClientException

client = discord.Client()

steam_url_regex = re.compile(r"(?:https://store.steampowered.com/app/)([0-9]+)(?:/)")
app_details_url = "http://store.steampowered.com/api/appdetails?appids="

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith("$hello"):
        await message.reply(f"Hello {message.author.display_name}!")

    if message.content.startswith("https://store.steampowered.com/app/"):
        print("Detected Steam URL")
        app_id = re.match(steam_url_regex, message.content).group(1)
        print("Extracted app ID from URL")
        app_name, app_desc = get_app_details(app_id)
        print("Retrieved app name and description from Steam:")
        print(f"App Name = {app_name}\nApp Description = {app_desc}")
        print("Polling transformer API to generate review")
        review = poll_transformer_api(app_desc)
        print(f"Type of 'review' object returned by transformer API: {type(review)}")
        print(f"Length of 'review' object returned by transformer API: {len(review)}")
        print("'review' object:")
        print(review)
        await message.reply(f"Here's my take on {app_name} \n```" + review + "```")

def get_app_details(app_id):
    request_successful = False
    time_started = time.time()
    time_taken = 0
    while not request_successful:
        base_resp = requests.get(app_details_url + app_id)
        time_taken = time.time() - time_started
        if base_resp.status_code != 200:
            if time_taken > 10:
                print("Steam app details request timing out")
                return None, None
            time.sleep(0.2)
            continue
        else:
            request_successful = True
            app_details = base_resp.json()[app_id]
            if not app_details.get("data", None):
                return None, None
            app_details_data = app_details["data"]
    app_name = app_details_data["name"]
    app_desc = re.sub("<[^<]+?>", " ", app_details_data["detailed_description"])
    return app_name, app_desc

def poll_transformer_api(prompt):
    api_endpoint = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-2.7B"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_TOKEN')}"}
    payload = {
        "inputs" : prompt,
        "parameters" : {
            "return_full_text" : False,
            "max_new_tokens" : 200
        }
    }
    review = query(payload, api_endpoint, headers)[0]["generated_text"]
    return review

def query(payload, API_URL, headers):
    data = json.dumps(payload)
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))

secret_name = "DISCORD_BOT_TOKEN"
bot_token = json.loads(get_secret(secret_name))[secret_name]
client.run(bot_token)