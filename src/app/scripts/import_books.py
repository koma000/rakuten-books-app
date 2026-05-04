import asyncio
import logging
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Annotated

import httpx
from pydantic import Field, ValidationError, validate_call
from tqdm import tqdm

from app.core.config import settings
from app.core.logger import get_logger

# URL
API_URL = "http://127.0.0.1:8000/books/batch"

# 一度に送る件数
BATCH_SIZE = 50

logger = get_logger(__name__, log_file="import.log")


def convert_books_to_isbns(db_path: str) -> list[str]:
    """
    DBから出版者記号などを取得し、ISBN13に変換する
    """
    logger.info("ISBN変換処理を開始します")
    logger.debug(f"読み込み元DB：{db_path}")
    p = Path(db_path)
    if not p.exists():
        logger.error(f"DBファイルが見つかりません:{db_path}")
        return []

    isbns: list[str] = []

    try:
        with closing(sqlite3.connect(db_path)) as conn, conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT pub_code, book_code "
                "FROM comic "
                "WHERE asin IS NULL"
            )
            rows = cursor.fetchall()
            for pub, book in tqdm(rows, desc="Importing"):
                try:
                    if not pub or not book:
                        logger.warning(
                            f"NULL項目があります:pub=[{pub}] book=[{book}]"
                        )
                        continue
                    isbn13 = convert_to_isbn13(pub, book)
                    isbns.append(isbn13)
                except ValidationError as e:
                    # データ形式の不備
                    error_msg = e.errors()[0]["msg"]
                    logger.warning(
                        f"SKIP (Validation): pub={pub}, book={book} | "
                        f"Reason:{error_msg}"
                    )
                except Exception:
                    # 予期せぬエラー
                    logger.error(
                        f"FATAL ERROR: data={pub}-{book}",
                        exc_info=True
                    )
    except sqlite3.OperationalError as e:
        # ロックされている等の運用エラー
        logger.error(f"DB接続エラー:{e}")
    except sqlite3.Error as e:
        # その他のSQLite固有のエラー
        logger.error(f"SQLiteエラー:{e}")
    logger.info("ISBN変換処理を終了しました")
    return isbns


def convert_to_isbn13(pub: str, book: str) -> str:
    """
    ISBN13変換とチェックデジット計算ロジック
    """
    logger.debug(f"出版者記号=[{pub}] 書名記号=[{book}]")
    isbn_base: str = f"9784{pub}{book}".strip().replace("-", "")
    check_digit: str = calculate_check_digit(isbn_base)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"ISBN13=[978-4-{pub}-{book}-{check_digit}]")
    return f"{isbn_base}{check_digit}"


@validate_call
def calculate_check_digit(
    isbn_base: Annotated[str, Field(pattern=r"^\d{12}$")]
) -> str:
    """
    ISBN13のチェックデジットを算出します
    """
    weight_1_sum = sum(int(d) for d in isbn_base[::2])
    weight_3_sum = sum(int(d) for d in isbn_base[1::2])
    total = weight_1_sum + (weight_3_sum * 3)
    return str(-total % 10)


async def fetch_api(isbns: list[str]):
    """
    楽天ブックスAPI連携APIの呼び出し
    """
    logger.info("API呼び出しを開始します")
    isbns_len = len(isbns)
    async with httpx.AsyncClient(timeout=120.0) as client:
        with tqdm(total=isbns_len, desc="Fetch") as pbar:

            for i in range(0, isbns_len, BATCH_SIZE):
                batch = isbns[i:i + BATCH_SIZE]

                try:
                    response = await client.post(
                        API_URL,
                        json={"isbns": batch}
                    )
                    response.raise_for_status()
                    pbar.update(len(batch))
                    await asyncio.sleep(1.0)
                except httpx.HTTPStatusError as e:
                    logger.error(
                        f"APIエラー(Status):{e.response.status_code} at batch {i}"
                    )
                except Exception:
                    logger.error(f"API接続エラー at batch {i}", exc_info=True)
                    continue
    logger.info("API呼び出しを終了しました")


async def main():
    all_isbns = convert_books_to_isbns(settings.SRC_DB_PATH)

    if not all_isbns:
        logger.info("処理対象のISBNがないため、API呼び出しをスキップします")
        return

    await fetch_api(all_isbns)


if __name__ == "__main__":
    asyncio.run(main())
