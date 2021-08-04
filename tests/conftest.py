import docker as docker_client
import pytest
import boto3
from moto import mock_s3

CONTAINER_NAME = "game-review-generator"
CONTAINER_VERSION = "latest"

@pytest.fixture(autouse=True)
def s3():
    with mock_s3():
        s3 = boto3.client("s3")

        s3.create_bucket(
            Bucket="bucket",
            CreateBucketConfiguration={'LocationConstraint': "ap-southeast-2"},
        )

        yield s3


@pytest.fixture(scope="session")
def docker():
    return docker_client.from_env()


@pytest.fixture(scope="session")
def container_image(docker):
    #os.chdir('src/src-container/')
    docker.images.build(
        path = '.',
        tag = f"{CONTAINER_NAME}:{CONTAINER_VERSION}",
        rm = False,
        nocache = False
    )