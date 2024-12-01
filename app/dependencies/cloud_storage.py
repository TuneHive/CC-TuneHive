from google.cloud import storage
from typing import Annotated
from fastapi import Depends
from ..config import Config
import os

config = Config()


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.google_application_credentials


def get_bucket():
    storage_client = storage.Client()
    bucket = storage_client.bucket(config.bucket_name)
    return bucket


BucketDep = Annotated[storage.Bucket, Depends(get_bucket)]
