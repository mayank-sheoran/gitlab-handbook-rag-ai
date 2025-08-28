from fastapi import FastAPI
from app.src.api.chat_router import router as chat_router
from app.src.api.health_router import router as health_router
from app.src.api.ingest_router import router as ingest_router
import uvicorn

app = FastAPI()

app.include_router(chat_router)
app.include_router(health_router)
app.include_router(ingest_router)

if __name__ == '__main__':
    uvicorn.run("app.main:app", host="0.0.0.0", port=9999, reload=False)
