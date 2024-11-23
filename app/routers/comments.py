from fastapi import APIRouter, Body
from typing import Annotated

router = APIRouter(
  prefix="/posts/{post_id}/comments",
  tags=["posts"]
)

@router.get("/")
async def get_all_comments(post_id: str):
  return f"All comments from post with ID {post_id}"

@router.post("/")
async def create_comment(post_id: str, content: Annotated[str, Body()]):
  # Tambahin authentication -> hanya pengguna yg login yg bisa buat post
  return f"Created a comment with content {content} for post id {post_id}"

@router.put("/{comment_id}")
async def update_comment(
  post_id: str,
  comment_id: str,
  content: Annotated[str, Body()],
  like: int,
  dislike: int
):
  return {"post_id": post_id, "comment_id": comment_id, "content": content, "like": like, "dislike": dislike}

@router.delete("/{comment_id}")
async def delete_comment(post_id: str, comment_id: str):
  return f"Comment with ID {comment_id} from post with ID {post_id} was deleted"
