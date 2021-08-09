"""Compiles the templated Cloudformation defintion into a consumable format for AWS.

The templator relies on Jinja2 to manage its templating logic. Any files under
the `components/` directory will be merged together into a single file. 

There are no garuntees which resource / variable definition block will be kept
in the end. Ensure that your level-2 keys are unique across all files.
"""
import json
import os
from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader

DIR = Path(os.path.split(__file__)[0])
JINJA_VARIABLES = DIR / "globals.json"
COMPONENTS_DIR = DIR / "components"

JINJA = Environment(loader=FileSystemLoader(DIR))

####################
## Main Execution ##
####################


@click.command()
def compile():
    ## Load the global variables which are accessable to the templates ##
    if JINJA_VARIABLES.exists():
        variables = json.loads((DIR / "globals.json").read_text())
    else:
        variables = {}

    ## Loop over each file in the components directory ##
    output = {}
    for path in COMPONENTS_DIR.iterdir():
        try:
            relpath = path.relative_to(DIR)

            ## Just merge basic JSON files ##
            if path.suffix == ".json":
                json_string = path.read_text()

            ## Compute Jinja template ##
            elif path.suffix in (".jinja", ".jinja2", ".j2"):
                tmpl = JINJA.get_template(str(relpath))
                json_string = tmpl.render(**variables)

            ## Else skip if not a jinja template ##
            else:
                continue

            file_object = json.loads(json_string)

            output = merge(output, file_object)
        except Exception as exc:
            raise RuntimeError(f"Failed processing '{str(path)}'") from exc

    ## Print final template ##
    print(json.dumps(output, indent=2))


#################
## Subroutines ##
#################

def merge(*dicts):
    """Merges N cloudformation definition objects together."""

    result = {}

    for d in dicts:
        for k, v in d.items():

            if isinstance(v, dict):
                result[k] = {**result.get(k, {}), **v}

            else:
                result[k] = v

    return result


if __name__ == "__main__":
    compile()
