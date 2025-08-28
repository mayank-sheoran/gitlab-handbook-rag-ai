from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    k: int = None

class SearchResponse(BaseModel):
    id: str
    content: str
    url: str
    title: str
    index: int
    total: int
    similarity: float
    rank: int