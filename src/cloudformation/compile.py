"""Compiles the templated Cloudformation defintion into a consumable format for AWS.

Any files under the `components/` directory will be merged together into a single file. 

There are no garuntees which resource / variable definition block will be kept
in the end. Ensure that your level-2 keys are unique across all files.
"""

import json
import os
from pathlib import Path
import click

DIR = Path(os.path.split(__file__)[0])
COMPONENTS_DIR = DIR / "components"

####################
## Main Execution ##
####################


@click.command()
def compile():
    ## Loop over each file in the components directory ##
    output = {}
    for path in COMPONENTS_DIR.iterdir():
        try:
            ## Merge basic JSON files ##
            if path.suffix == ".json":
                json_string = path.read_text()

            ## Else skip if not a JSON file ##
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
