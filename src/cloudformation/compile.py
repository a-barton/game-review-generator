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
RESOURCE_TAGS = DIR / "tags.json"
COMPONENTS_DIR = DIR / "components"
MACROS_DIR = DIR / "macros"

JINJA = Environment(loader=FileSystemLoader(DIR))

####################
## Main Execution ##
####################


@click.command()
@click.option(
    "--environment",
    required=True,
    envvar="ENV",
    type=click.Choice(["dev", "uat", "prod"]),
)
def compile(environment):
    ## Load the global variables which are accessable to the templates ##
    if JINJA_VARIABLES.exists():
        variables = json.loads((DIR / "globals.json").read_text())
    else:
        variables = {}

    ## Load in the tags which will be automatically applied to each resource ##
    if RESOURCE_TAGS.exists():
        tags = json.loads((DIR / "tags.json").read_text())
    else:
        tags = {}

    ## Add environment information to both dictionaries ##
    variables["environment"] = environment
    tags["Environment"] = environment.upper()

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

            if "Resources" in file_object:
                file_object["Resources"] = add_tags(file_object["Resources"], tags)

            output = merge(output, file_object)
        except Exception as exc:
            raise RuntimeError(f"Failed processing '{str(path)}'") from exc

    ## Print final template ##
    print(json.dumps(output, indent=2))


#################
## Subroutines ##
#################


def add_tags(resources, tags):
    for resource_key, definition in resources.items():
        definition_tags = definition["Properties"].get("Tags")

        if definition["Type"].startswith("AWS::Glue"):
            definition_tags = definition_tags or {}
            definition_tags["ResourceName"] = resource_key

            merged_tags = {**tags, **definition_tags}

        else:
            definition_tags = definition_tags or []
            definition_tags.append({"Key": "ResourceName", "Value": resource_key})

            merged_tags = {
                **tags,
                **{item["Key"]: item["Value"] for item in definition_tags},
            }
            merged_tags = [{"Key": k, "Value": v} for k, v in merged_tags.items()]

        resources[resource_key]["Properties"]["Tags"] = merged_tags

    return resources


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
