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
    
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('https://store.steampowered.com/app/'):
        print('Detected Steam URL')
        app_id = re.match(steam_url_regex, message.content).group(1)
        app_desc = requests.get(app_details_url + app_id).json()[app_id]['data']['detailed_description']
        app_desc = re.sub("<[^<]+?>", " ", app_desc)
        await message.channel.send(f'Game Description: ' + app_desc)

def poll_transformer_api(prompt):
    api_endpoint = "https://api-inference.huggingface.co/models/gpt-neo-2.7B"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    data = json.dumps(prompt)
    response = requests.request("POST", api_endpoint, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))

client.run(os.getenv('DISCORD_BOT_TOKEN'))