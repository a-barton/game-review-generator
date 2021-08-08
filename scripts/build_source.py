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

    print("Building the lambdas...")
    build_definitions(definitions=config.lambdas, func=build_lambda)

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


def build_lambda(source_path, build_path):
    """Compiles a lambda directory into a zipped archive."""
    HOME = os.getcwd()

    with tempfile.TemporaryDirectory() as tmp_root:
        tmpdir = os.path.join(tmp_root, "source")

        shutil.copytree(source_path, tmpdir)

        if "requirements.txt" in os.listdir(tmpdir):
            os.chdir(tmpdir)
            subprocess.check_output(
                "pip install -r requirements.txt -t . --upgrade".split(" ")
            )
            os.chdir(HOME)

        build_path_no_ext, _ = os.path.splitext(
            build_path
        )  # HACK: shutil appends .zip to path.
        shutil.make_archive(
            build_path_no_ext,
            "zip",
            tmpdir,
        )

    return


##########################
## __name__ == __main__ ##
##########################

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
