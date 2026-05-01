import httpx

from app.core.config import settings
from app.schemas.book import RakutenBookData


class RakutenBookService:
    def __init__(self):
        self.base_url = (
            "https://openapi.rakuten.co.jp/services/api"
            "/BooksBook/Search/20170404"
        )
        self.app_id = settings.RAKUTEN_APPLICATION_ID
        self.access_key = settings.RAKUTEN_ACCESS_KEY

    async def fetch_book_by_isbn(self, isbn: str) -> RakutenBookData | None:
        """
        指定されたISBNを使って楽天APIから書籍情報を取得します。
        """
        params = {
            "applicationId": self.app_id,
            "accessKey": self.access_key,
            "isbn": isbn,
            "format": "json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)

            # APIエラー(400, 500系)が発生した場合は例外を投げます
            response.raise_for_status()

            data = response.json()

            if data.get("count", 0) == 0:
                return None

            item = data["Items"][0]["Item"]
            return RakutenBookData(
                isbn=item["isbn"],
                title=item["title"],
                sales_date=item["salesDate"],
                cover_url=item["largeImageUrl"],
                thumbnail_url=item["mediumImageUrl"],
                get_flg=True,
            )
