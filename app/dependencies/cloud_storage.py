from google.cloud import storage
from typing import Annotated
from fastapi import Depends
from ..config import config


def get_bucket():
    storage_client = storage.Client()
    bucket = storage_client.bucket(config.bucket_name)
    return bucket


BucketDep = Annotated[storage.Bucket, Depends(get_bucket)]
