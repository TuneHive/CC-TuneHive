from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated

router = APIRouter(
  prefix="/users",
  tags=["users"]
)

class UserCreate(BaseModel):
  fullname: Annotated[str, Field(min_length=3)]
  username: Annotated[str, Field(min_length=3)]
  description: str | None = None
  email: EmailStr
  phone: str | None = None
  password: Annotated[str, Field(min_length=8)]

class UserUpdate(BaseModel):
  fullname: Annotated[str | None, Field(min_length=3)] = None
  username: Annotated[str | None, Field(min_length=3)] = None
  description: str | None = None
  email: EmailStr | None = None
  phone: str | None = None

@router.get("/")
async def get_all_users():
  return "All users"

@router.get("/{user_id}")
async def get_user(user_id: str):
  return f"User with id {user_id}"

@router.post("/")
async def create_user(user: UserCreate):
  return user

@router.put("/{user_id}")
async def update_user(user_id: str, user: UserUpdate):
  return {"id": user_id, "user": user}

@router.delete("/{user_id}")
async def delete_user(user_id: str):
  return f"User with ID {user_id} was deleted"