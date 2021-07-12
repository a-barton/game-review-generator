"""Compiles the source code into AWS ready artifacts."""

import click

#########
## CLI ##
#########


@click.command()
def main():
    ...


#########################
## Main Build Function ##
#########################


def build_resources():
    ...


######################
## Build Strategies ##
######################


def passthrough():
    ...


def inject_values():
    ...


def install_requirements_txt_and_zip():
    ...
