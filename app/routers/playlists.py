from fastapi import APIRouter, UploadFile, File, Body
from typing import Annotated

router = APIRouter(
  prefix="/playlists",
  tags=["playlists"]
)

@router.get("/")
async def get_all_playlists(user_id: str):
  return f"All playlists from user with ID {user_id}"

@router.get("/{playlist_id}")
async def get_playlist(playlist_id: str):
  return f"Playlist data with id {playlist_id}"

@router.post("/")
async def create_playlist(name: Annotated[str, Body(min_length=3)]):
  # Tambahin authentication -> hanya pengguna yg login yg bisa buat playlist
  return f"Created empty playlist named {name} with some id"

@router.put("/{playlist_id}")
async def update_playlist(
  playlist_id: str,
  name: Annotated[str, Body(min_length=3)],
):
  return {"id": playlist_id, "playlist_name": name}

@router.delete("/{playlist_id}")
async def delete_playlist(playlist_id: str):
  return f"Playlist with ID {playlist_id} was deleted"

@router.post("/{playlist_id}/songs")
async def add_song_to_playlist(
  playlist_id: str,
  song_id: Annotated[str, Body()]
):
  return f"Song with id {song_id} has been added to playlist with ID {playlist_id}"

@router.delete("/{playlist_id}/songs/{song_id}")
async def remove_song_from_playlist(
  playlist_id: str,
  song_id: str
):
  return f"Song with id {song_id} has been removed from playlist with ID {playlist_id}"