import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RakutenBookData(BaseModel):
    title: str | None = None
    isbn: str
    sales_date: str | None = Field(default=None, alias="salesDate")
    cover_url: str | None = Field(default=None, alias="largeImageUrl")
    thumbnail_url: str | None = Field(default=None, alias="mediumImageUrl")
    get_flg: bool = False

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("isbn")
    @classmethod
    def normalize_isbn(cls, v: str) -> str:
        cleaned = re.sub(r"[- ]", "", v)

        if not re.fullmatch(r"(\d{13})|(\d{9}[\dX])", cleaned):
            raise ValueError(f"ISBNの形式が不正です：{v}")
        return cleaned

    @field_validator("sales_date", mode="before")
    @classmethod
    def format_sales_date(cls, v: str) -> str | None:
        if not v:
            return None

        nums = re.findall(r'\d+', v)

        if len(nums) >= 3:
            return f"{nums[0]}/{nums[1].zfill(2)}/{nums[2].zfill(2)}"
        return v
