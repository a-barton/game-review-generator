"""Compiles the configuration directory, for use across environments.

The repository comes with the file `/parameters.json` which defines the 
parameters to be passed into the files under the `/configuration/` directory.

This compiler uses Jinja2 for it's compilation needs. Any valid Jinja code will
also be valid here.

There is also a special variable called `parameters` which provides an interface
into the `parameters.json` file as a dot-notation accessable dictionary.
"""

import json
import re
import os

import click
import jinja2

CONFIGURATION_DIRECTORY = "./configuration"
BUILD_DIRECTORY = "./.build/configuration"

JINJA_ENV = jinja2.Environment(undefined=jinja2.StrictUndefined)


@click.command()
@click.option("--parameters", required=True)
def compile(parameters):

    with open(parameters, "r") as f:
        parameters = json.load(f)

    render_configuration_files(parameters=parameters)


def render_configuration_files(parameters):
    for fname in os.listdir(CONFIGURATION_DIRECTORY):

        template_fpath = os.path.join(CONFIGURATION_DIRECTORY, fname)
        build_fpath = os.path.join(BUILD_DIRECTORY, fname)

        with open(template_fpath, "r") as f:
            template = json.load(f)

        config = render_template(template=template, parameters=parameters)

        os.makedirs(BUILD_DIRECTORY, exist_ok=True)
        with open(build_fpath, "w") as f:
            json.dump(config, f, indent=2)

    return


def render_template(template, parameters):
    if isinstance(template, list):
        iterator = enumerate(template)
    elif isinstance(template, dict):
        iterator = template.items()
    else:
        raise RuntimeError(f"I don't know how to process type {type(template)}.")

    for k, v in iterator:

        if isinstance(v, dict):
            v = render_template(v, parameters=parameters)

        else:
            if isinstance(v, str):
                v = JINJA_ENV.from_string(v).render(
                    parameters=parameters
                )
            else:
                v = v

        template[k] = v

    return template


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    compile()