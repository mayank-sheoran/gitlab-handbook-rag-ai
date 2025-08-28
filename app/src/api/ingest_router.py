from fastapi import APIRouter, BackgroundTasks
from app.src.services.ingest.pipeline import IngestionPipeline
from app.src.services.store.store import VectorStore
from app.src.utils.logs import logger
router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("")
async def ingest(background_tasks: BackgroundTasks):
    pipeline = IngestionPipeline()
    def run():
        try:
            pipeline.run_sync()
            logger.info("ingestion success")
        except Exception as e:
            logger.error(f"ingestion error err={e}")
    background_tasks.add_task(run)
    return {"status": "ingestion started"}

@router.delete("")
async def ingest_reset():
    vs = VectorStore()
    vs.clear()
    logger.info("ingestion reset")
    return {"status":"reset"}

