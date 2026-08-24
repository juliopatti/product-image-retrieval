from pydantic import BaseModel, HttpUrl


class ImageCandidate(BaseModel):
    source: str
    source_id: str

    image_url: HttpUrl
    page_url: HttpUrl | None = None

    width: int | None = None
    height: int | None = None
    mime_type: str | None = None

    license: str | None = None
    license_url: HttpUrl | None = None
    author: str | None = None