from pydantic import BaseModel, Field


class IsbnImportRequest(BaseModel):
    isbns: list[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="ISBNリスト"
    )
