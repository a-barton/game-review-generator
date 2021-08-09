import discord
import boto3
import re
import requests
import json
import time
import click

from utils import get_secret

@click.command()
@click.option("--bucket", "bucket", required=True)
@click.option("--batch_job_queue", "batch_job_queue", required=True)
@click.option("--batch_job_definition", "batch_job_definition", required=True)
def main(bucket, batch_job_queue, batch_job_definition):

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
            print("Detected Steam URL")
            app_id = re.match(steam_url_regex, message.content).group(1)
            print("Extracted app ID from URL")
            app_name, app_desc = get_app_details(app_id)
            print("Retrieved app name and description from Steam:")
            print(f"App Name = {app_name}\nApp Description = {app_desc}")

            prompt = f"Game Description: {app_desc}\n Review: {app_name} is a game "
            put_prompt_in_s3(prompt, bucket, inference_input_key)
            
            job_id = start_batch_job(batch_job_queue, batch_job_definition)
            job_outcome = wait_on_job_completion(job_id)

            if job_outcome == "FAILED" or job_outcome == "TIMEOUT":
                print(f"Job unsuccessful: {job_outcome}")
                return
            
            review = get_generated_review(bucket, inference_output_key)

            await message.reply(f"Here's my take on {app_name} \n```" + review + "```")
    
    secret_name = "DISCORD_BOT_TOKEN"
    bot_token = json.loads(get_secret(secret_name))[secret_name]
    client.run(bot_token)

def get_app_details(app_id):
    app_details_url = "http://store.steampowered.com/api/appdetails?appids="
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

def put_prompt_in_s3(prompt, bucket, inference_input_key):
    s3_client = boto3.client("s3")
    s3_client.put_object(Body=prompt, Bucket=bucket, Key=inference_input_key)
    return

def start_batch_job(batch_job_queue, batch_job_definition):
    batch_client = boto3.client("batch")
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

def wait_on_job_completion(job_id):
    max_wait_time = 900
    check_delay = 2
    start_time = time.time()
    pending_statuses = ["SUBMITTED", "PENDING", "RUNNABLE", "STARTING", "RUNNING"]
    client = boto3.client("batch")
    while time.time() - start_time <= max_wait_time:
        describe_jobs_resp = client.describe_jobs([job_id])
        status = describe_jobs_resp['jobs'][0]['status']
        if status in pending_statuses:
            time.sleep(check_delay)
            continue
        if status == "SUCCEEDED" or status == "FAILED":
            return status
    return "TIMEOUT"

def get_generated_review(bucket, inference_output_key):
    s3_client = boto3.client("s3")
    s3_client.download_file(bucket, inference_output_key, "generated_review/review.txt")
    return open("generated_review/review.txt", "r").read()

if __name__ == "__main__":
    main()