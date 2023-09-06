import os

import boto3


def setup():
    session = boto3.session.Session()
    s3_client = session.client(
        service_name="s3",
        aws_access_key_id="minioadmin",  # Default from the minio docker.
        aws_secret_access_key="minioadmin",  # Default from the minio docker.
        endpoint_url=os.getenv("S3_HOST", "http://localhost:9000"),
    )
    for bucket_name in (os.getenv("S3_STORAGE_BUCKET_NAME", "dev"), "tests"):
        try:
            s3_client.create_bucket(ACL="private", Bucket=bucket_name)
        except s3_client.exceptions.BucketAlreadyOwnedByYou:
            pass
    s3_client.put_bucket_lifecycle_configuration(
        Bucket="tests",
        LifecycleConfiguration={
            "Rules": [
                {
                    "Expiration": {"Days": 7},
                    "Filter": {},
                    "Status": "Enabled",
                },
            ],
        },
    )
