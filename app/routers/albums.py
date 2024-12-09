from fastapi import APIRouter, Form, UploadFile, File, HTTPException, Query
from typing import Annotated
from sqlmodel import SQLModel, select
from datetime import datetime

from ..models import Albums, Songs
from ..dependencies.auth import CurrentUser
from ..dependencies.db import SessionDep
from ..dependencies.cloud_storage import BucketDep
from ..bucket_functions import upload_file, delete_file
from ..response_models import DetailedAlbumPublic, UserPublic, AlbumPublic

router = APIRouter(prefix="/albums", tags=["albums"])


class AlbumCreate(SQLModel):
    name: str
    singer_id: int
    cover: str
    cover_url: str


class AlbumUpdate(SQLModel):
    name: str | None = None
    cover: str | None = None
    cover_url: str | None = None


class AlbumDelete(SQLModel):
    id: int
    created_at: datetime
    updated_at: datetime
    name: str
    singer: UserPublic


@router.get("/", response_model=list[AlbumPublic])
async def get_all_albums(
    session: SessionDep,
    user_id: Annotated[int, Query(ge=1)],
    page: Annotated[int, Query(ge=1)] = 1,
    itemPerPage: Annotated[int, Query(ge=10, le=30)] = 10,
):
    offset = (page - 1) * itemPerPage
    albums = session.exec(
        select(Albums)
        .where(Albums.singer_id == user_id)
        .order_by(Albums.created_at.desc())
        .offset(offset)
        .limit(itemPerPage)
    ).all()
    return albums


@router.get("/{album_id}", response_model=DetailedAlbumPublic)
async def get_album(album_id: int, session: SessionDep):
    album = session.get(Albums, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    return album


@router.post("/", response_model=DetailedAlbumPublic)
async def create_album(
    name: Annotated[str, Form(min_length=3)],
    cover: Annotated[UploadFile, File()],
    current_user: CurrentUser,
    session: SessionDep,
    bucket: BucketDep,
):
    allowed_types = ["image/jpeg", "image/png"]
    if cover.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {cover.content_type}. Allowed types: {', '.join(allowed_types)}",
        )

    max_file_size = 1 * 1024 * 1024  # 1 MB in bytes
    if cover.size > max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds the limit of 1 MB. Your file is {cover.size / (1024 * 1024):.2f} MB.",
        )

    existing_album = session.exec(
        select(Albums).where(Albums.name == name, Albums.singer_id == current_user.id)
    ).one_or_none()
    if existing_album:
        raise HTTPException(
            status_code=400,
            detail="Album with the same name and singer has already been created",
        )

    try:
        folder_name = "album_cover"
        blob_name, public_url = upload_file(bucket, current_user.id, cover, folder_name)

        album = AlbumCreate(
            name=name, singer_id=current_user.id, cover=blob_name, cover_url=public_url
        )
        db_album = Albums.model_validate(album)
        session.add(db_album)
        session.commit()
        session.refresh(db_album)

        return db_album
    except Exception as e:
        session.rollback()
        if blob_name:
            delete_file(bucket, blob_name)

        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.put("/{album_id}", response_model=DetailedAlbumPublic)
async def update_album(
    album_id: int,
    current_user: CurrentUser,
    session: SessionDep,
    bucket: BucketDep,
    name: Annotated[str | None, Form(min_length=3)] = None,
    cover: Annotated[UploadFile | None, File()] = None,
):
    album_db = session.get(Albums, album_id)
    if not album_db:
        raise HTTPException(status_code=404, detail="Album not found")
    if album_db.singer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can not change other user data")

    allowed_types = ["image/jpeg", "image/png"]
    if cover.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {cover.content_type}. Allowed types: {', '.join(allowed_types)}",
        )

    max_file_size = 1 * 1024 * 1024  # 1 MB in bytes
    if cover.size > max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds the limit of 1 MB. Your file is {cover.size / (1024 * 1024):.2f} MB.",
        )

    existing_album = session.exec(
        select(Albums).where(Albums.name == name, Albums.singer_id == current_user.id)
    ).one_or_none()
    if existing_album:
        raise HTTPException(
            status_code=400,
            detail="Album with the same name and singer has already been created",
        )

    try:
        folder_name = "album_cover"
        album = AlbumUpdate()
        if cover is not None:
            blob_name, public_url = upload_file(
                bucket, current_user.id, cover, folder_name
            )

            delete_file(bucket, album_db.cover)

            album.cover = blob_name
            album.cover_url = public_url
        if name is not None:
            album.name = name

        album_update_data = album.model_dump(exclude_unset=True)
        album_db.sqlmodel_update(album_update_data)
        session.add(album_db)
        session.commit()
        session.refresh(album_db)
        return album_db
    except Exception as e:
        session.rollback()
        if blob_name:
            delete_file(bucket, blob_name)

        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}",
        )


@router.delete("/{album_id}", response_model=AlbumDelete)
async def delete_album(
    album_id: int, session: SessionDep, current_user: CurrentUser, bucket: BucketDep
):
    album = session.get(Albums, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    if album.singer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can not delete other user's album")

    try:
        delete_file(bucket, album.cover)

        session.delete(album)
        session.commit()
        return album
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}",
        )


@router.post("/{album_id}/songs/{song_id}", response_model=DetailedAlbumPublic)
async def add_song_to_album(
    album_id: int, song_id: int, session: SessionDep, current_user: CurrentUser
):
    album = session.get(Albums, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    if album.singer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can not change other user's album")
    song = session.get(Songs, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    if song.singer_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Can not add other user's song other your album"
        )
    if song.album_id == album_id:
        raise HTTPException(
            status_code=400, detail="Song has been added to this album before"
        )
    if song.album_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Song has been added to other album. Please remove the song from other album",
        )
    song.album_id = album_id
    session.add(song)
    session.commit()
    session.refresh(album)
    return album


@router.delete("/{album_id}/songs/{song_id}", response_model=DetailedAlbumPublic)
async def remove_song_from_album(
    album_id: int, song_id: int, session: SessionDep, current_user: CurrentUser
):
    album = session.get(Albums, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    if album.singer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can not change other user's album")
    song = session.get(Songs, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    if song.album_id is None or song.album_id != album_id:
        raise HTTPException(
            status_code=400,
            detail="Song has not been added to this album",
        )
    song.album_id = None
    session.add(song)
    session.commit()
    session.refresh(album)
    return album
