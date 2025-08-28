from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    k: int = None
    chat_history: List[ChatMessage] = []

class Citation(BaseModel):
    id: str
    url: str
    title: Optional[str]
    index: int
    total: int
    snippet: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    rewritten_query: str
