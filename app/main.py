from fastapi import FastAPI
from .routers import users, songs

app = FastAPI()

app.include_router(users.router)
app.include_router(songs.router)

@app.get("/")
async def getHelloWorld():
  return "Hello World"