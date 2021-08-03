import boto3

import json
import os
import shutil
import time

import pandas as pd
import pytest
import requests
import docker as docker_module

CONTAINER_NAME = "game-review-generator"
CONTAINER_VERSION = "latest"
TEST_CONTAINER_MOUNT = os.environ.get("CONTAINER_TEST_DIR")
MODEL_DIR = os.path.join(TEST_CONTAINER_MOUNT, 'fine-tuned-model')
INFERENCE_OUTPUT_DIR = os.path.join(TEST_CONTAINER_MOUNT, 'inference_output')

##############
## Fixtures ##
##############

@pytest.fixture(scope="module")
def inference_container(docker):
    container = docker.containers.run(
        f"{CONTAINER_NAME}:{CONTAINER_VERSION}", 
        remove = True,
        detach = True,
        volumes = {TEST_CONTAINER_MOUNT : {'bind' : '/src/src-container/artifacts', 'mode' : 'rw'}},
    )

    yield container
    container.kill()

###########
## Tests ##
###########

@pytest.mark.skip()
def test_train_local(docker):
    try:
        # Clear out test mount model directory in case any lingering temp files
        os.system('sudo chmod 777 -R {}'.format(MODEL_DIR))
        shutil.rmtree(MODEL_DIR, ignore_errors=True)
        os.makedirs(MODEL_DIR)
        
        # Spin up docker container in 'train' mode
        logs = docker.containers.run(
            f"{CONTAINER_NAME}:{CONTAINER_VERSION}",

            volumes = {TEST_CONTAINER_MOUNT : {'bind' : '/src/src-container/artifacts', 'mode' : 'rw'}},
            remove = False,

            environment={"MODE":"train"},

            stdout = True,
            stderr = True,
        )
        print(logs.decode())

        # Confirm that artifacts have been serialised to model artifact folder
        assert len(os.listdir(MODEL_DIR)) > 0

    except docker_module.errors.ContainerError as e:
        try:
            print("== Container Logs ==")
            print(e.container.logs().decode())
        finally:
            raise RuntimeError("Something went wrong. See stdout.") from e


def test_inference_local(docker):
    try:
        # Clear out test mount inference output directory
        os.system('sudo chmod 777 -R {}'.format(INFERENCE_OUTPUT_DIR))
        shutil.rmtree(INFERENCE_OUTPUT_DIR, ignore_errors=True)
        os.makedirs(INFERENCE_OUTPUT_DIR)

        # Spin up docker container in 'inference' mode
        logs = docker.containers.run(
            f"{CONTAINER_NAME}:{CONTAINER_VERSION}",

            volumes = {TEST_CONTAINER_MOUNT : {'bind' : '/src/src-container/artifacts', 'mode' : 'rw'}},
            remove = False,

            environment={"MODE":"inference"},

            stdout = True,
            stderr = True,
        )
        print(logs.decode())

        # Confirm that artifacts have been serialised to model artifact folder
        assert len(os.listdir(INFERENCE_OUTPUT_DIR)) > 0

    except docker_module.errors.ContainerError as e:
        try:
            print("== Container Logs ==")
            print(e.container.logs().decode())
        finally:
            raise RuntimeError("Something went wrong. See stdout.") from e