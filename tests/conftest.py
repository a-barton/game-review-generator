import pytest
import boto3
from moto import mock_s3


@pytest.fixture(autouse=True)
def s3():
    with mock_s3():
        s3 = boto3.client("s3")

        s3.create_bucket(
            Bucket="bucket",
            CreateBucketConfiguration={'LocationConstraint': "ap-southeast-2"},
        )

        yield s3
