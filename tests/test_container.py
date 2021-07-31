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
TRAIN_DATA_DIR = os.path.join(TEST_CONTAINER_MOUNT, "training_input")
TRAIN_DATA_PATH = os.path.join(TRAIN_DATA_DIR, 'data.csv')
MODEL_DIR = os.path.join(TEST_CONTAINER_MOUNT, 'fine-tuned-model')

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

def test_train(docker):
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
            print(e.container.logs().decode()) # TODO: Use a proper python logging library instead of print().
        finally:
            raise RuntimeError("Something went wrong. See stdout.") from e

