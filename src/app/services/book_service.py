import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.schemas.book_request import IsbnImportRequest
from app.services.rakuten import RakutenBookService


class BookService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rakuten_api = RakutenBookService()

    async def batch_import_by_isbns(self, request: IsbnImportRequest):
        """
        一括インポートのメインロジック
        """
        # 重複の削除
        unique_isbns = set(request.isbns)

        query = select(Book.isbn).where(Book.isbn.in_(unique_isbns))
        result = await self.db.execute(query)
        exist_isbns = {row[0] for row in result.all()}

        # 検索対象ISBNとDBに存在するISBNの差分を取得します
        target_isbns = unique_isbns - exist_isbns

        stats = {"success": 0, "skipped": len(exist_isbns), "errors": 0}

        for isbn in target_isbns:
            try:
                book_data = await self.rakuten_api.fetch_book_by_isbn(isbn)
                db_book = Book(**book_data.model_dump())

                self.db.add(db_book)
                stats["success"] += 1

                await asyncio.sleep(1.0)
            except Exception as e:
                print(f"Error processing ISBN {isbn}: {e}")
                stats["errors"] += 1
                await asyncio.sleep(5.0)
                continue

        await self.db.commit()
        return stats
