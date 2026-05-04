import logging
import sys
from typing import Optional

from app.core.config import settings


def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    アプリケーション共通のロガーを取得する

    Args:
        name: ロガー名（通常は __name__ を渡す）
        log_file: 出力先ファイルパス（任意）
    """
    logger = logging.getLogger(name)

    # 二重登録を防止します
    if logger.handlers:
        return logger

    level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ハンドラの設定（標準出力）
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    # ハンドラの設定（ファイル出力）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
