import boto3
import os
import shutil
import subprocess

def download_s3_file(bucket, key, dest_path):
    s3_client = boto3.client("s3")
    if '/' in dest_path:
        file_dir = os.path.join(dest_path.split('/')[:-1])
        if os.path.isdir(file_dir):
            shutil.rmtree(file_dir, ignore_erros=True)
        os.makedirs(file_dir)
    s3_client.download_file(bucket, key, dest_path)
    return

def download_s3_folder(bucket, key, dest_path):
    s3_path = f"s3://{bucket}/{key}"
    subprocess.check_call(f"aws s3 sync --quiet {s3_path} {dest_path}".split(" "))
    return

def upload_s3_file(bucket, key, local_path):
    s3_client = boto3.client('s3')
    s3_client.upload_file(local_path, bucket, key)
    return

def upload_s3_folder(bucket, key, local_path):
    s3_path = f"s3://{bucket}/{key}"
    subprocess.check_call(f"aws sync --quiet {local_path} {s3_path}".split(" "))
    return
