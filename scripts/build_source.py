"""Compiles all of the source code, ready for deployment."""

import tempfile
import shutil
import os
import subprocess
from datetime import datetime

import click
import terminal_banner

from utils import load_config


@click.command()
@click.option("--config", "configuration_file", required=True, type=click.File("r"))
def main(configuration_file):
    start_time = datetime.now()
    print(terminal_banner.Banner(f"Starting build pipeline at {start_time}."))

    config = load_config(file=configuration_file)

    print("Passing through discord-bot source...")
    passthrough_build(source_path=config.ec2.discord_bot.source, build_path=config.ec2.discord_bot.build)

    end_time = datetime.now()
    time_diff = end_time - start_time

    if time_diff.seconds > 1:
        label = "s"
        diff = time_diff.seconds
    else:
        label = "ms"
        diff = time_diff.microseconds / 1000

    print(terminal_banner.Banner(f"Completed successfully. Took {diff}{label}."))
    return


#####################
## Build Functions ##
#####################


def passthrough_build(source_path, build_path):
    """Simply copies files into the build directory without any special instructions."""
    build_dir, _ = os.path.split(build_path)
    shutil.rmtree(build_path)
    shutil.copytree(source_path, build_path)
    return


def build_definitions(definitions, func=passthrough_build):
    """Builds a collection of definitions using the supplied build function."""

    for name, definition in definitions.items():
        print(f"\tBuilding {name}...")
        func(source_path=definition.source, build_path=definition.build)

    return


##########################
## __name__ == __main__ ##
##########################

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
