from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from pydantic import EmailStr


class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, index=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    fullname: str
    username: str
    description: str | None = Field(default=None)
    email: EmailStr = Field(unique=True)
    phone: str | None = Field(default=None)
    password: str

    albums: list["Albums"] = Relationship(back_populates="singer", cascade_delete=True)
    songs: list["Songs"] = Relationship(back_populates="singer", cascade_delete=True)
    posts: list["Posts"] = Relationship(back_populates="user")
    liked_posts: list["Post_Likes"] = Relationship(back_populates="user")
    comments: list["Comments"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    followers: list["Follows"] = Relationship(
        back_populates="followed_user",
        sa_relationship_kwargs={"foreign_keys": "Follows.user_id"},
        cascade_delete=True,
    )
    followings: list["Follows"] = Relationship(
        back_populates="follower_user",
        sa_relationship_kwargs={"foreign_keys": "Follows.follower_id"},
        cascade_delete=True,
    )
    histories: list["Histories"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    liked_songs: list["Song_Likes"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    playlists: list["Playlists"] = Relationship(
        back_populates="user", cascade_delete=True
    )


class Albums(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, index=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    name: str
    singer_id: int = Field(foreign_key="users.id")
    cover: str
    cover_url: str

    singer: Users = Relationship(back_populates="albums")
    songs: list["Songs"] = Relationship(back_populates="album", cascade_delete=True)


class Songs(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, index=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    name: str
    singer_id: int = Field(foreign_key="users.id")
    album_id: int | None = Field(default=None, foreign_key="albums.id")
    like_count: int
    popularity: float
    genre: str
    danceability: float
    loudness: float
    acousticness: float
    instrumentalness: float
    tempo: float
    key: str
    duration: int
    cover: str
    cover_url: str
    song: str
    song_url: str

    singer: Users = Relationship(back_populates="songs")
    album: Albums = Relationship(back_populates="songs")
    likes: list["Song_Likes"] = Relationship(back_populates="song", cascade_delete=True)
    histories: list["Histories"] = Relationship(
        back_populates="song", cascade_delete=True
    )
    playlists: list["Playlist_Songs"] = Relationship(
        back_populates="song", cascade_delete=True
    )


class Song_Likes(SQLModel, table=True):
    user_id: int = Field(foreign_key="users.id", primary_key=True, nullable=False)
    song_id: int = Field(foreign_key="songs.id", primary_key=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    user: Users = Relationship(back_populates="liked_songs")
    song: Songs = Relationship(back_populates="likes")


class Playlists(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, index=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    name: str
    user_id: int = Field(foreign_key="users.id")

    user: Users = Relationship(back_populates="playlists")
    songs: list["Playlist_Songs"] = Relationship(
        back_populates="playlist", cascade_delete=True
    )


class Playlist_Songs(SQLModel, table=True):
    playlist_id: int = Field(
        foreign_key="playlists.id", primary_key=True, nullable=False
    )
    song_id: int = Field(foreign_key="songs.id", primary_key=True, nullable=False)

    playlist: Playlists = Relationship(back_populates="songs")
    song: Songs = Relationship(back_populates="playlists")


class Posts(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, index=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    user_id: int = Field(foreign_key="users.id")
    title: str
    content: str
    like_count: int = Field(default=0)

    user: Users = Relationship(back_populates="posts")
    likes: list["Post_Likes"] = Relationship(back_populates="post", cascade_delete=True)
    comments: list["Comments"] = Relationship(
        back_populates="post", cascade_delete=True
    )


class Post_Likes(SQLModel, table=True):
    user_id: int = Field(foreign_key="users.id", primary_key=True, nullable=False)
    post_id: int = Field(foreign_key="posts.id", primary_key=True, nullable=False)

    user: Users = Relationship(back_populates="liked_posts")
    post: Posts = Relationship(back_populates="likes")


class Comments(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, index=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    post_id: int = Field(foreign_key="posts.id")
    user_id: int = Field(foreign_key="users.id")
    content: str

    post: Posts = Relationship(back_populates="comments")
    user: Users = Relationship(back_populates="comments")


class Follows(SQLModel, table=True):
    user_id: int = Field(foreign_key="users.id", primary_key=True, nullable=False)
    follower_id: int = Field(foreign_key="users.id", primary_key=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    followed_user: Users = Relationship(
        back_populates="followers",
        sa_relationship_kwargs={"foreign_keys": "[Follows.user_id]"},
    )
    follower_user: Users = Relationship(
        back_populates="followings",
        sa_relationship_kwargs={"foreign_keys": "[Follows.follower_id]"},
    )


class Histories(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, index=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    user_id: int = Field(foreign_key="users.id")
    song_id: int = Field(foreign_key="songs.id")

    user: Users = Relationship(back_populates="histories")
    song: Songs = Relationship(back_populates="histories")
