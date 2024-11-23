from fastapi import FastAPI
from .routers import users, songs, playlists, albums, posts

app = FastAPI()

app.include_router(users.router)
app.include_router(songs.router)
app.include_router(playlists.router)
app.include_router(albums.router)
app.include_router(posts.router)

@app.get("/")
async def getHelloWorld():
  return "Hello World"