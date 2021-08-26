import discord
import boto3
import re
import requests
import json
import time
import click
import os
import random

from utils import get_secret

@click.command()
@click.option("--bucket", "bucket", required=True)
@click.option("--batch_job_queue", "batch_job_queue", required=True)
@click.option("--batch_job_definition", "batch_job_definition", required=True)
@click.option("--region", "region", required=True)
def main(bucket, batch_job_queue, batch_job_definition, region):

    client = discord.Client()
    steam_url_regex = re.compile(r"(?:https://store.steampowered.com/app/)([0-9]+)(?:/)")
    inference_input_key = "inference_input/prompt.txt"
    inference_output_key = "inference_output/generated.txt"

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
            try:
                print("Detected Steam URL")
                app_id = re.match(steam_url_regex, message.content).group(1)
                print("Extracted app ID from URL")
                app_name, app_desc = get_app_details(app_id)
                print("Retrieved app name and description from Steam:")
                print(f"App Name = {app_name}\nApp Description = {app_desc}")

                review_start = get_random_review_start(app_name)
                prompt = f"Game Description: {app_desc}\nReview: {review_start}"
                put_prompt_in_s3(prompt, bucket, inference_input_key)

                job_id = start_batch_job(batch_job_queue, batch_job_definition, region)
                job_outcome = wait_on_job_completion(job_id, region)

                if job_outcome == "FAILED" or job_outcome == "TIMEOUT":
                    print(f"Job unsuccessful: {job_outcome}")
                    return

                os.makedirs(app_id, exist_ok=True)
                inference_output = get_generated_review(bucket, inference_output_key, app_id)
                review = clean_output(inference_output, prompt, review_start)

                if "game-review-archive" in [channel.name for channel in message.guild.channels]:
                    channel_id = discord.utils.get(message.guild.text_channels, name='game-review-archive')
                    channel = client.get_channel(channel_id)
                    await channel.send(f"Archived review for {app_name}:\n```" + review + "```")
                await message.reply(f"Here's my take on {app_name} \n```" + review + "```")
            except Exception as e:
                print("Exception occurred while processing Steam link:")
                print(str(e))
                return
    
    secret_name = "DISCORD_BOT_TOKEN"
    bot_token = json.loads(get_secret(secret_name))[secret_name]
    client.run(bot_token)

def get_app_details(app_id):
    app_details_url = f"http://store.steampowered.com/api/appdetails?appids={app_id}&l=en"
    request_successful = False
    time_started = time.time()
    time_taken = 0
    while not request_successful:
        base_resp = requests.get(app_details_url)
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

def get_random_review_start(app_name):
    review_starts = [
        f"{app_name} is a game",
        f"I've been playing {app_name} for a few days now and",
        f"I can guarantee you'll love {app_name} because",
        f"If you ever see {app_name} on sale",
        f"Where do I even start when it comes to {app_name}, it's just",
        f"Definitely recommend {app_name}, and here's why:",
        f"{app_name} was on my wish list for a while and",
        f"I heard about {app_name} from a friend and",
        f"I bought {app_name} hoping for",
        f"{app_name} was gifted to me and",
        f"{app_name} is the Citizen Kane of video games.  It",
        f"I really wanted to like {app_name}, but"
    ]
    random_start = random.choice(review_starts)
    return random_start


def put_prompt_in_s3(prompt, bucket, inference_input_key):
    with open("prompt.txt", "w", encoding="utf-8") as writer:
        writer.write(prompt)
    s3_client = boto3.client("s3")
    s3_client.upload_file("prompt.txt", bucket, inference_input_key)
    return

def start_batch_job(batch_job_queue, batch_job_definition, region):
    batch_client = boto3.client("batch", region_name=region)
    batch_resp = batch_client.submit_job(
        jobName=batch_job_queue, 
        jobQueue=batch_job_queue, 
        jobDefinition=batch_job_definition,
        containerOverrides={
            "environment" : [
                {
                    "name" : "MODE",
                    "value" : "inference"
                }
            ]
        }
    )
    return batch_resp["jobId"]

def wait_on_job_completion(job_id, region):
    max_wait_time = 1200
    check_delay = 2
    start_time = time.time()
    pending_statuses = ["SUBMITTED", "PENDING", "RUNNABLE", "STARTING", "RUNNING"]
    client = boto3.client("batch", region_name=region)
    while time.time() - start_time <= max_wait_time:
        describe_jobs_resp = client.describe_jobs(jobs=[job_id])
        status = describe_jobs_resp['jobs'][0]['status']
        if status in pending_statuses:
            time.sleep(check_delay)
            continue
        if status == "SUCCEEDED" or status == "FAILED":
            return status
    return "TIMEOUT"

def get_generated_review(bucket, inference_output_key, app_id):
    s3_client = boto3.client("s3")
    s3_client.download_file(bucket, inference_output_key, f"{app_id}/review.txt")
    return open(f"{app_id}/review.txt", "r").read()

def clean_output(inference_output, prompt, review_start):
    review = inference_output.replace(prompt, review_start)
    review_clean = review.replace("Game Description:", "")
    last_full_stop_idx = review_clean.rfind(".")
    review_clean = review_clean[:last_full_stop_idx + 1]
    return review_clean

if __name__ == "__main__":
    main()