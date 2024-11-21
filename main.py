from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def getHelloWorld():
  return "Hello World"