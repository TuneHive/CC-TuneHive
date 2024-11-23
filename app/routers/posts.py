from fastapi import APIRouter, Body
from typing import Annotated

router = APIRouter(
  prefix="/posts",
  tags=["posts"]
)

@router.get("/")
async def get_all_posts(user_id: str):
  return f"All posts from user with ID {user_id}"

@router.get("/{post_id}")
async def get_post(post_id: str):
  return f"Post data with id {post_id}"

@router.post("/")
async def create_post(content: Annotated[str, Body()]):
  # Tambahin authentication -> hanya pengguna yg login yg bisa buat post
  return f"Created a post with content {content} with some id"

@router.put("/{post_id}")
async def update_post(
  post_id: str,
  content: Annotated[str, Body()],
  like: int,
  dislike: int
):
  return {"id": post_id, "content": content, "like": like, "dislike": dislike}


@router.delete("/{post_id}")
async def delete_post(post_id: str):
  return f"Post with ID {post_id} was deleted"
