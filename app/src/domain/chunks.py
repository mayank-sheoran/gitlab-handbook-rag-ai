from pydantic import BaseModel, HttpUrl
from typing import Optional

class Chunk(BaseModel):
    id: str
    url: HttpUrl
    title: Optional[str]
    content: str
    index: int
    total: int

