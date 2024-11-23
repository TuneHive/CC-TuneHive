from fastapi import APIRouter, Form, UploadFile, File, Body
from typing import Annotated

router = APIRouter(
  prefix="/albums",
  tags=["albums"]
)

@router.get("/")
async def get_all_albums(user_id: str):
  return f"All albums from user with ID {user_id}"

@router.get("/{album_id}")
async def get_album(album_id: str):
  return f"Album data with id {album_id}"

@router.post("/")
async def create_album(
  name: Annotated[str, Form(min_length=3)],
  cover: Annotated[UploadFile, File()]
):
  # Tambahin authentication -> hanya pengguna yg login yg bisa buat album
  return {
    "name": name,
    "cover": cover.filename
  }

@router.put("/{album_id}")
async def update_album(
  album_id: str,
  name: Annotated[str | None, Form(min_length=3)] = None,
  cover: Annotated[UploadFile | None, File()] = None
):
  return {"id": album_id, "album": {
    "name": name,
    "cover": cover.filename if cover is not None else "cover is not provided"
  }}

@router.delete("/{album_id}")
async def delete_album(album_id: str):
  return f"Album with ID {album_id} was deleted"

@router.post("/{album_id}/songs")
async def add_song_to_album(
  album_id: str,
  song_id: Annotated[str, Body()]
):
  return f"Song with id {song_id} has been added to album with ID {album_id}"

@router.delete("/{album_id}/songs/{song_id}")
async def remove_song_from_album(
  album_id: str,
  song_id: str
):
  return f"Song with id {song_id} has been removed from album with ID {album_id}"