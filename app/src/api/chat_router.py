from fastapi import APIRouter
from app.src.domain.chat import ChatRequest, ChatResponse
from app.src.services.chat.service import ChatService
router = APIRouter(prefix="/chat", tags=["chat"])
service = ChatService()

@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    return service.chat(req)

