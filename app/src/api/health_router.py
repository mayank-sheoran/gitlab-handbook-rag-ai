from fastapi import APIRouter
from app.src.utils.logs import logger
router = APIRouter(tags=["health"])

@router.get("/health")
async def health():
    logger.debug("health_check")
    return {"status":"ok"}

