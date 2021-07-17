"""Syncs the files in the .build/ directory with the remote."""

import re

import boto3
import click

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

                s3.upload_file(definition.build, bucket, key)
            else:
                continue

    return


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()