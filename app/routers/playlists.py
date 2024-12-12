from fastapi import APIRouter, Body, HTTPException, Query
from typing import Annotated
from sqlmodel import SQLModel, select

from ..models import Playlists, Playlist_Songs, Songs
from ..dependencies.db import SessionDep
from ..dependencies.auth import CurrentUser
from ..response_models import PlaylistPublic, DetailedPlaylistPublic

router = APIRouter(prefix="/playlists", tags=["playlists"])


class PlaylistCreate(SQLModel):
    name: str
    user_id: int


@router.get("/", response_model=list[PlaylistPublic])
async def get_all_playlists(
    session: SessionDep,
    user_id: Annotated[int, Query(ge=1)],
    page: Annotated[int, Query(ge=1)] = 1,
    itemPerPage: Annotated[int, Query(ge=10, le=30)] = 10,
):
    offset = (page - 1) * itemPerPage
    playlists = session.exec(
        select(Playlists)
        .where(Playlists.user_id == user_id)
        .order_by(Playlists.created_at.desc())
        .offset(offset)
        .limit(itemPerPage)
    ).all()
    return playlists


@router.get("/{playlist_id}", response_model=DetailedPlaylistPublic)
async def get_playlist(playlist_id: int, session: SessionDep):
    playlist = session.get(Playlists, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    playlist_songs = [song.song for song in playlist.songs]
    return DetailedPlaylistPublic(
        id=playlist.id,
        created_at=playlist.created_at,
        updated_at=playlist.updated_at,
        name=playlist.name,
        songs=playlist_songs,
    )


@router.post("/", response_model=PlaylistPublic)
async def create_playlist(
    name: Annotated[str, Body(min_length=3)],
    session: SessionDep,
    current_user: CurrentUser,
):
    playlist = PlaylistCreate(name=name, user_id=current_user.id)
    playlist_db = Playlists.model_validate(playlist)
    session.add(playlist_db)
    session.commit()
    session.refresh(playlist_db)
    return playlist_db


@router.put("/{playlist_id}", response_model=PlaylistPublic)
async def update_playlist(
    playlist_id: int,
    name: Annotated[str, Body(min_length=3)],
    session: SessionDep,
    current_user: CurrentUser,
):
    playlist = session.get(Playlists, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Can not change other user's playlist"
        )
    playlist.name = name
    session.add(playlist)
    session.commit()
    session.refresh(playlist)
    return playlist


@router.delete("/{playlist_id}", response_model=PlaylistPublic)
async def delete_playlist(
    playlist_id: int, session: SessionDep, current_user: CurrentUser
):
    playlist = session.get(Playlists, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Can not delete other user's playlist"
        )
    session.delete(playlist)
    session.commit()
    return playlist


@router.post("/{playlist_id}/songs/{song_id}", response_model=DetailedPlaylistPublic)
async def add_song_to_playlist(
    playlist_id: int, song_id: int, session: SessionDep, current_user: CurrentUser
):
    playlist = session.get(Playlists, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    song = session.get(Songs, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Can not change other user's playlist"
        )
    already_added = session.exec(
        select(Playlist_Songs).where(
            Playlist_Songs.playlist_id == playlist_id, Playlist_Songs.song_id == song_id
        )
    ).one_or_none()
    if already_added:
        raise HTTPException(
            status_code=400, detail="Song has been added to playlist before"
        )
    playlist_song_db = Playlist_Songs(playlist_id=playlist_id, song_id=song_id)
    session.add(playlist_song_db)
    session.commit()
    session.refresh(playlist)

    playlist_songs = [song.song for song in playlist.songs]
    return DetailedPlaylistPublic(
        id=playlist.id,
        created_at=playlist.created_at,
        updated_at=playlist.updated_at,
        name=playlist.name,
        songs=playlist_songs,
    )


@router.delete("/{playlist_id}/songs/{song_id}", response_model=DetailedPlaylistPublic)
async def remove_song_from_playlist(
    playlist_id: int, song_id: int, session: SessionDep, current_user: CurrentUser
):
    playlist = session.get(Playlists, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    song = session.get(Songs, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Can not remove song from other user's playlist"
        )
    playlist_song = session.get(Playlist_Songs, (playlist_id, song_id))
    if not playlist_song:
        raise HTTPException(
            status_code=404, detail="Song has not been added to playlist before"
        )
    session.delete(playlist_song)
    session.commit()
    session.refresh(playlist)

    playlist_songs = [song.song for song in playlist.songs]
    return DetailedPlaylistPublic(
        id=playlist.id,
        created_at=playlist.created_at,
        updated_at=playlist.updated_at,
        name=playlist.name,
        songs=playlist_songs,
    )
