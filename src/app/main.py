from fastapi import FastAPI

from app.api.v1 import books
from app.core.config import settings
from app.core.db import init_db

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.include_router(books.router, prefix="/books", tags=["books"])


# アプリ起動時に実行されるイベント
@app.on_event("startup")
async def startup_event():
    # データベースのテーブルを作成
    await init_db()
    print("--- Database initialized ---")


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
