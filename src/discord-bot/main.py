import discord
import os
import re

from discord.errors import ClientException

client = discord.Client()

steam_url_regex = re.compile(r'(?:https://store.steampowered.com/app/)([0-9]+)(?:/)')

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
        app_id = re.match(steam_url_regex, message.content).group()
        await message.channel.send(f'Found this app ID: {app_id}')

client.run(os.getenv('DISCORD_BOT_TOKEN'))