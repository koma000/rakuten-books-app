from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # アプリの基本情報
    PROJECT_NAME: str = "Rakuten Books App"
    VERSION: str = "0.1.0"

    # データベース接続URL
    DATABASE_URL: str = "sqlite+aiosqlite:///./books.db"

    # 楽天API設定
    # .envファイルから読み込むことを想定しています
    RAKUTEN_APPLICATION_ID: str = ""
    RAKUTEN_ACCESS_KEY: str = ""

    # .envファイルの読み込み設定
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # 定義外の環境変数があっても無視します
    )


# インスタンス化して、他のファイルから使いまわせるようにします
settings = Settings()
