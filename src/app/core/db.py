from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.models.book import Base

# 非同期エンジンの作成
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True
)

# セッションを作る工場の設定
async_session_factory = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)


# テーブルの自動生成関数
async def init_db():
    async with engine.begin() as conn:
        # モデル定義に基づいてテーブルを作成します
        await conn.run_sync(Base.metadata.create_all)


# FastAPIのDependencyで使う「DB接続の配布」関数
async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
