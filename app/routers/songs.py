from fastapi import APIRouter, UploadFile, Form, File
from typing import Annotated

router = APIRouter(prefix="/songs", tags=["songs"])


@router.get("/")
async def get_all_songs(user_id: str):
    return f"All songs from user with ID {user_id}"


@router.get("/{song_id}")
async def get_song(song_id: str):
    return f"Song data with id {song_id}"


@router.post("/")
async def create_song(
    name: Annotated[str, Form(min_length=3)],
    song: Annotated[UploadFile, File()],
    cover: Annotated[UploadFile, File()],
    album: Annotated[str | None, Form()] = None,
):
    # Tambahin authentication -> hanya pengguna yg login yg bisa tambah lagu
    return {
        "name": name,
        "album": album,
        "song": song.filename,
        "cover": cover.filename,
    }


@router.put("/{song_id}")
async def update_song(
    song_id: str,
    name: Annotated[str | None, Form()] = None,
    album: Annotated[str | None, Form()] = None,
    cover: Annotated[UploadFile | None, File()] = None,
):
    return {
        "id": song_id,
        "song": {
            "name": name,
            "album": album,
            "cover": cover.filename if cover is not None else "cover not provided",
        },
    }


@router.delete("/{song_id}")
async def delete_song(song_id: str):
    return f"Song with ID {song_id} was deleted"
