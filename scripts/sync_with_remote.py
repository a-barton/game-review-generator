"""Syncs the files in the .build/ directory with the remote."""

import re

import boto3
import click
import os
import subprocess

from utils import load_config


@click.command()
@click.option("--config", "configuration_file", required=True, type=click.File("r"))
def main(configuration_file):
    s3 = boto3.client("s3")
    config = load_config(file=configuration_file)

    for service in config.values():

        for name, definition in service.items():

            if "remote" in definition:
                s3_uri = definition.remote
                bucket, key = re.match(r"s3:\/\/(.+?)\/(.+)", s3_uri).groups()
                
                if os.path.isdir(definition.build):
                    upload_s3_folder(bucket, key, definition.build)
                else:
                    s3.upload_file(definition.build, bucket, key)
            else:
                continue

    return

def upload_s3_folder(bucket, key, local_path):
    s3_path = f"s3://{bucket}/{key}"
    subprocess.check_call(f"aws s3 sync --quiet {local_path} {s3_path}".split(" "))
    return

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()