from fastapi import UploadFile
from google.cloud import storage
import random
import string


def upload_file(bucket: storage.Bucket, user_id: str, file: UploadFile):
    random_string = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=12)
    )

    filename = f"album_cover/{user_id}_{random_string}_{file.filename}"
    blob = bucket.blob(filename)

    generation_match_precondition = 0
    blob.upload_from_file(
        file.file,
        content_type=file.content_type,
        if_generation_match=generation_match_precondition,
    )

    return blob.name, blob.public_url


def delete_file(bucket: storage.Bucket, filename: str):
    fileToDelete = bucket.blob(filename)
    fileToDelete.reload()
    generation_match_precondition = fileToDelete.generation
    fileToDelete.delete(if_generation_match=generation_match_precondition)
