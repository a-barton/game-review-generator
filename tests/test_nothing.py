import boto3

def test_nothing():
    """Always passes. Boilerplate to assert Pytest works as expected."""
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket="bucket",
        Key="test.txt",
        Body="Hello World!".encode(),
    )
