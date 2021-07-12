"""Scaffolds the boilerplate of a new lambda function.

TODO: Explain what this scaffolding does.
TODO: Create a new CloudFormation definition too as a part of scaffold.
"""

import os
import shutil
import json
from pathlib import Path

import click
from jinja2 import Template

PROJECT_HOME = Path(os.environ["APPLICATION_HOME"])
BUILD_HOME = PROJECT_HOME / ".build"
TEMPLATES_HOME = PROJECT_HOME / "scripts" / "templates"
CLOUDFORMATION_HOME = PROJECT_HOME / "src" / "cloudformation"


@click.command()
@click.argument("service", type=click.Choice(["lambda", "glue", "stepfunction"]))
@click.option("--name", prompt="Name (snake_case)")
def scaffold(service, name):
    if service == "lambda":
        scaffold_lambda(name=name)
    elif service == "glue":
        scaffold_glue(name=name)
    elif service == "stepfunction":
        scaffold_stepfunction(name=name)
    return


def scaffold_lambda(name):
    lambdas_home = PROJECT_HOME / "src" / "lambdas"

    localpath = lambdas_home / name
    buildpath = BUILD_HOME / "lambdas" / f"{name}.zip"
    remotepath = Path("source") / "lambdas" / f"{name}.json"

    ## Create new directory for lambda ##
    os.makedirs(lambdas_home / name)

    ## Install boilerplate app.py and requirements.txt files. ##
    shutil.copy(TEMPLATES_HOME / "app.py", localpath / "app.py")
    (localpath / "requirements.txt").touch()

    ## Update DevOps boilerplate. ##
    add_to_paths_json(
        service="lambda",
        name=name,
        localpath=localpath,
        buildpath=buildpath,
        remotepath=remotepath,
    )
    init_cloudformation_template(
        template="cfn.lambda.json", name=name, source_key=remotepath
    )
    return


def scaffold_glue(name):
    glue_home = PROJECT_HOME / "src" / "glue"

    localpath = glue_home / f"{name}.py"
    buildpath = BUILD_HOME / "glue" / f"{name}.py"
    remotepath = Path("source") / "glue" / f"{name}.py"

    ## Install boilerplate glue job ##
    shutil.copy(TEMPLATES_HOME / "glue.py", localpath)

    ## Update DevOps boilerplate. ##
    add_to_paths_json(
        service="glue",
        name=name,
        localpath=localpath,
        buildpath=buildpath,
        remotepath=remotepath,
    )
    init_cloudformation_template(
        template="cfn.glue.json", name=name, source_key=remotepath
    )
    return


def scaffold_stepfunction(name):
    stepfunctions_home = PROJECT_HOME / "src" / "stepfunctions"

    localpath = stepfunctions_home / f"{name}.json"
    buildpath = BUILD_HOME / "stepfunctions" / f"{name}.json"
    remotepath = Path("source") / "stepfunctions" / f"{name}.json"

    ## Install boilerplate stepfunctions.json ##
    shutil.copy(TEMPLATES_HOME / "stepfunction.json", localpath)

    ## Update DevOps boilerplate. ##

    add_to_paths_json(
        service="stepfunction",
        name=name,
        localpath=localpath,
        buildpath=buildpath,
        remotepath=remotepath,
    )
    init_cloudformation_template(
        template="cfn.stepfunction.json", name=name, source_key=remotepath,
    )
    return


###############
## Utilities ##
###############


def add_to_paths_json(service, name, localpath, buildpath, remotepath):
    with open("configuration/paths.json", "r") as f:
        config = json.load(f)

    config[service] = config.get(service, {})
    config[service][name] = {
        "source": str(localpath),
        "build": str(buildpath),
        "remote": "s3://{{ bucket }}/{{ prefix }}/" + str(remotepath),
    }

    with open("configuration/paths.json", "w") as f:
        json.dump(config, f, indent=2)

    return


def init_cloudformation_template(template, name, **kwargs):
    with open(TEMPLATES_HOME / template, "r") as f:
        tmpl = Template(f.read())

    dst = CLOUDFORMATION_HOME / "components" / f"{name}.json"
    with open(dst, "w") as f:
        f.write(tmpl.render(name=snake_case_to_title_case(name), **kwargs))


def snake_case_to_title_case(string):
    return "".join([word.title() for word in string.split("_")])


if __name__ == "__main__":
    scaffold()
