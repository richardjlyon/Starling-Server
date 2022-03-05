from fastapi import FastAPI
from .routes.account import router as AccountRouter

app = FastAPI()
app.include_router(AccountRouter, tags=["Account"], prefix="/accounts")


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}
