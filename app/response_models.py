from pydantic import BaseModel
from sqlmodel import SQLModel
from datetime import datetime


class Response(BaseModel):
    detail: str


class DetailedUserPublic(SQLModel):
    id: int
    created_at: datetime
    updated_at: datetime
    fullname: str
    username: str
    description: str | None = None
    email: str
    phone: str | None = None


class UserPublic(SQLModel):
    id: int
    fullname: str
    username: str
    email: str


class AlbumPublic(SQLModel):
    id: int
    created_at: datetime
    name: str


class SongPublic(SQLModel):
    id: int
    created_at: datetime
    updated_at: datetime
    name: str
    like_count: int
    singer: UserPublic
    album: AlbumPublic
    song_url: str
    cover_url: str


class DetailedAlbumPublic(SQLModel):
    id: int
    created_at: datetime
    updated_at: datetime
    name: str
    singer: UserPublic
    cover_url: str
    songs: list[SongPublic]


class CommentPublic(SQLModel):
    id: int
    created_at: datetime
    updated_at: datetime
    content: str
    user: UserPublic


class PostPublic(SQLModel):
    id: int
    created_at: datetime
    updated_at: datetime
    title: str
    content: str
    like_count: int
    user: UserPublic


class HistoryPublic(SQLModel):
    created_at: datetime
    song: SongPublic


class PlaylistPublic(SQLModel):
    id: int
    created_at: datetime
    updated_at: datetime
    name: str


class DetailedPlaylistPublic(SQLModel):
    id: int
    created_at: datetime
    updated_at: datetime
    name: str
    songs: list[SongPublic]
