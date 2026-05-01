from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.book import Book
from app.schemas.book import RakutenBookData
from app.services.rakuten import RakutenBookService

router = APIRouter()

db_dependency = Annotated[AsyncSession, Depends(get_db)]


@router.post("/fetch/{isbn}", response_model=RakutenBookData)
async def fetch_and_save_book(
    isbn: str,
    db: db_dependency
):
    service = RakutenBookService()
    book_data = await service.fetch_book_by_isbn(isbn)

    if not book_data:
        raise HTTPException(
            status_code=404,
            detail="Book not found in Rakuten API"
        )

    db_book = Book(
        isbn=book_data.isbn,
        title=book_data.title,
        sales_date=book_data.sales_date,
        cover_url=book_data.cover_url,
        thumbnail_url=book_data.thumbnail_url,
        get_flg=book_data.get_flg,
    )

    db.add(db_book)
    try:
        await db.commit()
        await db.refresh(db_book)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Database error:{str(e)}"
        ) from e

    return book_data
