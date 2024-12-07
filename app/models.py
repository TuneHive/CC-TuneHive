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
    posts: list["Posts"] = Relationship(back_populates="user", cascade_delete=True)
    liked_posts: list["Post_Likes"] = Relationship(back_populates="user")
    comments: list["Comments"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    followers: list["Follows"] = Relationship(
        back_populates="followed_user",
        sa_relationship_kwargs={"foreign_keys": "Follows.user_id"},
    )
    followings: list["Follows"] = Relationship(
        back_populates="follower_user",
        sa_relationship_kwargs={"foreign_keys": "Follows.follower_id"},
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
    likes: list["Post_Likes"] = Relationship(back_populates="post")
    comments: list["Comments"] = Relationship(back_populates="post")


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

    followed_user: Users = Relationship(
        back_populates="followers",
        sa_relationship_kwargs={"foreign_keys": "[Follows.user_id]"},
    )
    follower_user: Users = Relationship(
        back_populates="followings",
        sa_relationship_kwargs={"foreign_keys": "[Follows.follower_id]"},
    )
