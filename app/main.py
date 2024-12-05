from fastapi import FastAPI
from .routers import login, users, songs, playlists, albums, posts, comments

app = FastAPI()

app.include_router(login.router)
app.include_router(users.router)
app.include_router(songs.router)
app.include_router(playlists.router)
app.include_router(albums.router)
app.include_router(posts.router)
app.include_router(comments.router)


@app.get("/")
async def getHelloWorld():
    return "Hello World"
