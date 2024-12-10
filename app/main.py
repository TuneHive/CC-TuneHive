from fastapi import FastAPI
from .routers import auth, users, songs, playlists, albums, posts, comments
from .config import config
import os

app = FastAPI()

if config.google_application_credentials is not None:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.google_application_credentials

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(songs.router)
app.include_router(playlists.router)
app.include_router(albums.router)
app.include_router(posts.router)
app.include_router(comments.router)


@app.get("/")
async def getHelloWorld():
    return "Hello World"
