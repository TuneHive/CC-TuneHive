from fastapi import APIRouter, Body, Query, HTTPException
from typing import Annotated
from sqlmodel import SQLModel, select
from datetime import datetime

from ..models import Comments
from ..dependencies.db import SessionDep
from ..dependencies.auth import CurrentUser

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["posts"])


class CommentCreate(SQLModel):
    content: str
    post_id: int
    user_id: int


class CommentPublisher(SQLModel):
    id: int
    fullname: str
    username: str
    email: str


class CommentPublic(SQLModel):
    id: int
    created_at: datetime
    updated_at: datetime
    content: str
    user: CommentPublisher


@router.get("/", response_model=list[CommentPublic])
async def get_all_comments(
    session: SessionDep,
    post_id: int,
    page: Annotated[int, Query(ge=1)] = 1,
    itemPerPage: Annotated[int, Query(ge=10, le=30)] = 10,
):
    offset = page - 1
    comments = session.exec(
        select(Comments)
        .where(Comments.post_id == post_id)
        .offset(offset)
        .limit(itemPerPage)
    ).all()
    return comments


@router.post("/", response_model=CommentPublic)
async def create_comment(
    post_id: int,
    content: Annotated[str, Body(min_length=1)],
    session: SessionDep,
    current_user: CurrentUser,
):
    comment = CommentCreate(content=content, post_id=post_id, user_id=current_user.id)
    db_comment = Comments.model_validate(comment)
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment


@router.delete("/{comment_id}", response_model=CommentPublic)
async def delete_comment(
    post_id: int, comment_id: int, session: SessionDep, current_user: CurrentUser
):
    comment = session.get(Comments, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Can not delete other user's comment"
        )
    session.delete(comment)
    session.commit()
    return comment
