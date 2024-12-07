from fastapi import APIRouter, HTTPException, Query
from pydantic import EmailStr
from typing import Annotated
from sqlmodel import SQLModel, Field, select
from datetime import datetime

from ..dependencies.db import SessionDep
from ..dependencies.auth import pwd_context, CurrentUser
from ..models import Users, Follows

router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(SQLModel):
    fullname: Annotated[str, Field(min_length=3)]
    username: Annotated[str, Field(min_length=3)]
    description: str | None = None
    email: EmailStr
    phone: str | None = None
    password: Annotated[str, Field(min_length=8)]


class UserUpdate(SQLModel):
    fullname: Annotated[str | None, Field(min_length=3)] = None
    username: Annotated[str | None, Field(min_length=3)] = None
    description: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class UserPublic(SQLModel):
    id: int
    created_at: datetime
    updated_at: datetime
    fullname: str
    username: str
    description: str | None = None
    email: str
    phone: str | None = None


class FollowerPublic(SQLModel):
    id: int
    fullname: str
    username: str
    email: str


@router.get("/", response_model=list[UserPublic])
async def get_all_users(
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    itemPerPage: Annotated[int, Query(ge=10, le=30)] = 10,
):
    offset = page - 1
    users = session.exec(select(Users).offset(offset).limit(itemPerPage)).all()
    return users


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can not access other user data")
    user = session.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserPublic)
async def create_user(
    user: UserCreate,
    session: SessionDep,
):
    existing_user = session.exec(
        select(Users).where(Users.email == user.email)
    ).one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user.password = pwd_context.hash(user.password)
    db_user = Users.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user: UserUpdate,
    session: SessionDep,
    current_user: CurrentUser,
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can not change other user data")
    existing_user = session.exec(
        select(Users).where(Users.id != user_id, Users.email == user.email)
    ).one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_db = session.get(Users, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    user_update_data = user.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_update_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


@router.delete("/{user_id}", response_model=UserPublic)
async def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can not delete other user")
    user = session.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return user


@router.post("/follow/{user_id}", response_model=FollowerPublic)
async def follow_user(user_id: int, session: SessionDep, current_user: CurrentUser):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You can't follow your own account")
    db_follows = Follows(user_id=user_id, follower_id=current_user.id)
    session.add(db_follows)
    session.commit()
    session.refresh(db_follows)

    return db_follows.followed_user


@router.post("/unfollow/{user_id}")
async def unfollow_user(user_id: int, session: SessionDep, current_user: CurrentUser):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="You can't unfollow your own account"
        )
    follow = session.get(Follows, [user_id, current_user.id])
    if not follow:
        raise HTTPException(status_code=400, detail="You haven't followed this account")
    session.delete(follow)
    session.commit()
    return {"detail": f"Successfully unfollowed user with id {user_id}"}


@router.get("/{user_id}/followers", response_model=list[FollowerPublic])
async def get_followers(
    user_id: int,
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    itemPerPage: Annotated[int, Query(ge=10, le=30)] = 10,
):
    user = session.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    offset = page - 1
    followers = session.exec(
        select(Follows)
        .where(Follows.user_id == user_id)
        .offset(offset)
        .limit(itemPerPage)
    ).all()
    follower_users = [follow.follower_user for follow in followers]
    return follower_users
