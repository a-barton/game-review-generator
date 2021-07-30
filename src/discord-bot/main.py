import discord
import os
import re
import requests
import json

from discord.errors import ClientException

client = discord.Client()

steam_url_regex = re.compile(r'(?:https://store.steampowered.com/app/)([0-9]+)(?:/)')
app_details_url = "http://store.steampowered.com/api/appdetails?appids="

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")

    if message.content.startswith("https://store.steampowered.com/app/"):
        print('Detected Steam URL')
        app_id = re.match(steam_url_regex, message.content).group(1)
        app_details_resp = requests.get(app_details_url + app_id).json()[app_id]["data"]
        app_desc = app_details_resp["detailed_description"]
        app_name = app_details_resp["name"]
        app_desc = re.sub("<[^<]+?>", " ", app_desc)
        review = poll_transformer_api(app_desc)
        await message.channel.send(f"Here's my take on {app_name} \n ```" + review + "```")

def poll_transformer_api(prompt):
    api_endpoint = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-2.7B"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_TOKEN')}"}
    payload = {
        "inputs" : prompt,
        'parameters' : {
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

client.run(os.getenv("DISCORD_BOT_TOKEN"))