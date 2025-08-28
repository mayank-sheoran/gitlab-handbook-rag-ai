from pydantic import BaseModel, HttpUrl
from typing import Optional

class RawPage(BaseModel):
    url: HttpUrl
    depth: int
    html: str
    text: str
    title: Optional[str]
