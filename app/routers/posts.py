from fastapi import APIRouter, HTTPException, Body, Query
from typing import Annotated
from sqlmodel import SQLModel, select
from datetime import datetime

from ..models import Posts, Post_Likes
from ..dependencies.db import SessionDep
from ..dependencies.auth import CurrentUser

router = APIRouter(prefix="/posts", tags=["posts"])


class PostCreate(SQLModel):
    title: str
    content: str
    user_id: int


class PostLikeCreate(SQLModel):
    user_id: int
    post_id: int


class PostUpdate(SQLModel):
    title: str | None = None
    content: str | None = None


class PostPublisher(SQLModel):
    id: int
    fullname: str
    username: str
    email: str


class PostPublic(SQLModel):
    id: int
    created_at: datetime
    updated_at: datetime
    title: str
    content: str
    like_count: int
    user: PostPublisher


@router.get("/", response_model=list[PostPublic])
async def get_all_posts(
    session: SessionDep,
    user_id: Annotated[int, Query(ge=1)] = 1,
    page: Annotated[int, Query(ge=1)] = 1,
    itemPerPage: Annotated[int, Query(ge=10, le=30)] = 10,
):
    offset = page - 1
    posts = session.exec(
        select(Posts).where(Posts.user_id == user_id).offset(offset).limit(itemPerPage)
    ).all()
    return posts


@router.get("/{post_id}", response_model=PostPublic)
async def get_post(post_id: int, session: SessionDep):
    post = session.get(Posts, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/", response_model=PostPublic)
async def create_post(
    title: Annotated[str, Body(min_length=1)],
    content: Annotated[str, Body(min_length=1)],
    session: SessionDep,
    current_user: CurrentUser,
):
    post = PostCreate(title=title, content=content, user_id=current_user.id)
    db_post = Posts.model_validate(post)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@router.put("/{post_id}", response_model=PostPublic)
async def update_post(
    post_id: int, post: PostUpdate, session: SessionDep, current_user: CurrentUser
):
    post_db = session.get(Posts, post_id)
    if not post_db:
        raise HTTPException(status_code=404, detail="Post not found")
    if post_db.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can not change other user's post")
    post_update_data = post.model_dump(exclude_unset=True)
    post_db.sqlmodel_update(post_update_data)
    session.add(post_db)
    session.commit()
    session.refresh(post_db)
    return post_db


@router.put("/{post_id}/like", response_model=PostPublic)
async def like_post(post_id: int, session: SessionDep, current_user: CurrentUser):
    post = session.get(Posts, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    already_liked = session.exec(
        select(Post_Likes).where(
            Post_Likes.user_id == current_user.id, Post_Likes.post_id == post_id
        )
    ).one_or_none()
    if already_liked is not None:
        raise HTTPException(status_code=400, detail="User has alerady liked the post")
    post_like = PostLikeCreate(user_id=current_user.id, post_id=post_id)
    db_like = Post_Likes.model_validate(post_like)
    session.add(db_like)

    post.like_count += 1
    session.add(post)

    session.commit()
    session.refresh(post)
    return post


@router.delete("/{post_id}", response_model=PostPublic)
async def delete_post(post_id: int, session: SessionDep, current_user: CurrentUser):
    post = session.get(Posts, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can not delete other user's post")
    session.delete(post)
    session.commit()
    return post
