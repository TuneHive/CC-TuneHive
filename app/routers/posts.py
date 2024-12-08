from fastapi import APIRouter, HTTPException, Body, Query
from typing import Annotated
from sqlmodel import SQLModel, select
from datetime import datetime

from ..models import Posts, Post_Likes
from ..dependencies.db import SessionDep
from ..dependencies.auth import CurrentUser
from ..response_models import Response, PostPublic

router = APIRouter(prefix="/posts", tags=["posts"])


class PostCreate(SQLModel):
    title: str
    content: str
    user_id: int


class PostUpdate(SQLModel):
    title: str | None = None
    content: str | None = None


@router.get("/", response_model=list[PostPublic])
async def get_all_posts(
    session: SessionDep,
    user_id: Annotated[int, Query(ge=1)],
    page: Annotated[int, Query(ge=1)] = 1,
    itemPerPage: Annotated[int, Query(ge=10, le=30)] = 10,
):
    offset = (page - 1) * itemPerPage
    posts = session.exec(
        select(Posts)
        .where(Posts.user_id == user_id)
        .order_by(Posts.created_at.desc())
        .offset(offset)
        .limit(itemPerPage)
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


@router.put("/{post_id}/like")
async def like_or_unlike_post(
    post_id: int, session: SessionDep, current_user: CurrentUser
):
    post = session.get(Posts, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    already_liked = session.exec(
        select(Post_Likes).where(
            Post_Likes.user_id == current_user.id, Post_Likes.post_id == post_id
        )
    ).one_or_none()
    if already_liked is not None:
        session.delete(already_liked)
        post.like_count -= 1
        session.add(post)

        session.commit()
        return Response(detail=f"Successfully liked post with id {post_id}")
    else:
        post_like = Post_Likes(user_id=current_user.id, post_id=post_id)
        session.add(post_like)

        post.like_count += 1
        session.add(post)

        session.commit()
        return Response(detail=f"Successfully liked post with id {post_id}")


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
