from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_db
from app.models.book import Book
from app.schemas.book import RakutenBookData
from app.services.rakuten import RakutenBookService

router = APIRouter()

db_dependency = Annotated[AsyncSession, Depends(get_db)]


@router.post("/fetch/{isbn}", response_model=RakutenBookData)
async def fetch_and_save_book(isbn: str, db: db_dependency):
    # DBチェック
    query = select(Book).where(Book.isbn == isbn)
    result = await db.execute(query)
    db_book = result.scalar_one_or_none()

    if db_book:
        # すでにデータがある場合は、APIを叩かずにそのまま返します
        return db_book

    service = RakutenBookService()
    try:
        book_data = await service.fetch_book_by_isbn(isbn)
    except httpx.HTTPStatusError as e:
        error_payload = e.response.json()
        status_code = e.response.status_code
        detail_msg = error_payload.get("error_description", "楽天APIエラー")
        raise HTTPException(status_code=status_code, detail=detail_msg) from e
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="外部サービス接続不可") from e

    db_book = Book(**book_data.model_dump())
    db.add(db_book)
    try:
        await db.commit()
        await db.refresh(db_book)
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Database error:{str(e)}"
        ) from e

    return book_data
