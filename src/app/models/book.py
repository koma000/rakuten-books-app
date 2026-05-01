from sqlalchemy import Boolean, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Book(Base):
    """
    楽天ブックスから取得した書籍情報を保存するテーブル
    """
    __tablename__ = "books"

    isbn: Mapped[str] = mapped_column(String(13), primary_key=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # 発売日（yyyy/mm/dd）
    sales_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True)
    get_flg: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="0"
    )
